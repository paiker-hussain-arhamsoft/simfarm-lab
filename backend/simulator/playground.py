"""Playground — Build a SIM farm from scratch in a Pakistani telecom ecosystem.

Students configure every aspect of a SIM farm:
- Choose carrier(s): Jazz, Zong, Telenor, Ufone, SCOM
- Acquire SIMs (CNIC registration, biometric bypass methods)
- Select hardware (GSM modems, SIM banks, SIM boxes, OTG dongles)
- Set up infrastructure (SMS gateway, SMPP server, VPN, proxy rotation)
- Configure automation (bulk SMS scripts, OTP harvesting, account creation)
- Choose operational security measures (IMEI rotation, tower hopping, traffic shaping)
- Deploy and see how detectable the farm is

Pakistani telecom specifics:
- PTA (Pakistan Telecommunication Authority) oversight
- CNIC (Computerized National Identity Card) required for SIM registration
- Biometric verification at franchise/retailer
- Per-CNIC SIM limit (currently 5 per carrier, max 20 total across all carriers)
- DIRBS (Device Identification, Registration & Blocking System)
- PTA device registration (IMEI whitelist)
"""

from __future__ import annotations

import hashlib
import math
import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


# ── Pakistani Telecom Constants ─────────────────────────────────────

CARRIERS = {
    "jazz": {
        "name": "Jazz (Mobilink + Warid)",
        "mcc_mnc": "410-01",
        "msisdn_prefix": ["+9230", "+9231"],
        "market_share": 0.38,
        "sim_cost_pkr": 100,
        "sms_rate_pkr": 1.5,
        "data_rate_pkr_per_gb": 150,
        "franchise_density": "high",
        "biometric_strictness": 0.7,
        "description": "Largest carrier. Wide franchise network. Moderate biometric enforcement.",
    },
    "zong": {
        "name": "Zong (CMPak)",
        "mcc_mnc": "410-04",
        "msisdn_prefix": ["+9231"],
        "market_share": 0.22,
        "sim_cost_pkr": 120,
        "sms_rate_pkr": 1.2,
        "data_rate_pkr_per_gb": 120,
        "franchise_density": "medium",
        "biometric_strictness": 0.75,
        "description": "Chinese-backed. Strong 4G. Slightly stricter biometric checks.",
    },
    "telenor": {
        "name": "Telenor Pakistan",
        "mcc_mnc": "410-06",
        "msisdn_prefix": ["+9234", "+9232"],
        "market_share": 0.20,
        "sim_cost_pkr": 80,
        "sms_rate_pkr": 1.0,
        "data_rate_pkr_per_gb": 100,
        "franchise_density": "high",
        "biometric_strictness": 0.65,
        "description": "Budget-friendly. Dense rural coverage. Less strict enforcement in rural areas.",
    },
    "ufone": {
        "name": "Ufone (PTCL)",
        "mcc_mnc": "410-03",
        "msisdn_prefix": ["+9233"],
        "market_share": 0.15,
        "sim_cost_pkr": 90,
        "sms_rate_pkr": 1.3,
        "data_rate_pkr_per_gb": 130,
        "franchise_density": "medium",
        "biometric_strictness": 0.6,
        "description": "PTCL subsidiary. Moderate network. Lower enforcement at some outlets.",
    },
    "scom": {
        "name": "SCOM (Special Communications Organization)",
        "mcc_mnc": "410-05",
        "msisdn_prefix": ["+9235"],
        "market_share": 0.05,
        "sim_cost_pkr": 150,
        "sms_rate_pkr": 2.0,
        "data_rate_pkr_per_gb": 200,
        "franchise_density": "low",
        "biometric_strictness": 0.5,
        "description": "Military-operated. Covers AJK and GB. Limited availability, lax enforcement.",
    },
}

CITIES = {
    "karachi": {"name": "Karachi", "province": "Sindh", "population": 16_000_000, "towers": 850, "risk_level": "high"},
    "lahore": {"name": "Lahore", "province": "Punjab", "population": 13_000_000, "towers": 720, "risk_level": "high"},
    "islamabad": {"name": "Islamabad", "province": "ICT", "population": 1_200_000, "towers": 320, "risk_level": "very_high"},
    "rawalpindi": {"name": "Rawalpindi", "province": "Punjab", "population": 2_200_000, "towers": 280, "risk_level": "high"},
    "faisalabad": {"name": "Faisalabad", "province": "Punjab", "population": 3_200_000, "towers": 250, "risk_level": "medium"},
    "peshawar": {"name": "Peshawar", "province": "KPK", "population": 2_000_000, "towers": 200, "risk_level": "medium"},
    "quetta": {"name": "Quetta", "province": "Balochistan", "population": 1_000_000, "towers": 120, "risk_level": "low"},
    "multan": {"name": "Multan", "province": "Punjab", "population": 1_900_000, "towers": 180, "risk_level": "medium"},
    "hyderabad": {"name": "Hyderabad", "province": "Sindh", "population": 1_700_000, "towers": 160, "risk_level": "medium"},
    "sialkot": {"name": "Sialkot", "province": "Punjab", "population": 700_000, "towers": 90, "risk_level": "low"},
}

HARDWARE_OPTIONS = {
    "gsm_modem_single": {
        "name": "Single-Port GSM Modem (Huawei E173)",
        "type": "modem",
        "sim_capacity": 1,
        "cost_pkr": 3500,
        "throughput_sms_per_hour": 120,
        "detectability": 0.3,
        "description": "Basic USB modem. One SIM per device. Low throughput but very cheap.",
    },
    "gsm_modem_8port": {
        "name": "8-Port GSM Modem Pool (SIMCom 800C)",
        "type": "modem_pool",
        "sim_capacity": 8,
        "cost_pkr": 25000,
        "throughput_sms_per_hour": 960,
        "detectability": 0.5,
        "description": "8 SIM slots in one device. Good price/performance. Common in SIM farms.",
    },
    "gsm_modem_16port": {
        "name": "16-Port GSM Gateway (OpenVox VS-GW1600)",
        "type": "gateway",
        "sim_capacity": 16,
        "cost_pkr": 75000,
        "throughput_sms_per_hour": 1920,
        "detectability": 0.6,
        "description": "Enterprise-grade. High throughput. Generates noticeable network patterns.",
    },
    "sim_bank_128": {
        "name": "128-Slot SIM Bank (SMB128)",
        "type": "sim_bank",
        "sim_capacity": 128,
        "cost_pkr": 180000,
        "throughput_sms_per_hour": 5000,
        "detectability": 0.7,
        "description": "Remote SIM management. Rotate SIMs across modems. Professional-grade.",
    },
    "sim_box_32": {
        "name": "32-Channel SIM Box (Hybertone GoIP32)",
        "type": "sim_box",
        "sim_capacity": 32,
        "cost_pkr": 120000,
        "throughput_sms_per_hour": 3840,
        "detectability": 0.65,
        "description": "VoIP + SIM. Used for call termination fraud. High throughput.",
    },
    "android_farm": {
        "name": "Android Phone Farm (10x Redmi 9A)",
        "type": "phone_farm",
        "sim_capacity": 10,
        "cost_pkr": 150000,
        "throughput_sms_per_hour": 600,
        "detectability": 0.2,
        "description": "Real phones with unique IMEIs. Hardest to detect. Expensive to scale.",
    },
    "otg_dongle_array": {
        "name": "OTG Dongle Array (USB Hub + 5 dongles)",
        "type": "otg",
        "sim_capacity": 5,
        "cost_pkr": 8000,
        "throughput_sms_per_hour": 300,
        "detectability": 0.25,
        "description": "Budget phone farm alternative. Connect SIM dongles to a single Android.",
    },
}

SIM_ACQUISITION_METHODS = {
    "legitimate_cnic": {
        "name": "Legitimate CNIC Registration",
        "description": "Register SIMs using your own CNIC at authorized franchises.",
        "sims_per_cnic": 5,
        "cost_multiplier": 1.0,
        "risk_level": "low",
        "detection_risk": 0.1,
        "pta_flag_probability": 0.05,
        "notes": "Limited to 5 SIMs per carrier (PTA regulation). Paper trail exists.",
    },
    "recruited_cnics": {
        "name": "Recruited CNIC Holders",
        "description": "Pay individuals (students, laborers) to register SIMs on their CNICs.",
        "sims_per_cnic": 5,
        "cost_multiplier": 2.5,
        "risk_level": "medium",
        "detection_risk": 0.3,
        "pta_flag_probability": 0.15,
        "notes": "Each recruit can register 5 per carrier. Need to recruit many people. Recruits may talk.",
    },
    "stolen_cnics": {
        "name": "Stolen/Forged CNIC Data",
        "description": "Use stolen CNIC numbers with forged biometric data or bribed franchise agents.",
        "sims_per_cnic": 5,
        "cost_multiplier": 4.0,
        "risk_level": "high",
        "detection_risk": 0.6,
        "pta_flag_probability": 0.4,
        "notes": "Illegal. PTA audits can cross-reference NADRA biometric database. High criminal risk.",
    },
    "corporate_bulk": {
        "name": "Corporate/Enterprise Bulk Order",
        "description": "Register a fake company and order bulk SIMs under corporate account.",
        "sims_per_cnic": 100,
        "cost_multiplier": 1.5,
        "risk_level": "medium",
        "detection_risk": 0.35,
        "pta_flag_probability": 0.25,
        "notes": "Requires NTN, company registration documents. PTA reviews bulk activations.",
    },
    "grey_market": {
        "name": "Grey Market Pre-Activated SIMs",
        "description": "Buy pre-activated SIMs from grey market dealers (Saddar, Hall Road, etc.).",
        "sims_per_cnic": 1,
        "cost_multiplier": 3.0,
        "risk_level": "high",
        "detection_risk": 0.5,
        "pta_flag_probability": 0.35,
        "notes": "SIMs already registered on random CNICs. No biometric. PTA crackdowns frequent.",
    },
}

OPSEC_MEASURES = {
    "imei_rotation": {
        "name": "IMEI Rotation",
        "description": "Change device IMEI periodically to avoid DIRBS fingerprinting.",
        "effectiveness": 0.7,
        "cost_pkr": 0,
        "complexity": "medium",
        "dirbs_bypass": True,
        "notes": "DIRBS tracks IMEI-SIM pairings. Rotation breaks the fingerprint chain.",
    },
    "tower_hopping": {
        "name": "Cell Tower Hopping",
        "description": "Distribute SIMs across multiple towers / move equipment periodically.",
        "effectiveness": 0.6,
        "cost_pkr": 5000,
        "complexity": "medium",
        "dirbs_bypass": False,
        "notes": "Prevents tower-level clustering detection. Requires mobile setup or multiple locations.",
    },
    "traffic_shaping": {
        "name": "Traffic Shaping / Humanization",
        "description": "Add random delays, vary message patterns, mix SMS with voice/data.",
        "effectiveness": 0.8,
        "cost_pkr": 0,
        "complexity": "high",
        "dirbs_bypass": False,
        "notes": "Most effective single measure. Makes traffic indistinguishable from real users.",
    },
    "vpn_rotation": {
        "name": "VPN / Proxy Rotation",
        "description": "Route data traffic through rotating VPN endpoints.",
        "effectiveness": 0.5,
        "cost_pkr": 3000,
        "complexity": "low",
        "dirbs_bypass": False,
        "notes": "Prevents IP-based clustering. Less relevant for SMS (which goes over GSM).",
    },
    "multi_location": {
        "name": "Multi-Location Deployment",
        "description": "Split farm across 3+ physical locations in different cities.",
        "effectiveness": 0.75,
        "cost_pkr": 50000,
        "complexity": "high",
        "dirbs_bypass": False,
        "notes": "Dramatically reduces risk. Each location looks like a small operation.",
    },
    "sim_sleeping": {
        "name": "SIM Sleeping / Rotation Schedule",
        "description": "Only activate a subset of SIMs at any time. Rest 'sleep' to mimic normal usage.",
        "effectiveness": 0.65,
        "cost_pkr": 0,
        "complexity": "medium",
        "dirbs_bypass": False,
        "notes": "Reduces per-SIM traffic volume. PTA monitors always-on SIMs.",
    },
    "registered_imei": {
        "name": "DIRBS-Registered Devices",
        "description": "Use only PTA-registered (whitelisted) devices/IMEIs.",
        "effectiveness": 0.4,
        "cost_pkr": 10000,
        "complexity": "low",
        "dirbs_bypass": True,
        "notes": "Avoids DIRBS blocks but doesn't hide traffic patterns.",
    },
}

AUTOMATION_TOOLS = {
    "gammu": {
        "name": "Gammu SMS Daemon",
        "description": "Open-source SMS gateway. Supports multiple modems. Scriptable.",
        "throughput": "medium",
        "complexity": "medium",
        "cost_pkr": 0,
    },
    "kannel": {
        "name": "Kannel WAP/SMS Gateway",
        "description": "Enterprise SMPP gateway. High throughput. REST API.",
        "throughput": "high",
        "complexity": "high",
        "cost_pkr": 0,
    },
    "custom_python": {
        "name": "Custom Python + AT Commands",
        "description": "Direct AT command control over serial. Full flexibility.",
        "throughput": "medium",
        "complexity": "high",
        "cost_pkr": 0,
    },
    "sms_caster": {
        "name": "SMSCaster (Commercial)",
        "description": "Windows-based bulk SMS tool. GUI. Supports modem pools.",
        "throughput": "medium",
        "complexity": "low",
        "cost_pkr": 15000,
    },
    "android_adb": {
        "name": "ADB Automation (Phone Farm)",
        "description": "Android Debug Bridge scripts to automate phones. App interaction.",
        "throughput": "low",
        "complexity": "high",
        "cost_pkr": 0,
    },
}


@dataclass
class FarmConfig:
    """Student's SIM farm configuration."""
    farm_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "My Farm"
    city: str = "karachi"
    carriers: list[str] = field(default_factory=lambda: ["jazz"])
    acquisition_method: str = "legitimate_cnic"
    num_cnics: int = 1
    hardware: list[dict] = field(default_factory=list)
    automation_tool: str = "gammu"
    opsec_measures: list[str] = field(default_factory=list)
    target_sims: int = 10
    purpose: str = "otp_harvesting"
    monthly_budget_pkr: int = 50000


def calculate_farm_metrics(config: FarmConfig) -> dict:
    """Calculate the farm's operational metrics and detection risk."""

    # SIM capacity from hardware
    total_sim_slots = 0
    total_hardware_cost = 0
    total_throughput = 0
    max_detectability = 0.0

    for hw_entry in config.hardware:
        hw_id = hw_entry.get("id", "")
        qty = hw_entry.get("quantity", 1)
        hw = HARDWARE_OPTIONS.get(hw_id)
        if hw:
            total_sim_slots += hw["sim_capacity"] * qty
            total_hardware_cost += hw["cost_pkr"] * qty
            total_throughput += hw["throughput_sms_per_hour"] * qty
            max_detectability = max(max_detectability, hw["detectability"])

    # SIM acquisition
    acq = SIM_ACQUISITION_METHODS.get(config.acquisition_method, SIM_ACQUISITION_METHODS["legitimate_cnic"])
    sims_per_cnic = acq["sims_per_cnic"]
    max_sims = config.num_cnics * sims_per_cnic * len(config.carriers)
    actual_sims = min(config.target_sims, max_sims, total_sim_slots)

    sim_cost_per_unit = sum(
        CARRIERS[c]["sim_cost_pkr"] for c in config.carriers
    ) / max(len(config.carriers), 1)
    total_sim_cost = actual_sims * sim_cost_per_unit * acq["cost_multiplier"]

    # OPSEC effectiveness
    opsec_score = 0.0
    opsec_cost = 0
    for measure_id in config.opsec_measures:
        measure = OPSEC_MEASURES.get(measure_id)
        if measure:
            opsec_score = max(opsec_score, measure["effectiveness"])
            opsec_cost += measure["cost_pkr"]

    # Detection risk calculation
    base_detection = acq["detection_risk"]
    hw_detection = max_detectability
    volume_factor = min(actual_sims / 500, 1.0)  # more SIMs = more detectable
    city_data = CITIES.get(config.city, CITIES["karachi"])
    city_risk_multiplier = {
        "very_high": 1.5, "high": 1.2, "medium": 1.0, "low": 0.7
    }.get(city_data["risk_level"], 1.0)

    raw_detection = (base_detection * 0.3 + hw_detection * 0.3 + volume_factor * 0.4) * city_risk_multiplier
    final_detection = max(0.01, raw_detection * (1 - opsec_score * 0.6))
    final_detection = min(final_detection, 0.99)

    # PTA flag probability
    pta_flag = acq["pta_flag_probability"] * city_risk_multiplier
    pta_flag = max(0.01, pta_flag * (1 - opsec_score * 0.4))

    # Monthly operating cost
    avg_sms_rate = sum(
        CARRIERS[c]["sms_rate_pkr"] for c in config.carriers
    ) / max(len(config.carriers), 1)
    monthly_sms_cost = total_throughput * 24 * 30 * avg_sms_rate * 0.1  # 10% utilization
    automation = AUTOMATION_TOOLS.get(config.automation_tool, {})
    automation_cost = automation.get("cost_pkr", 0)

    total_setup_cost = total_hardware_cost + total_sim_cost + opsec_cost + automation_cost
    monthly_cost = monthly_sms_cost + (opsec_cost * 0.1)  # recurring opsec costs

    # Detection timeline estimate
    if final_detection > 0.7:
        detection_timeline = "1-2 weeks"
    elif final_detection > 0.5:
        detection_timeline = "1-3 months"
    elif final_detection > 0.3:
        detection_timeline = "3-6 months"
    elif final_detection > 0.15:
        detection_timeline = "6-12 months"
    else:
        detection_timeline = "12+ months (very hard to detect)"

    # Stealth grade
    if final_detection <= 0.1:
        stealth_grade = "S"
        stealth_label = "Ghost — Nearly Undetectable"
    elif final_detection <= 0.2:
        stealth_grade = "A"
        stealth_label = "Shadow — Very Hard to Detect"
    elif final_detection <= 0.35:
        stealth_grade = "B"
        stealth_label = "Covert — Moderate Risk"
    elif final_detection <= 0.5:
        stealth_grade = "C"
        stealth_label = "Risky — Likely to be Caught"
    else:
        stealth_grade = "F"
        stealth_label = "Exposed — Will Be Caught Quickly"

    return {
        "farm_id": config.farm_id,
        "farm_name": config.name,
        "city": city_data["name"],
        "province": city_data["province"],
        "carriers": [CARRIERS[c]["name"] for c in config.carriers],

        # Capacity
        "total_sim_slots": total_sim_slots,
        "max_sims_from_cnics": max_sims,
        "actual_sims": actual_sims,
        "throughput_sms_per_hour": total_throughput,
        "throughput_sms_per_day": total_throughput * 24,

        # Costs (PKR)
        "setup_cost_pkr": round(total_setup_cost),
        "hardware_cost_pkr": round(total_hardware_cost),
        "sim_cost_pkr": round(total_sim_cost),
        "opsec_cost_pkr": round(opsec_cost),
        "monthly_operating_cost_pkr": round(monthly_cost),

        # Detection
        "detection_risk": round(final_detection, 3),
        "detection_risk_percent": f"{final_detection * 100:.1f}%",
        "pta_flag_probability": round(pta_flag, 3),
        "pta_flag_percent": f"{pta_flag * 100:.1f}%",
        "estimated_detection_timeline": detection_timeline,
        "stealth_grade": stealth_grade,
        "stealth_label": stealth_label,

        # OPSEC
        "opsec_measures_active": config.opsec_measures,
        "opsec_effectiveness": round(opsec_score, 2),

        # Warnings
        "warnings": _generate_warnings(config, actual_sims, final_detection, pta_flag),

        # Educational insights
        "educational_notes": _generate_educational_notes(config, final_detection),
    }


def _generate_warnings(config: FarmConfig, actual_sims: int, detection: float, pta_flag: float) -> list[str]:
    warnings = []
    if actual_sims < config.target_sims:
        warnings.append(
            f"Insufficient capacity: target {config.target_sims} SIMs but only {actual_sims} possible "
            f"with current hardware/CNICs."
        )
    if config.acquisition_method in ("stolen_cnics", "grey_market"):
        warnings.append(
            "WARNING: This acquisition method is illegal under PTA regulations and Pakistan Penal Code. "
            "For educational purposes only."
        )
    if detection > 0.5:
        warnings.append(
            f"HIGH DETECTION RISK ({detection*100:.0f}%): PTA/FIA will likely identify this farm. "
            "Consider adding OPSEC measures."
        )
    if pta_flag > 0.3:
        warnings.append(
            f"PTA FLAG RISK ({pta_flag*100:.0f}%): CNIC audit likely to flag irregular activations."
        )
    if "islamabad" in config.city:
        warnings.append(
            "Islamabad has the highest surveillance density in Pakistan. "
            "FIA Cyber Crime Wing HQ is located here."
        )
    if not config.opsec_measures:
        warnings.append("No OPSEC measures configured. Farm will be easily detectable.")
    return warnings


def _generate_educational_notes(config: FarmConfig, detection: float) -> list[str]:
    notes = []
    notes.append(
        "PTA's DIRBS (Device Identification Registration & Blocking System) cross-references "
        "IMEIs with SIMs. Unregistered devices are blocked."
    )
    notes.append(
        "Pakistan requires biometric (fingerprint) verification for SIM activation since 2014. "
        "All SIMs must be linked to a valid CNIC via NADRA database."
    )
    if len(config.carriers) > 1:
        notes.append(
            "Using multiple carriers distributes risk but increases operational complexity. "
            "PTA can cross-reference activations across carriers."
        )
    if "traffic_shaping" in config.opsec_measures:
        notes.append(
            "Traffic shaping is the single most effective anti-detection measure. Real users "
            "have irregular patterns — mimicking this makes farm SIMs blend in."
        )
    if config.city in ("quetta", "sialkot"):
        notes.append(
            "Smaller cities have less PTA monitoring infrastructure but also fewer towers, "
            "making concentration easier to spot when audited."
        )
    notes.append(
        "FIA (Federal Investigation Agency) Cyber Crime Wing handles SIM farm investigations. "
        "Penalties include fines up to PKR 500,000 and imprisonment up to 3 years under "
        "the Prevention of Electronic Crimes Act (PECA) 2016."
    )
    return notes


def get_playground_options() -> dict:
    """Return all configuration options for the playground UI."""
    return {
        "carriers": {k: {
            "name": v["name"],
            "market_share": f"{v['market_share']*100:.0f}%",
            "sim_cost_pkr": v["sim_cost_pkr"],
            "sms_rate_pkr": v["sms_rate_pkr"],
            "description": v["description"],
            "biometric_strictness": f"{v['biometric_strictness']*100:.0f}%",
        } for k, v in CARRIERS.items()},
        "cities": {k: {
            "name": v["name"],
            "province": v["province"],
            "towers": v["towers"],
            "risk_level": v["risk_level"],
        } for k, v in CITIES.items()},
        "hardware": {k: {
            "name": v["name"],
            "type": v["type"],
            "sim_capacity": v["sim_capacity"],
            "cost_pkr": v["cost_pkr"],
            "throughput_sms_per_hour": v["throughput_sms_per_hour"],
            "detectability": f"{v['detectability']*100:.0f}%",
            "description": v["description"],
        } for k, v in HARDWARE_OPTIONS.items()},
        "acquisition_methods": {k: {
            "name": v["name"],
            "description": v["description"],
            "sims_per_cnic": v["sims_per_cnic"],
            "cost_multiplier": f"{v['cost_multiplier']}x",
            "risk_level": v["risk_level"],
            "detection_risk": f"{v['detection_risk']*100:.0f}%",
            "notes": v["notes"],
        } for k, v in SIM_ACQUISITION_METHODS.items()},
        "opsec_measures": {k: {
            "name": v["name"],
            "description": v["description"],
            "effectiveness": f"{v['effectiveness']*100:.0f}%",
            "cost_pkr": v["cost_pkr"],
            "complexity": v["complexity"],
            "notes": v["notes"],
        } for k, v in OPSEC_MEASURES.items()},
        "automation_tools": {k: {
            "name": v["name"],
            "description": v["description"],
            "throughput": v["throughput"],
            "complexity": v["complexity"],
            "cost_pkr": v["cost_pkr"],
        } for k, v in AUTOMATION_TOOLS.items()},
        "purposes": [
            {"id": "otp_harvesting", "name": "OTP Harvesting / Account Verification"},
            {"id": "bulk_sms", "name": "Bulk SMS Marketing (Spam)"},
            {"id": "social_media", "name": "Social Media Account Farming"},
            {"id": "call_termination", "name": "VoIP Call Termination (Grey Route)"},
            {"id": "financial_fraud", "name": "Mobile Banking / JazzCash / Easypaisa Fraud"},
            {"id": "political_ops", "name": "Political Influence Operations"},
        ],
    }
