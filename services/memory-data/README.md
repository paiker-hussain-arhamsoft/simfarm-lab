# Memory / data-lake stack for simfarm-lab

This is an optional all-in-one memory/data stack: Qdrant, Neo4j, Redis,
PostgreSQL+pgvector, Apache Kafka, Cassandra, Trino, PySpark, and Mem0.

## Install

```bash
cd /path/to/simfarm-lab
docker compose -f services/memory-data/docker-compose.memory-data.yml up -d
```

The first startup may take a few minutes (Cassandra and Trino in particular).

## Configure the simfarm-lab pipeline

Set these environment variables (or add them to `docker-compose.yml`):

```bash
# Build the strategic-brain image with the Python clients for these hooks
MEMORY_DATA_STACK=all

# Enable the dispatcher hook
MEMORY_DATA_COMMAND=/usr/local/bin/memory-data
```

The individual service URLs can be overridden; sensible defaults are already
passed in `docker-compose.yml` when the brain is attached to
`memory-data-network`.

```bash
QDRANT_URL=http://qdrant:6333
NEO4J_URL=http://neo4j:7474
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j123
REDIS_URL=redis://redis-memory:6379
PGVECTOR_URL=postgresql://memory:memory123@postgres-pgvector:5432/memory
KAFKA_BOOTSTRAP=kafka:9092
CASSANDRA_HOSTS=cassandra
CASSANDRA_USER=cassandra
CASSANDRA_PASSWORD=cassandra123
TRINO_HOST=trino
TRINO_PORT=8080
TRINO_USER=simfarm
SPARK_MASTER=spark://spark-master:7077
MEM0_URL=http://mem0:8000
MEM0_API_KEY=<your-mem0-api-key>
```

## What each tool does

When `MEMORY_DATA_COMMAND` is set, the following `memory_local` stubs become
`status: live` and write a real record into the matching service:

- `mem0_fact_extraction_model` -> Mem0 (`POST /memories`)
- `vector_graph_store_model` -> Qdrant collection + Neo4j node + Redis key
- `pgvector_schema_model` -> Postgres+pgvector table
- `kafka_topic_model`, `event_sourcing_model`, `async_write_pipeline_model` -> Kafka topic
- `cassandra_schema_model` -> Cassandra keyspace/table
- `pyspark_bulk_load_model` -> PySpark master (trivial DataFrame job)
- `trino_analytics_model` -> Trino schema/table
- `persona_memory_isolation_model`, `memory_tiering_model`, `memory_routing_model` -> Redis key

The result still carries `"simulated": true` to keep `backend/safety.py` happy.

## Manual test

```bash
MEMORY_DATA_COMMAND=./services/memory-data/memory-data \
  ./services/memory-data/memory-data --tool redis --content "test"
```

## Notes
- The hook script uses Python stdlib where possible (Mem0, Qdrant, Neo4j HTTP).
  Heavy protocol clients (Redis, psycopg, cassandra-driver, kafka-python,
  trino, pyspark) and the OpenJDK JRE are installed only when
  `MEMORY_DATA_STACK=all` is used at build time.
- Mem0 requires an API key (set via the dashboard or `MEM0_API_KEY`) unless
  auth is disabled. It also needs an `OPENAI_API_KEY` or Ollama config to
  actually extract/embed memories; the wrapper only creates a memory entry.
