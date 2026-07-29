"""Internal-only deterministic SIM-farm/GSM-gateway simulator."""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI

app = FastAPI(title="TIER 4 SIM Farm Simulator")
_NOTE = ("SIMULATED lab model only. Real execution would require specific orders "
         "from the communications secretariat and is NOT performed here.")


def _result(kind: str, **data: Any) -> dict:
    return {"simulated": True, "requires_internet": False, "model": kind, **data, "note": _NOTE}


@app.get("/health")
def health() -> dict:
    return {"ok": True, "simulated": True, "requires_internet": False, "note": _NOTE}


@app.post("/modem/topology")
def modem_topology(params: dict) -> dict:
    return _result("modem-topology", modem_type=params.get("modem_type", "SIM800C"),
                   ports=params.get("ports", 8), hub_layout=params.get("hub_layout", "modeled"),
                   modem_pool={"family": "SIM800/SIM900", "ports": params.get("ports", 8)},
                   usb_hub={"layout": params.get("hub_layout", "modeled"), "physical": False},
                   gammu_config={"device": "lab-virtual-modem", "connection": "simulated"})


@app.post("/gateway/config")
def gateway_config(params: dict) -> dict:
    return _result("gateway-config", gateway=params.get("gateway", "SMSgate"),
                   pool_size=params.get("pool_size", 8),
                   gateway_config={"gateway": "SMSgate", "adapter": "Gammu", "delivery": "modeled"},
                   modem_pool={"size": params.get("pool_size", 8), "physical": False})


@app.post("/provision/plan")
def provision_plan(params: dict) -> dict:
    count = int(params.get("count", 0) or 0)
    return _result("provision-plan", count=count, carriers=params.get("carriers", []),
                   provisioning={"numbers": [f"sim-number-{i:04d}(lab)" for i in range(min(count, 10))],
                                 "real_numbers": False},
                   carrier_rotation="modeled round-robin",
                   burnout_management="risk thresholds and retirement model only")


@app.post("/campaign/orchestrate")
def campaign_orchestrate(params: dict) -> dict:
    return _result("campaign-orchestration", tasks=params.get("tasks", []),
                   schedule=params.get("schedule", "modeled"),
                   celery={"queue": "simulated-infrastructure", "workers": 0, "executed": False},
                   delivery_tracking={"status": "modeled", "real_delivery": False})


@app.post("/sim/activate")
def sim_activate(params: dict) -> dict:
    iccid = str(params.get("iccid", "unknown"))
    return _result("sim-activation", iccid=f"sim-{iccid}(lab)",
                   status="activated (simulated)", real_sim=False)


@app.post("/modem/control")
def modem_control(params: dict) -> dict:
    return _result("modem-control", command=params.get("command", ""),
                   acknowledgement="acknowledged (simulated)", hardware_touched=False)


@app.post("/sms/send")
def sms_send(params: dict) -> dict:
    return _result("sms-send", to="…(lab-sink)", body=params.get("body", ""),
                   status="queued (simulated)", delivered=False, real_recipient=False)


@app.post("/carrier/access")
def carrier_access(params: dict) -> dict:
    return _result("carrier-access", carrier=params.get("carrier", ""),
                   handshake="conceptual (simulated)", api_contacted=False)


@app.post("/celery/dispatch")
def celery_dispatch(params: dict) -> dict:
    return _result("celery-dispatch", task=params.get("task", ""),
                   dispatch="recorded (simulated)", worker_contacted=False)
