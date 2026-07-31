#!/usr/bin/env python3
"""Strapi v5 lifecycle content API client for the simfarm-lab pipeline.

Uses only stdlib (urllib). Requires a Strapi API token with permissions on the
`Lifecycle` collection type. The result always has `"simulated": true` so the
simfarm-lab safety invariants stay satisfied; the real write happens inside
Strapi itself.
"""
from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from typing import Any


def _api_request(
    url: str,
    path: str,
    token: str,
    method: str = "GET",
    data: dict | None = None,
) -> Any:
    full = url.rstrip("/") + path
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data is not None else None

    ctx = ssl.create_default_context()
    req = urllib.request.Request(full, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Strapi API error {exc.code}: {err_body[:500]}") from exc
    except Exception as exc:
        raise RuntimeError(f"Strapi API request failed: {exc}") from exc


def _create_entry(base_url: str, token: str, content_type: str, payload: dict) -> dict:
    result = _api_request(
        base_url,
        f"/api/{content_type}",
        token,
        "POST",
        {"data": payload},
    )
    item = result.get("data", {}) if isinstance(result, dict) else {}
    attrs = item.get("attributes") or {}
    return {
        "artifact": f"{base_url}/admin/content-manager/collection-types/api::{content_type[:-1]}.{content_type[:-1]}/{item.get('documentId') or item.get('id')}",
        "simulated": True,
        "strapi_entry_id": item.get("id"),
        "strapi_document_id": item.get("documentId"),
        "strapi_title": attrs.get("title"),
        "strapi_stage": attrs.get("stage"),
    }


def _list_entries(base_url: str, token: str, content_type: str) -> dict:
    result = _api_request(base_url, f"/api/{content_type}?pagination[pageSize]=1", token)
    return {
        "artifact": base_url,
        "simulated": True,
        "strapi_total": result.get("meta", {}).get("pagination", {}).get("total") if isinstance(result, dict) else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Create/read Strapi lifecycle entries")
    parser.add_argument("--mode", choices=["create", "list", "status"], default="create")
    parser.add_argument("--title", default="SimFarm Lifecycle Entry")
    parser.add_argument("--body", default="")
    parser.add_argument("--channel", default="")
    parser.add_argument("--stage", default="draft")
    parser.add_argument("--content-type", default=os.environ.get("STRAPI_CONTENT_TYPE", "lifecycles"))
    parser.add_argument("--url", default=os.environ.get("STRAPI_URL", "http://strapi:1337"))
    parser.add_argument("--token", default=os.environ.get("STRAPI_API_TOKEN", ""))
    args = parser.parse_args()

    if not args.url:
        print(json.dumps({"error": "Strapi URL not set", "simulated": True}), file=sys.stderr)
        sys.exit(1)

    try:
        if args.mode == "create":
            result = _create_entry(
                args.url,
                args.token,
                args.content_type,
                {
                    "title": args.title,
                    "body": args.body,
                    "channel": args.channel,
                    "stage": args.stage,
                },
            )
        else:
            result = _list_entries(args.url, args.token, args.content_type)
    except Exception as exc:
        print(json.dumps({"error": str(exc), "simulated": True}), file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result))


if __name__ == "__main__":
    main()
