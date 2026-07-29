"""Offline-first adapter for the isolated TIER 4 simulator."""
from __future__ import annotations

import os
from typing import Any

import httpx

BASE_URL = os.getenv("SIMFARM_SIM_URL", "http://tier4-simfarm-simulator:9000").rstrip("/")
_NOTE = ("SIMULATED lab model only. Real execution would require specific orders from "
         "the communications secretariat and is NOT performed here.")


async def _call(path: str, payload: dict[str, Any], kind: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(f"{BASE_URL}{path}", json=payload)
            response.raise_for_status()
            result = response.json()
    except Exception:
        result = {"model": kind, "fallback": True, **payload, "note": _NOTE}
        if path == "/sms/send":
            result["to"] = "…(lab-sink)"
            result["delivered"] = False
            result["real_recipient"] = False
    if not isinstance(result, dict):
        result = {"model": kind, "value": result}
    result["simulated"] = True
    result["requires_internet"] = False
    result.setdefault("note", _NOTE)
    return result


async def modem_topology(modem_type="", ports=8, hub_layout="modeled"): return await _call("/modem/topology", locals(), "modem-topology")
async def gateway_config(gateway="SMSgate", pool_size=8): return await _call("/gateway/config", locals(), "gateway-config")
async def provision_plan(count=0, carriers=None): return await _call("/provision/plan", {"count": count, "carriers": carriers or []}, "provision-plan")
async def campaign_orchestrate(tasks=None, schedule="modeled"): return await _call("/campaign/orchestrate", {"tasks": tasks or [], "schedule": schedule}, "campaign-orchestration")
async def sim_activate(iccid=""): return await _call("/sim/activate", locals(), "sim-activation")
async def modem_control(command=""): return await _call("/modem/control", locals(), "modem-control")
async def sms_send(to="", body=""): return await _call("/sms/send", locals(), "sms-send")
async def carrier_access(carrier=""): return await _call("/carrier/access", locals(), "carrier-access")
async def celery_dispatch(task=""): return await _call("/celery/dispatch", locals(), "celery-dispatch")
