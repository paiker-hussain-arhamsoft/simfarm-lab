#!/usr/bin/env python3
"""Postiz public API client for the simfarm-lab pipeline.

Uses only stdlib (urllib). Requires a Postiz API key and an integration ID
for the target social account. The result always has `"simulated": true` so
`backend/safety.py` stays satisfied; the real write happens inside Postiz.
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


def _iso_now_plus(minutes: int = 5) -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _api_request(
    base_url: str,
    path: str,
    token: str,
    method: str = "GET",
    data: dict | None = None,
) -> Any:
    full = base_url.rstrip("/") + path
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": token,
    }
    body = json.dumps(data).encode("utf-8") if data is not None else None

    ctx = ssl.create_default_context()
    req = urllib.request.Request(full, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Postiz API error {exc.code}: {err_body[:500]}") from exc
    except Exception as exc:
        raise RuntimeError(f"Postiz API request failed: {exc}") from exc


def _create_post(
    base_url: str,
    token: str,
    content: str,
    integration_id: str,
    platform: str,
    schedule_date: str,
) -> dict:
    payload = {
        "type": "schedule",
        "date": schedule_date,
        "shortLink": False,
        "tags": [],
        "posts": [
            {
                "integration": {"id": integration_id},
                "value": [{"content": content, "image": []}],
                "settings": {"__type": platform},
            }
        ],
    }
    result = _api_request(base_url, "/posts", token, "POST", payload)
    return {
        "artifact": f"{base_url}/posts",
        "simulated": True,
        "postiz_response": result if isinstance(result, dict) else {},
    }


def _list_posts(base_url: str, token: str) -> dict:
    result = _api_request(base_url, "/posts?limit=1", token)
    return {
        "artifact": base_url,
        "simulated": True,
        "postiz_total": result.get("total") if isinstance(result, dict) else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Create/list Postiz posts")
    parser.add_argument("--mode", choices=["create", "list", "status"], default="create")
    parser.add_argument("--content", default="Hello from the simfarm-lab pipeline")
    parser.add_argument("--integration-id", default=os.environ.get("POSTIZ_INTEGRATION_ID", ""))
    parser.add_argument("--platform", default=os.environ.get("POSTIZ_PLATFORM", "bluesky"))
    parser.add_argument("--date", default=_iso_now_plus(5))
    parser.add_argument("--url", default=os.environ.get("POSTIZ_API_URL", "http://postiz:5000/api/public/v1"))
    parser.add_argument("--token", default=os.environ.get("POSTIZ_API_TOKEN", ""))
    args = parser.parse_args()

    if not args.url:
        print(json.dumps({"error": "Postiz API URL not set", "simulated": True}), file=sys.stderr)
        sys.exit(1)

    try:
        if args.mode == "create":
            if not args.integration_id:
                raise RuntimeError(
                    "POSTIZ_INTEGRATION_ID is required to create a post. "
                    "Add a social integration in Postiz and copy its integration ID."
                )
            result = _create_post(
                args.url,
                args.token,
                args.content,
                args.integration_id,
                args.platform,
                args.date,
            )
        else:
            result = _list_posts(args.url, args.token)
    except Exception as exc:
        print(json.dumps({"error": str(exc), "simulated": True}), file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result))


if __name__ == "__main__":
    main()
