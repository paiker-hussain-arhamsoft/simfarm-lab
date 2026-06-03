"""SimFarm Security Lab — FastAPI Backend."""

from __future__ import annotations

import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.detection.engine import ANALYSIS_TOOLS
from backend.detection.exercises import get_exercises, validate_flag
from backend.phishing.game import (
    GameState,
    create_game_session,
    get_company_directory,
    get_game_status,
    send_phishing_email,
    submit_final_report,
)
from backend.simulator.beginner import generate_scenario as beginner_scenario
from backend.simulator.easy import generate_scenario as easy_scenario
from backend.simulator.legendary import generate_scenario as legendary_scenario
from backend.simulator.models import Level
from backend.simulator.playground import (
    FarmConfig,
    calculate_farm_metrics,
    get_playground_options,
)
from backend.simulator.uk_demo import (
    build_uk_farm,
    calculate_uk_demo_metrics,
    generate_simulation_events,
    get_uk_demo_scenarios,
    get_uk_playground_options,
)

app = FastAPI(
    title="SimFarm Security Lab",
    description="A cybersecurity training platform for SIM farm detection",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory stores
_scenarios: dict[str, dict] = {}
_game_sessions: dict[str, GameState] = {}


# ── Scenario endpoints ──────────────────────────────────────────────


@app.get("/api/levels")
def list_levels():
    return {
        "levels": [
            {
                "id": "beginner",
                "name": "The Obvious Farm",
                "difficulty": "Beginner",
                "description": "Blatant SIM farm with obvious indicators. Great for learning the basics.",
                "color": "#22c55e",
                "icon": "🟢",
            },
            {
                "id": "easy",
                "name": "The Hidden Network",
                "difficulty": "Easy",
                "description": "Sophisticated farm using VPNs, IMEI rotation, and distributed towers.",
                "color": "#f59e0b",
                "icon": "🟡",
            },
            {
                "id": "legendary",
                "name": "The Ghost Farm",
                "difficulty": "Legendary",
                "description": "99.9% undetectable. Only insider intelligence can expose this operation.",
                "color": "#ef4444",
                "icon": "🔴",
            },
        ]
    }


@app.post("/api/scenario/{level}")
def generate_scenario(level: str):
    """Generate (or retrieve cached) scenario data for a level."""
    if level not in ("beginner", "easy", "legendary"):
        raise HTTPException(status_code=400, detail="Invalid level")

    if level not in _scenarios:
        generators = {
            "beginner": beginner_scenario,
            "easy": easy_scenario,
            "legendary": legendary_scenario,
        }
        _scenarios[level] = generators[level]()

    scenario = _scenarios[level]
    # Return metadata without full data arrays (those are fetched separately)
    return {
        "level": scenario["level"],
        "name": scenario["name"],
        "description": scenario["description"],
        "briefing": scenario["briefing"],
        "farm_sim_count": scenario["farm_sim_count"],
        "legit_sim_count": scenario["legit_sim_count"],
        "total_cdrs": scenario["total_cdrs"],
        "cell_towers": scenario["cell_towers"],
        "sim_count": len(scenario["sim_cards"]),
        "cdr_count": len(scenario["cdrs"]),
    }


@app.get("/api/scenario/{level}/sims")
def get_sims(level: str, page: int = 1, per_page: int = 50):
    if level not in _scenarios:
        raise HTTPException(status_code=404, detail="Generate scenario first")
    sims = _scenarios[level]["sim_cards"]
    start = (page - 1) * per_page
    end = start + per_page
    return {
        "sims": sims[start:end],
        "total": len(sims),
        "page": page,
        "per_page": per_page,
    }


@app.get("/api/scenario/{level}/cdrs")
def get_cdrs(level: str, page: int = 1, per_page: int = 100):
    if level not in _scenarios:
        raise HTTPException(status_code=404, detail="Generate scenario first")
    cdrs = _scenarios[level]["cdrs"]
    start = (page - 1) * per_page
    end = start + per_page
    return {
        "cdrs": cdrs[start:end],
        "total": len(cdrs),
        "page": page,
        "per_page": per_page,
    }


@app.get("/api/scenario/{level}/network-logs")
def get_network_logs(level: str, page: int = 1, per_page: int = 100):
    if level not in _scenarios:
        raise HTTPException(status_code=404, detail="Generate scenario first")
    logs = _scenarios[level]["network_logs"]
    start = (page - 1) * per_page
    end = start + per_page
    return {
        "logs": logs[start:end],
        "total": len(logs),
        "page": page,
        "per_page": per_page,
    }


# ── Detection / Analysis endpoints ─────────────────────────────────


class AnalysisRequest(BaseModel):
    tool: str
    data_type: str = "sim_cards"  # sim_cards or cdrs


@app.post("/api/analyze/{level}")
def run_analysis(level: str, req: AnalysisRequest):
    if level not in _scenarios:
        raise HTTPException(status_code=404, detail="Generate scenario first")

    tool_fn = ANALYSIS_TOOLS.get(req.tool)
    if not tool_fn:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown tool: {req.tool}. Available: {list(ANALYSIS_TOOLS.keys())}",
        )

    scenario = _scenarios[level]
    if req.tool in ("traffic_patterns", "temporal_patterns", "imei_changes"):
        data = scenario["cdrs"]
    else:
        data = scenario["sim_cards"]

    result = tool_fn(data)
    return {"tool": req.tool, "level": level, "result": result}


@app.get("/api/analysis-tools")
def list_analysis_tools():
    return {
        "tools": [
            {"id": "tower_distribution", "name": "Tower Distribution Analysis",
             "description": "Count SIMs per cell tower to spot concentration anomalies.",
             "data_type": "sim_cards"},
            {"id": "imei_patterns", "name": "IMEI Pattern Analysis",
             "description": "Analyze IMEI prefixes and device model distribution.",
             "data_type": "sim_cards"},
            {"id": "activation_dates", "name": "Activation Date Analysis",
             "description": "Identify mass activation events and date clusters.",
             "data_type": "sim_cards"},
            {"id": "ip_distribution", "name": "IP Distribution Analysis",
             "description": "Find shared IPs and VPN exit nodes.",
             "data_type": "sim_cards"},
            {"id": "traffic_patterns", "name": "Traffic Pattern Analysis",
             "description": "Analyze SMS-to-voice ratios per subscriber.",
             "data_type": "cdrs"},
            {"id": "temporal_patterns", "name": "Temporal Pattern Analysis",
             "description": "Detect regular/automated sending intervals.",
             "data_type": "cdrs"},
            {"id": "imei_changes", "name": "IMEI Change Tracking",
             "description": "Track devices that swap IMEI numbers over time.",
             "data_type": "cdrs"},
        ]
    }


# ── Exercise endpoints ──────────────────────────────────────────────


@app.get("/api/exercises/{level}")
def get_level_exercises(level: str):
    try:
        lvl = Level(level)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid level")
    return {"exercises": get_exercises(lvl)}


class FlagSubmission(BaseModel):
    exercise_id: str
    flag: str


@app.post("/api/exercises/submit")
def submit_exercise_flag(submission: FlagSubmission):
    result = validate_flag(submission.exercise_id, submission.flag)
    return result


# ── Phishing Game endpoints (Legendary) ────────────────────────────


@app.post("/api/phishing/new-game")
def new_phishing_game():
    state = create_game_session()
    _game_sessions[state.session_id] = state
    return {
        "session_id": state.session_id,
        "max_attempts": state.max_attempts,
        "company_directory": get_company_directory(),
    }


@app.get("/api/phishing/directory")
def phishing_directory():
    return {"directory": get_company_directory()}


class PhishingEmail(BaseModel):
    session_id: str
    target_email: str
    subject: str
    body: str
    sender_alias: str = "Anonymous Researcher"
    pretext: str = ""


@app.post("/api/phishing/send")
def send_phish(email: PhishingEmail):
    state = _game_sessions.get(email.session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Game session not found")

    result = send_phishing_email(
        state=state,
        target_email=email.target_email,
        subject=email.subject,
        body=email.body,
        sender_alias=email.sender_alias,
        pretext=email.pretext,
    )
    result["game_status"] = get_game_status(state)
    return result


@app.get("/api/phishing/status/{session_id}")
def phishing_status(session_id: str):
    state = _game_sessions.get(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Game session not found")
    return get_game_status(state)


class ReportSubmission(BaseModel):
    session_id: str
    report_text: str


@app.post("/api/phishing/submit-report")
def submit_report(submission: ReportSubmission):
    state = _game_sessions.get(submission.session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Game session not found")
    return submit_final_report(state, submission.report_text)


# ── Playground endpoints (Attack Mode) ─────────────────────────────


@app.get("/api/playground/options")
def playground_options():
    """Return all available configuration options for the playground."""
    return get_playground_options()


class PlaygroundBuildRequest(BaseModel):
    name: str = "My Farm"
    city: str = "karachi"
    carriers: list[str] = ["jazz"]
    acquisition_method: str = "legitimate_cnic"
    num_cnics: int = 1
    hardware: list[dict] = []
    automation_tool: str = "gammu"
    opsec_measures: list[str] = []
    target_sims: int = 10
    purpose: str = "otp_harvesting"
    monthly_budget_pkr: int = 50000


@app.post("/api/playground/build")
def build_farm(req: PlaygroundBuildRequest):
    """Calculate metrics for a SIM farm configuration."""
    config = FarmConfig(
        name=req.name,
        city=req.city,
        carriers=req.carriers,
        acquisition_method=req.acquisition_method,
        num_cnics=req.num_cnics,
        hardware=req.hardware,
        automation_tool=req.automation_tool,
        opsec_measures=req.opsec_measures,
        target_sims=req.target_sims,
        purpose=req.purpose,
        monthly_budget_pkr=req.monthly_budget_pkr,
    )
    return calculate_farm_metrics(config)


# ── UK Demo endpoints (/uk-demo slug) ──────────────────────────────


@app.get("/api/uk-demo/scenarios")
def uk_demo_scenarios():
    """Return available UK demo scenarios and UK telecom context."""
    return get_uk_demo_scenarios()


@app.get("/api/uk-demo/run/{scenario_id}")
def uk_demo_run(scenario_id: str):
    """Calculate full metrics for a UK demo scenario."""
    result = calculate_uk_demo_metrics(scenario_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.get("/api/uk-demo/options")
def uk_demo_options():
    """Return UK playground configuration options (carriers, cities, hardware, etc.)."""
    return get_uk_playground_options()


class UkBuildRequest(BaseModel):
    name: str = "UK Operation"
    city: str = "london"
    carriers: list[str] = ["giffgaff"]
    acquisition_method: str = "payg_walk_in"
    hardware: list[dict] = []
    automation_tool: str = "selenium_browser"
    opsec_measures: list[str] = []
    platforms: list[str] = ["x_twitter", "facebook"]
    target_sims: int = 50


@app.post("/api/uk-demo/build")
def uk_build_farm(req: UkBuildRequest):
    """Calculate metrics for a custom UK SIM farm configuration."""
    return build_uk_farm(req.model_dump())


@app.get("/api/uk-demo/simulate/{scenario_id}")
def uk_simulate(scenario_id: str):
    """Generate 200 simulation events for the live dashboard."""
    events = generate_simulation_events(scenario_id)
    if not events:
        raise HTTPException(status_code=404, detail=f"Unknown scenario: {scenario_id}")
    return {"events": events, "total": len(events)}


# ── Static files (frontend) ────────────────────────────────────────

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

if os.path.isdir(FRONTEND_DIR):
    for subdir in ("assets", "css", "js"):
        sub_path = os.path.join(FRONTEND_DIR, subdir)
        if os.path.isdir(sub_path):
            app.mount(f"/{subdir}", StaticFiles(directory=sub_path), name=subdir)

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    @app.get("/{path:path}")
    def serve_spa(path: str):
        file_path = os.path.join(FRONTEND_DIR, path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
