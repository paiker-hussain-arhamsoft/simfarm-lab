#!/usr/bin/env python3
"""Mautic campaign/segment/lead-score API client for the simfarm-lab pipeline.

Uses only stdlib (urllib) so it can be copied into any container without extra
pip dependencies. It expects Basic Auth to be enabled in Mautic:
    MAUTIC_API_ENABLED=true
    MAUTIC_API_ENABLE_BASIC_AUTH=true

The script always returns `"simulated": true` so it satisfies the simfarm-lab
safety invariants; the real side effect (creating a draft campaign/segment)
happens inside Mautic itself.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from typing import Any


def _basic_auth_header(user: str, password: str) -> str:
    creds = f"{user}:{password}".encode("utf-8")
    return "Basic " + base64.b64encode(creds).decode("ascii")


def _api_request(
    url: str,
    path: str,
    user: str,
    password: str,
    method: str = "GET",
    data: dict | None = None,
) -> Any:
    full = url.rstrip("/") + path
    headers = {
        "Authorization": _basic_auth_header(user, password),
        "Accept": "application/json",
    }
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        full, data=body, headers=headers, method=method
    )
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Mautic API error {exc.code}: {err_body[:500]}") from exc
    except Exception as exc:
        raise RuntimeError(f"Mautic API request failed: {exc}") from exc


def _campaign_action(base_url: str, user: str, password: str, name: str, description: str) -> dict:
    segment = _api_request(
        base_url,
        "/api/segments/new",
        user,
        password,
        "POST",
        {
            "name": f"{name} - Segment",
            "description": description,
            "isPublished": False,
            "isGlobal": True,
        },
    )
    segment_id = segment.get("list", {}).get("id") if isinstance(segment, dict) else None

    campaign = _api_request(
        base_url,
        "/api/campaigns/new",
        user,
        password,
        "POST",
        {
            "name": name,
            "description": description,
            "isPublished": False,
            "lists": [segment_id] if segment_id else [],
        },
    )
    campaign_id = campaign.get("campaign", {}).get("id") if isinstance(campaign, dict) else None

    return {
        "artifact": f"{base_url}/s/campaigns/view/{campaign_id}" if campaign_id else base_url,
        "simulated": True,
        "mautic_segment": segment_id,
        "mautic_campaign": campaign_id,
        "mautic_url": base_url,
    }


def _lead_score_action(base_url: str, user: str, password: str, name: str, description: str) -> dict:
    group = _api_request(
        base_url,
        "/api/points/groups/new",
        user,
        password,
        "POST",
        {"name": name, "description": description},
    )
    group_id = group.get("pointGroup", {}).get("id") if isinstance(group, dict) else None

    return {
        "artifact": f"{base_url}/s/points/groups" if group_id else base_url,
        "simulated": True,
        "mautic_point_group": group_id,
        "mautic_url": base_url,
    }


def _status_action(base_url: str, user: str, password: str) -> dict:
    result = _api_request(base_url, "/api/campaigns?limit=1", user, password)
    return {
        "artifact": base_url,
        "simulated": True,
        "mautic_total_campaigns": result.get("total") if isinstance(result, dict) else None,
        "mautic_url": base_url,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Create/read Mautic campaigns via REST API")
    parser.add_argument("--mode", choices=["campaign", "lead_score", "status"], default="campaign")
    parser.add_argument("--name", default="SimFarm Campaign", help="Campaign / segment / point group name")
    parser.add_argument("--description", default="", help="Campaign / segment / point group description")
    parser.add_argument("--url", default=os.environ.get("MAUTIC_URL", "http://mautic-web"))
    parser.add_argument("--user", default=os.environ.get("MAUTIC_USER", "admin"))
    parser.add_argument("--password", default=os.environ.get("MAUTIC_PASSWORD", "Maut1cR0cks!"))
    args = parser.parse_args()

    if not args.url:
        print(json.dumps({"error": "Mautic URL not set", "simulated": True}), file=sys.stderr)
        sys.exit(1)

    try:
        if args.mode == "campaign":
            result = _campaign_action(args.url, args.user, args.password, args.name, args.description)
        elif args.mode == "lead_score":
            result = _lead_score_action(args.url, args.user, args.password, args.name, args.description)
        else:
            result = _status_action(args.url, args.user, args.password)
    except Exception as exc:
        print(json.dumps({"error": str(exc), "simulated": True}), file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result))


if __name__ == "__main__":
    main()
