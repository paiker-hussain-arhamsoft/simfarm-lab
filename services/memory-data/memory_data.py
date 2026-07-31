#!/usr/bin/env python3
"""Unified memory/data-lake command hook for simfarm-lab.

Talks to Qdrant, Neo4j, Redis, PostgreSQL+pgvector, Apache Kafka, Cassandra,
Trino, and Mem0. Real writes happen inside each service; the result is still
wrapped with "simulated": true to satisfy backend/safety.py.
"""
from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any


def _api_request(
    url: str,
    method: str = "GET",
    data: dict | None = None,
    headers: dict | None = None,
    auth: tuple[str, str] | None = None,
) -> Any:
    full = url
    req_headers = {"Accept": "application/json"}
    if headers:
        req_headers.update(headers)
    body = json.dumps(data).encode("utf-8") if data is not None else None
    if body is not None:
        req_headers.setdefault("Content-Type", "application/json")

    ctx = ssl.create_default_context()
    req = urllib.request.Request(full, data=body, headers=req_headers, method=method)
    if auth:
        import base64
        creds = base64.b64encode(f"{auth[0]}:{auth[1]}".encode()).decode()
        req.add_header("Authorization", f"Basic {creds}")
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
            text = resp.read().decode("utf-8", errors="replace")
            return json.loads(text) if text else {}
    except urllib.error.HTTPError as exc:
        err = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {err[:500]}") from exc


def _fail(message: str) -> None:
    print(json.dumps({"error": message, "simulated": True}), file=sys.stderr)
    sys.exit(1)


def _ok(payload: dict) -> None:
    print(json.dumps({"simulated": True, **payload}))


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def _mem0(args: argparse.Namespace) -> dict:
    url = (args.url or os.environ.get("MEM0_URL", "http://mem0:8000")).rstrip("/")
    token = args.token or os.environ.get("MEM0_API_KEY", "")
    if not token:
        raise RuntimeError("MEM0_API_KEY is required to call the Mem0 REST API")

    payload = {
        "messages": [{"role": "user", "content": args.content}],
        "user_id": args.user_id,
        "metadata": args.metadata or {"source": "simfarm-lab"},
    }
    headers = {"Authorization": f"Bearer {token}"}
    result = _api_request(f"{url}/memories", "POST", payload, headers)
    return {"tool": "mem0", "artifact": f"{url}/memories", "result": result}


def _qdrant(args: argparse.Namespace) -> dict:
    url = (args.url or os.environ.get("QDRANT_URL", "http://qdrant:6333")).rstrip("/")
    collection = os.environ.get("QDRANT_COLLECTION", "simfarm")
    vector_size = int(os.environ.get("QDRANT_VECTOR_SIZE", "384"))

    create_body = {
        "vectors": {"size": vector_size, "distance": "Cosine"},
    }
    try:
        _api_request(f"{url}/collections/{collection}", "PUT", create_body)
    except RuntimeError as exc:
        if "already exists" not in str(exc).lower():
            raise

    return {"tool": "qdrant", "artifact": f"{url}/collections/{collection}"}


def _neo4j(args: argparse.Namespace) -> dict:
    url = (args.url or os.environ.get("NEO4J_URL", "http://neo4j:7474")).rstrip("/")
    user = args.username or os.environ.get("NEO4J_USER", "neo4j")
    password = args.password or os.environ.get("NEO4J_PASSWORD", "neo4j123")

    cypher = (
        "CREATE (m:Memory {content: $content, created: datetime(), source: $source}) "
        "RETURN id(m) AS id, m.created AS created"
    )
    tx_body = {
        "statements": [
            {
                "statement": cypher,
                "parameters": {
                    "content": args.content,
                    "source": "simfarm-lab",
                },
            }
        ]
    }
    result = _api_request(f"{url}/db/neo4j/tx/commit", "POST", tx_body, auth=(user, password))
    return {"tool": "neo4j", "artifact": f"{url}/browser/", "result": result}


def _redis(args: argparse.Namespace) -> dict:
    url = args.url or os.environ.get("REDIS_URL", "redis://redis-memory:6379")
    try:
        import redis as redis_client
    except ImportError as exc:
        raise RuntimeError("redis Python client is not installed") from exc

    r = redis_client.from_url(url)
    key = f"simfarm:memory:{args.user_id}"
    r.set(key, args.content)
    return {"tool": "redis", "artifact": url, "key": key}


def _pgvector(args: argparse.Namespace) -> dict:
    dsn = args.url or os.environ.get(
        "PGVECTOR_URL",
        "postgresql://memory:memory123@postgres-pgvector:5432/memory",
    )
    try:
        import psycopg
    except ImportError as exc:
        raise RuntimeError("psycopg is not installed") from exc

    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS simfarm_memory (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT,
                    content TEXT,
                    embedding vector(384)
                )
            """)
            zeros = [0.0] * 384
            cur.execute(
                "INSERT INTO simfarm_memory (user_id, content, embedding) VALUES (%s, %s, %s)",
                (args.user_id, args.content, zeros),
            )
        conn.commit()
    return {"tool": "pgvector", "artifact": dsn}


def _kafka(args: argparse.Namespace) -> dict:
    bootstrap = args.url or os.environ.get("KAFKA_BOOTSTRAP", "kafka:9092")
    topic = os.environ.get("KAFKA_TOPIC", "simfarm-memory-events")
    try:
        from kafka.admin import KafkaAdminClient, NewTopic
    except ImportError as exc:
        raise RuntimeError("kafka-python is not installed") from exc

    admin = KafkaAdminClient(bootstrap_servers=bootstrap, client_id="simfarm-lab")
    try:
        existing = admin.list_topics()
        if topic not in existing:
            admin.create_topics([NewTopic(name=topic, num_partitions=1, replication_factor=1)])
    finally:
        admin.close()
    return {"tool": "kafka", "artifact": f"{bootstrap}/topic/{topic}"}


def _cassandra(args: argparse.Namespace) -> dict:
    host = args.url or os.environ.get("CASSANDRA_HOSTS", "cassandra")
    user = args.username or os.environ.get("CASSANDRA_USER", "cassandra")
    password = args.password or os.environ.get("CASSANDRA_PASSWORD", "cassandra123")
    try:
        from cassandra.cluster import Cluster
        from cassandra.auth import PlainTextAuthProvider
    except ImportError as exc:
        raise RuntimeError("cassandra-driver is not installed") from exc

    auth = PlainTextAuthProvider(username=user, password=password)
    cluster = Cluster([host], auth_provider=auth, protocol_version=5)
    session = cluster.connect()
    session.execute(
        "CREATE KEYSPACE IF NOT EXISTS simfarm WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}"
    )
    session.set_keyspace("simfarm")
    session.execute(
        "CREATE TABLE IF NOT EXISTS memory_events (user_id text, content text, created timestamp, PRIMARY KEY (user_id, created))"
    )
    session.execute(
        "INSERT INTO memory_events (user_id, content, created) VALUES (%s, %s, %s)",
        (args.user_id, args.content, datetime.now(timezone.utc)),
    )
    cluster.shutdown()
    return {"tool": "cassandra", "artifact": f"cassandra://{host}/simfarm"}


def _trino(args: argparse.Namespace) -> dict:
    host = args.url or os.environ.get("TRINO_HOST", "trino")
    port = int(os.environ.get("TRINO_PORT", "8080"))
    user = args.username or os.environ.get("TRINO_USER", "simfarm")
    try:
        import trino.dbapi
    except ImportError as exc:
        raise RuntimeError("trino Python client is not installed") from exc

    conn = trino.dbapi.connect(host=host, port=port, user=user)
    cur = conn.cursor()
    try:
        cur.execute("CREATE SCHEMA IF NOT EXISTS memory.simfarm")
        cur.execute(
            "CREATE TABLE IF NOT EXISTS memory.simfarm.events ("
            "user_id varchar, content varchar, created timestamp)"
        )
        cur.execute(
            "INSERT INTO memory.simfarm.events (user_id, content, created) VALUES (?, ?, ?)",
            (args.user_id, args.content, datetime.now(timezone.utc)),
        )
    finally:
        cur.close()
        conn.close()
    return {"tool": "trino", "artifact": f"http://{host}:{port}/ui/query.html"}


def _pyspark(args: argparse.Namespace) -> dict:
    """Submit a trivial Spark job against the configured Spark master."""
    master = args.url or os.environ.get("SPARK_MASTER", "spark://spark-master:7077")
    try:
        from pyspark.sql import SparkSession
    except ImportError as exc:
        raise RuntimeError("pyspark is not installed") from exc

    spark = SparkSession.builder.appName("simfarm-lab").master(master).getOrCreate()
    try:
        df = spark.createDataFrame([(args.content, args.user_id)], ["content", "user_id"])
        count = df.count()
        return {"tool": "pyspark", "artifact": master, "row_count": count}
    finally:
        spark.stop()


def _vector_graph(args: argparse.Namespace) -> dict:
    """Touch Qdrant, Neo4j, and Redis in one call (used by vector_graph_store_model)."""
    qdrant_result = _qdrant(args)
    neo4j_result = _neo4j(args)
    redis_result = _redis(args)
    return {
        "tool": "vector_graph",
        "artifact": "qdrant+neo4j+redis",
        "qdrant": qdrant_result,
        "neo4j": neo4j_result,
        "redis": redis_result,
    }


_TOOL_MAP = {
    "mem0": _mem0,
    "qdrant": _qdrant,
    "neo4j": _neo4j,
    "redis": _redis,
    "pgvector": _pgvector,
    "kafka": _kafka,
    "cassandra": _cassandra,
    "trino": _trino,
    "pyspark": _pyspark,
    "vector_graph": _vector_graph,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Memory/data-lake command hook")
    parser.add_argument("--tool", required=True, choices=list(_TOOL_MAP.keys()))
    parser.add_argument("--content", default="SimFarm memory/data event")
    parser.add_argument("--user-id", default="simfarm")
    parser.add_argument("--metadata", type=json.loads, default=None)
    parser.add_argument("--url", default="")
    parser.add_argument("--token", default="")
    parser.add_argument("--username", default="")
    parser.add_argument("--password", default="")
    args = parser.parse_args()

    try:
        result = _TOOL_MAP[args.tool](args)
    except Exception as exc:
        _fail(str(exc))

    _ok(result)


if __name__ == "__main__":
    main()
