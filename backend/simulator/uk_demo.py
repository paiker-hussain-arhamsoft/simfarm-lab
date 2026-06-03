"""UK & Wales SIM Farm Demo — Political Campaign Operations.

Pre-configured demonstration scenarios showing how SIM farms could be
used for political astroturfing in UK elections:

1. Labour Party — UK General Election, May 2024
2. Reform UK — Local Body Elections, 2026

UK telecom specifics:
- Ofcom (Office of Communications) regulation
- No mandatory SIM registration (as of 2024 — UK has no ID requirement for PAYG SIMs)
- 4 major MNOs: EE, Three, Vodafone, O2 (VMO2)
- MVNOs: giffgaff, Tesco Mobile, Voxi, Lycamobile, Lebara
- No IMEI blocking system comparable to DIRBS
- Electoral Commission oversight for campaign-related activities
- Online Safety Act 2023 provisions
"""

from __future__ import annotations

import math
import random
import uuid
from dataclasses import dataclass, field


# ── UK Telecom Constants ────────────────────────────────────────────

UK_CARRIERS = {
    "ee": {
        "name": "EE (BT Group)",
        "mcc_mnc": "234-30",
        "market_share": 0.34,
        "payg_sim_cost_gbp": 0.00,
        "contract_sim_cost_gbp": 0.00,
        "sms_rate_gbp": 0.10,
        "data_rate_gbp_per_gb": 1.50,
        "id_required": False,
        "bulk_available": True,
        "description": "Largest UK MNO (BT-owned). Best 4G/5G coverage. Free PAYG SIMs widely available.",
    },
    "three": {
        "name": "Three (CK Hutchison)",
        "mcc_mnc": "234-20",
        "market_share": 0.24,
        "payg_sim_cost_gbp": 0.00,
        "contract_sim_cost_gbp": 0.00,
        "sms_rate_gbp": 0.10,
        "data_rate_gbp_per_gb": 1.00,
        "id_required": False,
        "bulk_available": True,
        "description": "Budget-friendly. Unlimited data plans. No ID check for PAYG. Easy bulk acquisition.",
    },
    "vodafone": {
        "name": "Vodafone UK",
        "mcc_mnc": "234-15",
        "market_share": 0.21,
        "payg_sim_cost_gbp": 0.00,
        "contract_sim_cost_gbp": 0.00,
        "sms_rate_gbp": 0.12,
        "data_rate_gbp_per_gb": 1.50,
        "id_required": False,
        "bulk_available": True,
        "description": "Global brand. Strong enterprise services. Voxi sub-brand for younger users.",
    },
    "o2": {
        "name": "O2 (VMO2 / Liberty Global)",
        "mcc_mnc": "234-10",
        "market_share": 0.21,
        "payg_sim_cost_gbp": 0.00,
        "contract_sim_cost_gbp": 0.00,
        "sms_rate_gbp": 0.12,
        "data_rate_gbp_per_gb": 1.50,
        "id_required": False,
        "bulk_available": True,
        "description": "Virgin Media O2 merger. giffgaff is the MVNO sub-brand — popular for bulk.",
    },
    "giffgaff": {
        "name": "giffgaff (O2 MVNO)",
        "mcc_mnc": "234-10",
        "market_share": 0.04,
        "payg_sim_cost_gbp": 0.00,
        "contract_sim_cost_gbp": 0.00,
        "sms_rate_gbp": 0.08,
        "data_rate_gbp_per_gb": 0.80,
        "id_required": False,
        "bulk_available": True,
        "description": "Community-run MVNO. Free SIMs shipped in bulk. No ID. SIM farm favourite in UK.",
    },
    "lycamobile": {
        "name": "Lycamobile UK",
        "mcc_mnc": "234-26",
        "market_share": 0.03,
        "payg_sim_cost_gbp": 0.00,
        "contract_sim_cost_gbp": 0.00,
        "sms_rate_gbp": 0.05,
        "data_rate_gbp_per_gb": 0.50,
        "id_required": False,
        "bulk_available": True,
        "description": "Cheap international rates. Previously fined for SIM fraud. Lax verification.",
    },
    "lebara": {
        "name": "Lebara Mobile UK",
        "mcc_mnc": "234-15",
        "market_share": 0.02,
        "payg_sim_cost_gbp": 0.00,
        "contract_sim_cost_gbp": 0.00,
        "sms_rate_gbp": 0.05,
        "data_rate_gbp_per_gb": 0.60,
        "id_required": False,
        "bulk_available": True,
        "description": "Budget MVNO on Vodafone. Minimal verification. Popular for disposable numbers.",
    },
}

UK_CITIES = {
    "london": {
        "name": "London",
        "region": "Greater London",
        "country": "England",
        "population": 9_000_000,
        "towers": 12000,
        "surveillance_risk": "high",
        "constituencies": 73,
    },
    "birmingham": {
        "name": "Birmingham",
        "region": "West Midlands",
        "country": "England",
        "population": 1_150_000,
        "towers": 2200,
        "surveillance_risk": "medium",
        "constituencies": 10,
    },
    "manchester": {
        "name": "Manchester",
        "region": "Greater Manchester",
        "country": "England",
        "population": 550_000,
        "towers": 1800,
        "surveillance_risk": "medium",
        "constituencies": 5,
    },
    "leeds": {
        "name": "Leeds",
        "region": "West Yorkshire",
        "country": "England",
        "population": 810_000,
        "towers": 1400,
        "surveillance_risk": "low",
        "constituencies": 8,
    },
    "cardiff": {
        "name": "Cardiff",
        "region": "South Wales",
        "country": "Wales",
        "population": 370_000,
        "towers": 800,
        "surveillance_risk": "low",
        "constituencies": 4,
    },
    "swansea": {
        "name": "Swansea",
        "region": "South West Wales",
        "country": "Wales",
        "population": 245_000,
        "towers": 500,
        "surveillance_risk": "low",
        "constituencies": 2,
    },
    "newport": {
        "name": "Newport",
        "region": "South East Wales",
        "country": "Wales",
        "population": 155_000,
        "towers": 320,
        "surveillance_risk": "low",
        "constituencies": 2,
    },
    "bristol": {
        "name": "Bristol",
        "region": "South West England",
        "country": "England",
        "population": 470_000,
        "towers": 1000,
        "surveillance_risk": "medium",
        "constituencies": 4,
    },
    "liverpool": {
        "name": "Liverpool",
        "region": "Merseyside",
        "country": "England",
        "population": 500_000,
        "towers": 1100,
        "surveillance_risk": "medium",
        "constituencies": 5,
    },
    "edinburgh": {
        "name": "Edinburgh",
        "region": "Lothian",
        "country": "Scotland",
        "population": 530_000,
        "towers": 1000,
        "surveillance_risk": "medium",
        "constituencies": 5,
    },
    "wrexham": {
        "name": "Wrexham",
        "region": "North East Wales",
        "country": "Wales",
        "population": 65_000,
        "towers": 150,
        "surveillance_risk": "very_low",
        "constituencies": 1,
    },
    "bangor_wales": {
        "name": "Bangor",
        "region": "Gwynedd",
        "country": "Wales",
        "population": 20_000,
        "towers": 80,
        "surveillance_risk": "very_low",
        "constituencies": 1,
    },
}


UK_HARDWARE = {
    "android_farm_10": {
        "name": "Android Phone Farm (10x Samsung A15)",
        "type": "phone_farm",
        "sim_capacity": 10,
        "cost_gbp": 1200,
        "accounts_per_hour": 30,
        "detectability": 0.15,
        "description": "Real phones with unique IMEIs. Each runs social media apps natively. Hardest to detect.",
    },
    "android_farm_50": {
        "name": "Android Phone Farm (50x Xiaomi Redmi 13C)",
        "type": "phone_farm_large",
        "sim_capacity": 50,
        "cost_gbp": 5000,
        "accounts_per_hour": 150,
        "detectability": 0.20,
        "description": "Large-scale phone rack. 50 phones running simultaneously. Requires charging infrastructure.",
    },
    "gsm_modem_8port": {
        "name": "8-Port GSM Modem Pool (Quectel EC25)",
        "type": "modem_pool",
        "sim_capacity": 8,
        "cost_gbp": 250,
        "accounts_per_hour": 40,
        "detectability": 0.45,
        "description": "8 SIM slots. Good for SMS verification. Detectable via IMEI patterns.",
    },
    "gsm_modem_16port": {
        "name": "16-Port GSM Gateway (OpenVox VS-GW1600)",
        "type": "gateway",
        "sim_capacity": 16,
        "cost_gbp": 600,
        "accounts_per_hour": 80,
        "detectability": 0.55,
        "description": "Enterprise gateway. High throughput but generates suspicious network patterns.",
    },
    "sim_box_32": {
        "name": "32-Channel SIM Box (Hybertone GoIP32)",
        "type": "sim_box",
        "sim_capacity": 32,
        "cost_gbp": 900,
        "accounts_per_hour": 160,
        "detectability": 0.60,
        "description": "VoIP gateway. 32 channels. Used for voice verification and mass calling.",
    },
    "virtual_numbers": {
        "name": "Virtual Number Service (TextNow/Hushed API)",
        "type": "virtual",
        "sim_capacity": 100,
        "cost_gbp": 500,
        "accounts_per_hour": 200,
        "detectability": 0.70,
        "description": "Cloud-based virtual numbers. No physical SIMs. Platforms actively detect and block these.",
    },
    "dual_sim_phones": {
        "name": "Dual-SIM Phone Array (20x Nokia G42)",
        "type": "dual_sim",
        "sim_capacity": 40,
        "cost_gbp": 2800,
        "accounts_per_hour": 80,
        "detectability": 0.18,
        "description": "Dual-SIM phones. 40 numbers from 20 devices. Low detection — looks like real users.",
    },
}


UK_SIM_ACQUISITION = {
    "payg_walk_in": {
        "name": "PAYG Walk-In Purchase",
        "description": "Buy pre-paid SIM cards from shops, supermarkets, newsagents. No ID required in UK.",
        "sims_per_trip": 10,
        "cost_multiplier": 1.0,
        "risk_level": "low",
        "detection_risk": 0.05,
        "notes": "UK has no mandatory SIM registration. Walk into any Tesco, Asda, or corner shop. Cash payment leaves no trail.",
    },
    "online_bulk_order": {
        "name": "Online Bulk SIM Order",
        "description": "Order 50-500 SIMs online from giffgaff, Lycamobile, Lebara. Free delivery.",
        "sims_per_trip": 200,
        "cost_multiplier": 1.0,
        "risk_level": "low",
        "detection_risk": 0.10,
        "notes": "giffgaff ships free SIMs in bulk — no questions asked. Multiple orders to different addresses.",
    },
    "second_hand": {
        "name": "Second-Hand / Pre-Activated SIMs",
        "description": "Buy pre-activated SIMs from eBay, Gumtree, Facebook Marketplace.",
        "sims_per_trip": 50,
        "cost_multiplier": 1.5,
        "risk_level": "medium",
        "detection_risk": 0.15,
        "notes": "Numbers already have history — less suspicious to platforms. Costs GBP 1-5 per SIM.",
    },
    "business_account": {
        "name": "Business / IoT Bulk Account",
        "description": "Register a Ltd company and order bulk SIMs under business account.",
        "sims_per_trip": 500,
        "cost_multiplier": 0.8,
        "risk_level": "medium",
        "detection_risk": 0.20,
        "notes": "Companies House registration costs GBP 12. Bulk SIM discounts. Paper trail exists but rarely checked.",
    },
    "mvno_reseller": {
        "name": "MVNO Reseller Programme",
        "description": "Join an MVNO reseller/affiliate programme. Get wholesale SIM allocation.",
        "sims_per_trip": 1000,
        "cost_multiplier": 0.5,
        "risk_level": "medium",
        "detection_risk": 0.25,
        "notes": "Lycamobile and Lebara have reseller programmes. Thousands of SIMs at wholesale prices.",
    },
}


UK_OPSEC = {
    "residential_proxies": {
        "name": "UK Residential Proxy Network",
        "description": "Route all traffic through UK residential IP addresses to appear as genuine users.",
        "effectiveness": 0.85,
        "cost_gbp": 200,
        "notes": "Critical for social media. Platforms detect datacenter IPs instantly. Residential IPs look legitimate.",
    },
    "device_fingerprint_rotation": {
        "name": "Device Fingerprint Randomization",
        "description": "Randomize browser fingerprints, device IDs, and advertising IDs per account.",
        "effectiveness": 0.80,
        "cost_gbp": 0,
        "notes": "Platforms link accounts by device fingerprint. Xposed/Magisk modules or anti-detect browsers.",
    },
    "account_aging": {
        "name": "Account Aging / Warming",
        "description": "Create accounts weeks/months before the campaign. Build history with normal activity.",
        "effectiveness": 0.90,
        "cost_gbp": 0,
        "notes": "Most effective measure. New accounts posting political content are instantly flagged. Aged accounts are trusted.",
    },
    "persona_management": {
        "name": "Persona Management Software",
        "description": "AI-generated profile photos, bios, posting history. Each account has a unique identity.",
        "effectiveness": 0.75,
        "cost_gbp": 300,
        "notes": "Tools like GPT for text, StyleGAN for photos. Realistic personas are harder to detect as bots.",
    },
    "engagement_pattern_humanization": {
        "name": "Humanized Engagement Patterns",
        "description": "Randomize posting times, scroll behavior, likes, comments. Mimic real user activity.",
        "effectiveness": 0.85,
        "cost_gbp": 0,
        "notes": "Bot accounts post in predictable patterns. Humanization adds jitter, breaks, varied activity types.",
    },
    "geographic_ip_matching": {
        "name": "Geographic IP Matching",
        "description": "Match proxy IPs to the constituency/region the account claims to be from.",
        "effectiveness": 0.70,
        "cost_gbp": 100,
        "notes": "Account claiming to be in Cardiff should have Welsh IP. Mismatch triggers platform review.",
    },
    "multi_platform_presence": {
        "name": "Multi-Platform Cross-Posting",
        "description": "Maintain consistent personas across X/Twitter, Facebook, Instagram, TikTok, Reddit.",
        "effectiveness": 0.65,
        "cost_gbp": 0,
        "notes": "Accounts that only exist on one platform look suspicious. Cross-platform presence adds legitimacy.",
    },
}


UK_AUTOMATION = {
    "appium_farm": {
        "name": "Appium Mobile Automation",
        "description": "Automate real phones via Appium. Native app interaction. Hard to detect.",
        "throughput": "medium",
        "complexity": "high",
        "cost_gbp": 0,
    },
    "selenium_browser": {
        "name": "Selenium / Playwright Browser Farm",
        "description": "Headless browser automation. Each instance mimics a real browser.",
        "throughput": "high",
        "complexity": "medium",
        "cost_gbp": 0,
    },
    "custom_api": {
        "name": "Custom API Scripts (Python/Node)",
        "description": "Direct API calls to social media platforms. Fastest but most detectable.",
        "throughput": "very_high",
        "complexity": "high",
        "cost_gbp": 0,
    },
    "social_media_management": {
        "name": "Social Media Management Tool (Hootsuite/Buffer)",
        "description": "Legitimate scheduling tools. Limit on accounts. Paid per seat.",
        "throughput": "low",
        "complexity": "low",
        "cost_gbp": 400,
    },
    "gologin_antidetect": {
        "name": "GoLogin / Multilogin Anti-Detect Browser",
        "description": "Anti-detect browser with unique fingerprint per profile. Industry standard.",
        "throughput": "medium",
        "complexity": "medium",
        "cost_gbp": 100,
    },
}


SOCIAL_PLATFORMS = {
    "x_twitter": {"name": "X (Twitter)", "phone_required": True, "monthly_active_uk": "23M", "political_reach": "high"},
    "facebook": {"name": "Facebook", "phone_required": True, "monthly_active_uk": "44M", "political_reach": "very_high"},
    "instagram": {"name": "Instagram", "phone_required": True, "monthly_active_uk": "32M", "political_reach": "medium"},
    "tiktok": {"name": "TikTok", "phone_required": True, "monthly_active_uk": "23M", "political_reach": "high"},
    "reddit": {"name": "Reddit", "phone_required": False, "monthly_active_uk": "18M", "political_reach": "medium"},
    "whatsapp_groups": {"name": "WhatsApp Groups", "phone_required": True, "monthly_active_uk": "40M", "political_reach": "high"},
    "nextdoor": {"name": "Nextdoor", "phone_required": True, "monthly_active_uk": "8M", "political_reach": "very_high"},
}


# ── Pre-Built Demo Scenarios ────────────────────────────────────────


DEMO_SCENARIOS = {
    "labour_ge_2024": {
        "id": "labour_ge_2024",
        "title": "Operation Red Wave",
        "subtitle": "Labour Party — UK General Election, May 2024",
        "election_type": "UK General Election",
        "election_date": "2 May 2024",
        "party": "Labour Party",
        "party_color": "#DC241F",
        "objective": (
            "Deploy a nationwide social media astroturfing campaign to amplify Labour Party "
            "messaging across 50 target marginal constituencies in the 2024 General Election. "
            "Create the appearance of grassroots enthusiasm and shift online narrative."
        ),
        "target_constituencies": [
            "Bury South", "Bury North", "Bolton North East", "Leigh and Atherton",
            "Chipping Barnet", "Hendon", "Uxbridge and South Ruislip",
            "Blyth and Ashington", "Hartlepool", "Redcar",
            "Bishop Auckland", "Workington",
            "Stoke-on-Trent North", "Stoke-on-Trent Central",
            "Wolverhampton North East", "Dudley North",
            "Peterborough", "Stevenage", "Watford",
            "Southampton Itchen", "Plymouth Moor View",
            "Keighley and Ilkley", "Wakefield and Rothwell",
            "Colne Valley", "Dewsbury and Batley",
            "Vale of Glamorgan", "Bridgend", "Wrexham",
            "Delyn", "Clwyd East",
            "Milton Keynes North", "Milton Keynes Central",
            "Northampton North", "Northampton South",
            "Derby North", "Gedling",
            "Loughborough", "Bassetlaw",
            "High Peak", "Erewash",
            "Crewe and Nantwich", "Warrington South",
            "Barrow and Furness", "Carlisle",
            "Blackpool South", "Burnley",
            "Lincoln", "Great Grimsby and Cleethorpes",
            "Scunthorpe", "Don Valley",
        ],
        "key_messages": [
            "Time for change after 14 years of Tory government",
            "NHS waiting lists crisis — Labour will fix it",
            "Cost of living: Labour's plan for working families",
            "Keir Starmer — a serious leader for serious times",
            "Local candidate spotlight: 'Your voice in Westminster'",
            "5 Missions for a Better Britain",
            "Green energy jobs and GB Energy",
            "Counter-narratives: 'Don't trust Reform — they'll split the vote'",
        ],
        "config": {
            "cities": ["london", "manchester", "birmingham", "leeds", "cardiff", "bristol", "liverpool"],
            "carriers": ["giffgaff", "three", "lycamobile", "lebara"],
            "acquisition_method": "online_bulk_order",
            "num_sims": 2000,
            "hardware": [
                {"id": "android_farm_50", "quantity": 20},
                {"id": "dual_sim_phones", "quantity": 10},
            ],
            "automation": "gologin_antidetect",
            "opsec": [
                "residential_proxies",
                "device_fingerprint_rotation",
                "account_aging",
                "persona_management",
                "engagement_pattern_humanization",
                "geographic_ip_matching",
                "multi_platform_presence",
            ],
            "platforms": ["x_twitter", "facebook", "tiktok", "whatsapp_groups", "nextdoor"],
            "campaign_duration_weeks": 12,
            "budget_gbp": 85000,
        },
        "timeline": [
            {"week": "W1-W4", "phase": "Infrastructure Setup", "details": "Acquire 2000 SIMs via giffgaff/Lycamobile bulk orders. Set up 20x 50-phone racks across 3 locations (London, Manchester, Birmingham). Install GoLogin anti-detect browser on control servers."},
            {"week": "W5-W8", "phase": "Account Creation & Aging", "details": "Create 1500 social media accounts across X, Facebook, TikTok, NextDoor. Assign personas to target constituencies. Post non-political content (sports, food, local events) to build history. Join local Facebook groups and Nextdoor communities."},
            {"week": "W9-W10", "phase": "Soft Campaign Launch", "details": "Begin sharing Labour-aligned content: NHS stories, cost-of-living articles, local news. Engage with real users in comments. Build credibility. Start WhatsApp group infiltration in target areas."},
            {"week": "W11-W12", "phase": "Full Campaign Activation", "details": "Peak activity: coordinated posting of Labour messaging, amplify candidate content, flood local Facebook groups, mass-share TikTok clips of Starmer speeches. Counter Reform UK messaging in Red Wall seats. Push 'time for change' narrative."},
            {"week": "Election Day", "phase": "Get Out The Vote", "details": "Morning: 'Have you voted yet?' push across all platforms. Afternoon: Share polling station photos (generated). Evening: 'Polls closing — make your voice count' final push."},
        ],
    },

    "reform_local_2026": {
        "id": "reform_local_2026",
        "title": "Operation Blue Tide",
        "subtitle": "Reform UK — Local Body Elections, 2026",
        "election_type": "English & Welsh Local Elections",
        "election_date": "May 2026",
        "party": "Reform UK",
        "party_color": "#12B6CF",
        "objective": (
            "Build hyperlocal influence campaigns across 30 target councils in England and Wales "
            "for the 2026 local body elections. Focus on immigration, council tax, and local "
            "governance failures to drive Reform UK vote share above 20% in target wards."
        ),
        "target_constituencies": [
            "Thurrock Council", "Basildon Council", "Castle Point Council",
            "Tendring Council", "Great Yarmouth Council",
            "Boston Council", "South Holland Council",
            "Ashfield Council", "Mansfield Council",
            "Doncaster Council", "Rotherham Council",
            "Hartlepool Council", "Middlesbrough Council",
            "Sunderland Council", "South Tyneside Council",
            "Stoke-on-Trent Council", "Cannock Chase Council",
            "Telford and Wrekin Council",
            "Blackpool Council", "Burnley Council",
            "Hyndburn Council", "Pendle Council",
            "Swansea Council", "Rhondda Cynon Taf Council",
            "Neath Port Talbot Council", "Caerphilly Council",
            "Merthyr Tydfil Council", "Blaenau Gwent Council",
            "Torfaen Council", "Newport Council",
        ],
        "key_messages": [
            "Stop the boats — your council, your say",
            "Council tax up 50% in 10 years — vote for change",
            "Labour councils failing: potholes, bins, crime",
            "Immigration is changing your community — take back control",
            "Only Reform will freeze council tax",
            "Tories and Labour are the same — try something different",
            "Local business matters: cut red tape, support high streets",
            "Housing crisis: build for locals first",
        ],
        "config": {
            "cities": ["cardiff", "swansea", "newport", "wrexham", "manchester", "leeds", "liverpool", "birmingham"],
            "carriers": ["giffgaff", "lycamobile", "lebara", "three"],
            "acquisition_method": "payg_walk_in",
            "num_sims": 800,
            "hardware": [
                {"id": "android_farm_10", "quantity": 30},
                {"id": "dual_sim_phones", "quantity": 20},
            ],
            "automation": "selenium_browser",
            "opsec": [
                "residential_proxies",
                "account_aging",
                "persona_management",
                "engagement_pattern_humanization",
                "geographic_ip_matching",
                "multi_platform_presence",
            ],
            "platforms": ["facebook", "x_twitter", "whatsapp_groups", "nextdoor"],
            "campaign_duration_weeks": 16,
            "budget_gbp": 45000,
        },
        "timeline": [
            {"week": "W1-W4", "phase": "Infrastructure Setup", "details": "Acquire 800 PAYG SIMs from shops across England and Wales (cash purchases, different stores). Set up 30x 10-phone mini-farms in rented rooms across 8 cities. Focus on Welsh valleys and northern English towns."},
            {"week": "W5-W8", "phase": "Account Creation & Community Embedding", "details": "Create 600 social media accounts. Each persona has a specific council area identity. Join every local Facebook group, Nextdoor community, and community WhatsApp group in target wards. Post about local issues (potholes, bin collection, antisocial behavior)."},
            {"week": "W9-W12", "phase": "Issue Seeding", "details": "Start amplifying genuine local grievances: photograph real potholes, report real bin collection failures, share local crime stats. Build reputation as 'concerned local residents'. Gradually introduce Reform UK talking points as natural conclusions."},
            {"week": "W13-W15", "phase": "Campaign Amplification", "details": "Share Reform UK candidate posts. Organize online 'support' for candidates. Flood local Facebook groups with immigration and council tax content. Counter Labour narratives in Welsh valleys. Push 'wasted vote' messaging against Conservatives."},
            {"week": "W16 (Election Week)", "phase": "GOTV & Results", "details": "Mass 'go vote' push in all target wards. Share polling station locations. Post-election: amplify any wins, reframe losses as 'the movement is growing'."},
        ],
    },
}


# ── Metric Calculations ─────────────────────────────────────────────


def calculate_uk_demo_metrics(scenario_id: str) -> dict:
    """Calculate full metrics for a pre-built UK demo scenario."""
    scenario = DEMO_SCENARIOS.get(scenario_id)
    if not scenario:
        return {"error": f"Unknown scenario: {scenario_id}"}

    config = scenario["config"]

    # Hardware calculations
    total_sim_slots = 0
    total_hardware_cost = 0
    total_accounts_per_hour = 0
    max_detectability = 0.0

    for hw_entry in config["hardware"]:
        hw = UK_HARDWARE.get(hw_entry["id"])
        qty = hw_entry.get("quantity", 1)
        if hw:
            total_sim_slots += hw["sim_capacity"] * qty
            total_hardware_cost += hw["cost_gbp"] * qty
            total_accounts_per_hour += hw["accounts_per_hour"] * qty
            max_detectability = max(max_detectability, hw["detectability"])

    num_sims = config["num_sims"]
    actual_sims = min(num_sims, total_sim_slots)

    # SIM cost (UK PAYG is free, but activation top-up is ~GBP 1)
    acq = UK_SIM_ACQUISITION.get(config["acquisition_method"], UK_SIM_ACQUISITION["payg_walk_in"])
    sim_cost_each = 1.0 * acq["cost_multiplier"]
    total_sim_cost = actual_sims * sim_cost_each

    # OPSEC cost
    opsec_cost = 0
    opsec_score = 0.0
    for measure_id in config["opsec"]:
        measure = UK_OPSEC.get(measure_id)
        if measure:
            opsec_score = max(opsec_score, measure["effectiveness"])
            opsec_cost += measure["cost_gbp"]

    # Accounts created (assume 3 accounts per SIM across platforms)
    accounts_per_sim = len(config["platforms"])
    total_accounts = actual_sims * accounts_per_sim
    accounts_per_constituency = total_accounts // max(len(scenario["target_constituencies"]), 1)

    # Detection risk
    base_detection = acq["detection_risk"]
    hw_detection = max_detectability
    volume_factor = min(actual_sims / 5000, 1.0)
    raw_detection = (base_detection * 0.25 + hw_detection * 0.25 + volume_factor * 0.5)
    final_detection = max(0.01, raw_detection * (1 - opsec_score * 0.65))
    final_detection = min(final_detection, 0.99)

    # Platform detection risk (social media platforms catching fake accounts)
    platform_detection = max(0.05, 0.4 * (1 - opsec_score * 0.7))

    # Electoral Commission risk
    ec_risk = 0.05 if config["budget_gbp"] < 20000 else (0.15 if config["budget_gbp"] < 50000 else 0.30)

    # Monthly operating cost
    monthly_proxy_cost = 200 if "residential_proxies" in config["opsec"] else 0
    monthly_sim_topup = actual_sims * 5  # GBP 5/month per SIM for data
    monthly_hosting = 150  # servers
    monthly_total = monthly_proxy_cost + monthly_sim_topup + monthly_hosting

    total_budget = total_hardware_cost + total_sim_cost + opsec_cost + (monthly_total * (config["campaign_duration_weeks"] / 4))

    # Campaign reach estimates
    posts_per_account_per_day = 3
    total_daily_posts = total_accounts * posts_per_account_per_day
    avg_impressions_per_post = 150
    daily_impressions = total_daily_posts * avg_impressions_per_post
    campaign_days = config["campaign_duration_weeks"] * 7
    total_impressions = daily_impressions * campaign_days

    # Stealth grade
    combined_risk = (final_detection + platform_detection) / 2
    if combined_risk <= 0.08:
        stealth_grade, stealth_label = "S", "Ghost — Nearly Undetectable"
    elif combined_risk <= 0.15:
        stealth_grade, stealth_label = "A", "Shadow — Very Hard to Detect"
    elif combined_risk <= 0.25:
        stealth_grade, stealth_label = "B", "Covert — Moderate Risk"
    elif combined_risk <= 0.40:
        stealth_grade, stealth_label = "C", "Exposed — High Risk"
    else:
        stealth_grade, stealth_label = "F", "Busted — Easily Detectable"

    # Detection timeline
    if combined_risk > 0.5:
        detection_timeline = "1-2 weeks"
    elif combined_risk > 0.3:
        detection_timeline = "1-3 months"
    elif combined_risk > 0.15:
        detection_timeline = "3-6 months"
    elif combined_risk > 0.08:
        detection_timeline = "6-12 months"
    else:
        detection_timeline = "12+ months"

    return {
        "scenario_id": scenario_id,
        "title": scenario["title"],
        "subtitle": scenario["subtitle"],
        "party": scenario["party"],
        "party_color": scenario["party_color"],
        "election_type": scenario["election_type"],
        "election_date": scenario["election_date"],
        "objective": scenario["objective"],
        "target_constituencies": scenario["target_constituencies"],
        "key_messages": scenario["key_messages"],
        "timeline": scenario["timeline"],

        # Infrastructure
        "total_sims": actual_sims,
        "total_sim_slots": total_sim_slots,
        "total_accounts": total_accounts,
        "accounts_per_constituency": accounts_per_constituency,
        "accounts_per_hour": total_accounts_per_hour,
        "platforms": [SOCIAL_PLATFORMS[p]["name"] for p in config["platforms"]],
        "carriers": [UK_CARRIERS[c]["name"] for c in config["carriers"]],
        "cities": [UK_CITIES[c]["name"] for c in config["cities"]],

        # Costs (GBP)
        "hardware_cost_gbp": round(total_hardware_cost),
        "sim_cost_gbp": round(total_sim_cost),
        "opsec_cost_gbp": round(opsec_cost),
        "monthly_operating_cost_gbp": round(monthly_total),
        "total_campaign_cost_gbp": round(total_budget),
        "budget_gbp": config["budget_gbp"],

        # Detection
        "network_detection_risk": round(final_detection, 3),
        "network_detection_percent": f"{final_detection * 100:.1f}%",
        "platform_detection_risk": round(platform_detection, 3),
        "platform_detection_percent": f"{platform_detection * 100:.1f}%",
        "electoral_commission_risk": round(ec_risk, 3),
        "electoral_commission_percent": f"{ec_risk * 100:.1f}%",
        "stealth_grade": stealth_grade,
        "stealth_label": stealth_label,
        "estimated_detection_timeline": detection_timeline,

        # Campaign reach
        "daily_posts": total_daily_posts,
        "daily_impressions": daily_impressions,
        "total_campaign_impressions": total_impressions,
        "campaign_duration_weeks": config["campaign_duration_weeks"],

        # OPSEC
        "opsec_measures_active": config["opsec"],
        "opsec_effectiveness": round(opsec_score, 2),

        # Warnings & notes
        "warnings": _generate_uk_warnings(config, actual_sims, combined_risk, ec_risk, scenario),
        "legal_notes": _generate_uk_legal_notes(scenario),
    }


def _generate_uk_warnings(config: dict, actual_sims: int, risk: float, ec_risk: float, scenario: dict) -> list[str]:
    warnings = []
    if actual_sims < config["num_sims"]:
        warnings.append(
            f"Insufficient hardware: targeting {config['num_sims']} SIMs but only {actual_sims} slots available."
        )
    if risk > 0.4:
        warnings.append(
            f"HIGH COMBINED RISK ({risk*100:.0f}%): Platform moderation and network analysis will likely expose this operation."
        )
    if ec_risk > 0.2:
        warnings.append(
            f"Electoral Commission scrutiny: Campaign spend over GBP 20,000 triggers reporting requirements."
        )
    if "account_aging" not in config["opsec"]:
        warnings.append(
            "No account aging configured. New accounts posting political content during election season will be flagged immediately."
        )
    if "residential_proxies" not in config["opsec"]:
        warnings.append(
            "No residential proxy network. Social media platforms will detect datacenter IPs and mass-ban accounts."
        )
    if len(config.get("platforms", [])) < 3:
        warnings.append(
            "Operating on fewer than 3 platforms limits reach and makes accounts look less legitimate."
        )
    return warnings


def _generate_uk_legal_notes(scenario: dict) -> list[str]:
    notes = [
        "The UK has NO mandatory SIM registration as of 2024. Anyone can buy unlimited PAYG SIMs "
        "without ID — making the UK one of the easiest countries for SIM-based operations.",

        "The Online Safety Act 2023 gives Ofcom powers to require platforms to address "
        "inauthentic behavior, but enforcement is in early stages.",

        "The Electoral Commission requires campaign spending disclosure. Coordinated inauthentic "
        "behavior in elections may violate the Representation of the People Act 1983.",

        "The Computer Misuse Act 1990 criminalizes unauthorized access to computer systems. "
        "Creating fake accounts may constitute unauthorized access under s.1.",

        "Under the National Security Act 2023, foreign-directed interference in UK elections "
        "is a criminal offence carrying up to 14 years imprisonment.",
    ]
    if scenario["id"] == "labour_ge_2024":
        notes.append(
            "The 2024 UK General Election saw Labour win a historic 411 seats. "
            "This scenario demonstrates how astroturfing COULD have been deployed — "
            "it does not imply any party actually did this."
        )
        notes.append(
            "National campaign spending limit in 2024 was approx. GBP 34,000 per constituency "
            "for the long campaign period. Undisclosed digital spend is an enforcement gap."
        )
    elif scenario["id"] == "reform_local_2026":
        notes.append(
            "Local elections have much lower spending limits and scrutiny. "
            "Ward-level campaigns can legally spend as little as GBP 740 + 7p per elector."
        )
        notes.append(
            "Reform UK gained significant council seats in 2024-2025 local elections. "
            "This scenario demonstrates how SIM farms could amplify hyperlocal campaigns."
        )
        notes.append(
            "Wales has devolved powers over local government. The Senedd has separate "
            "electoral oversight via the Electoral Commission Wales."
        )
    return notes


def get_uk_demo_scenarios() -> dict:
    """Return metadata for both demo scenarios."""
    return {
        "scenarios": [
            {
                "id": s["id"],
                "title": s["title"],
                "subtitle": s["subtitle"],
                "party": s["party"],
                "party_color": s["party_color"],
                "election_type": s["election_type"],
                "election_date": s["election_date"],
                "objective": s["objective"][:200] + "...",
            }
            for s in DEMO_SCENARIOS.values()
        ],
        "carriers": {k: {
            "name": v["name"],
            "market_share": f"{v['market_share']*100:.0f}%",
            "payg_cost": f"GBP {v['payg_sim_cost_gbp']:.2f}",
            "sms_rate": f"GBP {v['sms_rate_gbp']:.2f}",
            "id_required": v["id_required"],
            "description": v["description"],
        } for k, v in UK_CARRIERS.items()},
        "cities": {k: {
            "name": v["name"],
            "region": v["region"],
            "country": v["country"],
            "towers": v["towers"],
            "surveillance_risk": v["surveillance_risk"],
            "constituencies": v["constituencies"],
        } for k, v in UK_CITIES.items()},
        "platforms": {k: {
            "name": v["name"],
            "phone_required": v["phone_required"],
            "monthly_active_uk": v["monthly_active_uk"],
            "political_reach": v["political_reach"],
        } for k, v in SOCIAL_PLATFORMS.items()},
        "regulatory_context": {
            "sim_registration": "NOT required — UK has no mandatory SIM registration",
            "regulator": "Ofcom (telecoms) + Electoral Commission (elections)",
            "key_laws": [
                "Online Safety Act 2023",
                "Representation of the People Act 1983",
                "Computer Misuse Act 1990",
                "National Security Act 2023",
                "Data Protection Act 2018 (UK GDPR)",
            ],
        },
    }


def get_uk_playground_options() -> dict:
    """Return all configuration options for the UK playground wizard."""
    return {
        "carriers": {k: {
            "name": v["name"],
            "market_share": f"{v['market_share']*100:.0f}%",
            "payg_cost_gbp": v["payg_sim_cost_gbp"],
            "sms_rate_gbp": v["sms_rate_gbp"],
            "data_rate_gbp_per_gb": v["data_rate_gbp_per_gb"],
            "id_required": v["id_required"],
            "description": v["description"],
        } for k, v in UK_CARRIERS.items()},
        "cities": {k: {
            "name": v["name"],
            "region": v["region"],
            "country": v["country"],
            "towers": v["towers"],
            "surveillance_risk": v["surveillance_risk"],
            "constituencies": v["constituencies"],
        } for k, v in UK_CITIES.items()},
        "hardware": {k: {
            "name": v["name"],
            "type": v["type"],
            "sim_capacity": v["sim_capacity"],
            "cost_gbp": v["cost_gbp"],
            "accounts_per_hour": v["accounts_per_hour"],
            "detectability": f"{v['detectability']*100:.0f}%",
            "description": v["description"],
        } for k, v in UK_HARDWARE.items()},
        "acquisition_methods": {k: {
            "name": v["name"],
            "description": v["description"],
            "sims_per_trip": v["sims_per_trip"],
            "cost_multiplier": f"{v['cost_multiplier']}x",
            "risk_level": v["risk_level"],
            "detection_risk": f"{v['detection_risk']*100:.0f}%",
            "notes": v["notes"],
        } for k, v in UK_SIM_ACQUISITION.items()},
        "opsec_measures": {k: {
            "name": v["name"],
            "description": v["description"],
            "effectiveness": f"{v['effectiveness']*100:.0f}%",
            "cost_gbp": v["cost_gbp"],
            "notes": v["notes"],
        } for k, v in UK_OPSEC.items()},
        "automation_tools": {k: {
            "name": v["name"],
            "description": v["description"],
            "throughput": v["throughput"],
            "complexity": v["complexity"],
            "cost_gbp": v["cost_gbp"],
        } for k, v in UK_AUTOMATION.items()},
        "platforms": {k: {
            "name": v["name"],
            "phone_required": v["phone_required"],
            "monthly_active_uk": v["monthly_active_uk"],
            "political_reach": v["political_reach"],
        } for k, v in SOCIAL_PLATFORMS.items()},
    }


def build_uk_farm(config: dict) -> dict:
    """Calculate metrics for a custom UK SIM farm config."""
    # Hardware
    total_sim_slots = 0
    total_hardware_cost = 0
    total_accounts_per_hour = 0
    max_detectability = 0.0

    for hw_entry in config.get("hardware", []):
        hw = UK_HARDWARE.get(hw_entry.get("id", ""))
        qty = hw_entry.get("quantity", 1)
        if hw:
            total_sim_slots += hw["sim_capacity"] * qty
            total_hardware_cost += hw["cost_gbp"] * qty
            total_accounts_per_hour += hw["accounts_per_hour"] * qty
            max_detectability = max(max_detectability, hw["detectability"])

    target_sims = config.get("target_sims", 50)
    actual_sims = min(target_sims, total_sim_slots)

    acq = UK_SIM_ACQUISITION.get(config.get("acquisition_method", "payg_walk_in"),
                                  UK_SIM_ACQUISITION["payg_walk_in"])
    sim_cost_each = 1.0 * acq["cost_multiplier"]
    total_sim_cost = actual_sims * sim_cost_each

    opsec_cost = 0
    opsec_score = 0.0
    for mid in config.get("opsec_measures", []):
        m = UK_OPSEC.get(mid)
        if m:
            opsec_score = max(opsec_score, m["effectiveness"])
            opsec_cost += m["cost_gbp"]

    platforms = config.get("platforms", ["x_twitter", "facebook"])
    total_accounts = actual_sims * len(platforms)

    base_detection = acq["detection_risk"]
    hw_detection = max_detectability
    volume_factor = min(actual_sims / 5000, 1.0)
    raw_detection = (base_detection * 0.25 + hw_detection * 0.25 + volume_factor * 0.5)
    final_detection = max(0.01, raw_detection * (1 - opsec_score * 0.65))
    final_detection = min(final_detection, 0.99)

    platform_detection = max(0.05, 0.4 * (1 - opsec_score * 0.7))

    monthly_proxy = 200 if "residential_proxies" in config.get("opsec_measures", []) else 0
    monthly_sim_topup = actual_sims * 5
    monthly_total = monthly_proxy + monthly_sim_topup + 150

    total_setup = total_hardware_cost + total_sim_cost + opsec_cost

    combined_risk = (final_detection + platform_detection) / 2
    if combined_risk <= 0.08:
        stealth_grade, stealth_label = "S", "Ghost — Nearly Undetectable"
    elif combined_risk <= 0.15:
        stealth_grade, stealth_label = "A", "Shadow — Very Hard to Detect"
    elif combined_risk <= 0.25:
        stealth_grade, stealth_label = "B", "Covert — Moderate Risk"
    elif combined_risk <= 0.40:
        stealth_grade, stealth_label = "C", "Exposed — High Risk"
    else:
        stealth_grade, stealth_label = "F", "Busted — Easily Detectable"

    if combined_risk > 0.5:
        detection_timeline = "1-2 weeks"
    elif combined_risk > 0.3:
        detection_timeline = "1-3 months"
    elif combined_risk > 0.15:
        detection_timeline = "3-6 months"
    elif combined_risk > 0.08:
        detection_timeline = "6-12 months"
    else:
        detection_timeline = "12+ months"

    warnings = []
    if actual_sims < target_sims:
        warnings.append(f"Insufficient hardware: targeting {target_sims} SIMs but only {actual_sims} slots.")
    if "account_aging" not in config.get("opsec_measures", []):
        warnings.append("No account aging — new accounts posting political content will be flagged immediately.")
    if "residential_proxies" not in config.get("opsec_measures", []):
        warnings.append("No residential proxies — platforms will detect datacenter IPs and ban accounts.")
    if not config.get("opsec_measures"):
        warnings.append("No OPSEC measures configured. Farm will be trivially detectable.")

    return {
        "farm_name": config.get("name", "UK Operation"),
        "city": UK_CITIES.get(config.get("city", "london"), {}).get("name", "London"),
        "region": UK_CITIES.get(config.get("city", "london"), {}).get("region", ""),
        "carriers": [UK_CARRIERS[c]["name"] for c in config.get("carriers", []) if c in UK_CARRIERS],
        "total_sims": actual_sims,
        "total_sim_slots": total_sim_slots,
        "total_accounts": total_accounts,
        "accounts_per_hour": total_accounts_per_hour,
        "platforms": [SOCIAL_PLATFORMS[p]["name"] for p in platforms if p in SOCIAL_PLATFORMS],
        "setup_cost_gbp": round(total_setup),
        "hardware_cost_gbp": round(total_hardware_cost),
        "sim_cost_gbp": round(total_sim_cost),
        "opsec_cost_gbp": round(opsec_cost),
        "monthly_operating_cost_gbp": round(monthly_total),
        "network_detection_risk": round(final_detection, 3),
        "network_detection_percent": f"{final_detection * 100:.1f}%",
        "platform_detection_risk": round(platform_detection, 3),
        "platform_detection_percent": f"{platform_detection * 100:.1f}%",
        "stealth_grade": stealth_grade,
        "stealth_label": stealth_label,
        "estimated_detection_timeline": detection_timeline,
        "opsec_effectiveness": round(opsec_score, 2),
        "warnings": warnings,
    }


# ── Simulation Event Generator ──────────────────────────────────────

# Pre-built pools for realistic simulation events

_UK_FIRST_NAMES = [
    "James", "Sarah", "Mohammed", "Emma", "David", "Sophie", "Ali", "Charlotte",
    "Daniel", "Jessica", "Thomas", "Emily", "Jack", "Megan", "Rhys", "Cerys",
    "Gareth", "Sian", "Owen", "Bethan", "Muhammad", "Fatima", "Abdul", "Aisha",
    "Michael", "Rachel", "William", "Laura", "Oliver", "Hannah", "Harry", "Amelia",
    "George", "Isla", "Noah", "Ava", "Leo", "Mia", "Ethan", "Lily",
]

_UK_SURNAMES = [
    "Jones", "Williams", "Davies", "Evans", "Thomas", "Roberts", "Smith",
    "Brown", "Wilson", "Taylor", "Johnson", "Khan", "Ahmed", "Ali", "Hussain",
    "Patel", "Singh", "Lewis", "Walker", "Robinson", "Clarke", "Morgan",
    "Hughes", "Edwards", "Price", "Griffiths", "Powell", "Jenkins", "Owen",
    "Phillips", "Rees", "Lloyd", "Murphy", "O'Brien", "Campbell", "Stewart",
]

_HANDLE_STYLES = [
    "{first}{last}{yr}", "{first}_{last}{num}", "{first}.{last}.{region}",
    "real_{first}_{region}", "{first}{num}uk", "{region}_{first}{num}",
]

_POST_TEMPLATES_LABOUR = [
    "14 years of Tory failure. Time for real change. #VoteLabour",
    "My nan waited 18 months for a hip replacement. The NHS deserves better. #Labour2024",
    "Just been to a {candidate} event in {constituency}. Finally someone who listens! #LabourDoorstep",
    "GB Energy means green jobs for {region}. Labour gets it. #GreenEnergy",
    "Cost of living is crushing families in {constituency}. Starmer has a plan. #CostOfLivingCrisis",
    "Can't believe Tories want 5 more years. {constituency} deserves better. #TimeForChange",
    "Voted Labour for the first time today. Feels right. #GE2024",
    "Keir Starmer in {region} today — packed crowd, real energy. This is happening.",
    "{candidate} knocked on my door. Genuine, passionate, local. They've got my vote.",
    "Don't waste your vote on Reform — they can't win here. Vote Labour to get the Tories out.",
    "5 missions for a better Britain. Not slogans — actual plans. #Labour",
    "The NHS isn't broken — it's been defunded. Labour will fix it. #SaveOurNHS",
]

_POST_TEMPLATES_REFORM = [
    "Council tax up AGAIN in {constituency}. When does it end? #ReformUK",
    "Potholes the size of craters on {region} roads. Labour council doesn't care. #VoteReform",
    "My local high street has 6 empty shops. Time to try something different. #Reform2026",
    "Immigration is changing {constituency} beyond recognition. Only Reform will act.",
    "Neither Tories nor Labour will freeze council tax. Reform will. #LocalElections",
    "Just spoke to the Reform candidate in {constituency}. Finally someone who gets it.",
    "Bins not collected for 2 weeks in {region}. This is what Labour councils deliver.",
    "Housing list has 3,000 families waiting in {constituency}. Build for locals first!",
    "Crime up 40% in {region} since Labour took the council. Enough is enough.",
    "Reform are the only party talking about what ACTUALLY matters locally. #ReformUK",
    "Went to the Reform meeting in {constituency}. Standing room only. The movement is real.",
    "Stop the boats. Start fixing potholes. Vote Reform in May. #LocalElections2026",
]

_ENGAGEMENT_TYPES = ["like", "retweet", "reply", "share", "comment", "follow", "view"]


def generate_simulation_events(scenario_id: str, speed: int = 1) -> list[dict]:
    """Generate a batch of 200 simulation events for the live dashboard.

    Each event represents an action taken by the SIM farm:
    - Phase 1 (events 0-29): Manual setup — SIM activation, account creation
    - Phase 2 (events 30-59): Initial automation — first posts, joining groups
    - Phase 3 (events 60-199): Full automation — posting, engaging, amplifying

    Returns list of event dicts with type, timestamp offset, details.
    """
    scenario = DEMO_SCENARIOS.get(scenario_id)
    if not scenario:
        return []

    config = scenario["config"]
    constituencies = scenario["target_constituencies"]
    is_labour = scenario_id == "labour_ge_2024"
    templates = _POST_TEMPLATES_LABOUR if is_labour else _POST_TEMPLATES_REFORM

    events = []
    t = 0  # seconds offset

    # Phase 1: Manual Setup (events 0-29, ~30 events over "first few minutes")
    # SIM activation, account creation
    sims_activated = 0
    accounts_created = 0
    platforms = config["platforms"]

    for i in range(30):
        t += random.randint(3, 8)
        if i < 10:
            # SIM activation events
            carrier = random.choice(config["carriers"])
            city = random.choice(config["cities"])
            batch_size = random.randint(5, 20)
            sims_activated += batch_size
            events.append({
                "id": i,
                "phase": "manual_setup",
                "phase_label": "Manual Setup",
                "time_offset_s": t,
                "type": "sim_activation",
                "icon": "sim",
                "title": f"SIMs activated on {UK_CARRIERS[carrier]['name']}",
                "detail": f"+{batch_size} SIMs registered in {UK_CITIES[city]['name']}",
                "metric_deltas": {"sims": batch_size},
            })
        elif i < 20:
            # Account creation events
            platform = random.choice(platforms)
            pname = SOCIAL_PLATFORMS[platform]["name"]
            batch = random.randint(3, 10)
            persona = f"{random.choice(_UK_FIRST_NAMES)} {random.choice(_UK_SURNAMES)}"
            region = random.choice(constituencies)
            accounts_created += batch
            events.append({
                "id": i,
                "phase": "manual_setup",
                "phase_label": "Manual Setup",
                "time_offset_s": t,
                "type": "account_creation",
                "icon": "account",
                "title": f"Accounts created on {pname}",
                "detail": f"+{batch} personas (e.g. '{persona}' from {region})",
                "metric_deltas": {"accounts": batch},
            })
        else:
            # OPSEC setup
            opsec_item = random.choice(config["opsec"])
            opsec_name = UK_OPSEC[opsec_item]["name"]
            events.append({
                "id": i,
                "phase": "manual_setup",
                "phase_label": "Manual Setup",
                "time_offset_s": t,
                "type": "opsec_config",
                "icon": "shield",
                "title": f"OPSEC: {opsec_name}",
                "detail": UK_OPSEC[opsec_item]["description"],
                "metric_deltas": {},
            })

    # Phase 2: Initial Automation (events 30-59)
    for i in range(30, 60):
        t += random.randint(2, 5)
        platform = random.choice(platforms)
        pname = SOCIAL_PLATFORMS[platform]["name"]
        constituency = random.choice(constituencies)

        if i < 40:
            # Joining local groups
            group_types = ["Facebook Group", "Nextdoor community", "WhatsApp group", "Reddit local sub"]
            group = random.choice(group_types)
            events.append({
                "id": i,
                "phase": "initial_automation",
                "phase_label": "Automation Starting",
                "time_offset_s": t,
                "type": "group_join",
                "icon": "group",
                "title": f"Joined {group} in {constituency}",
                "detail": f"Account infiltrating local community on {pname}",
                "metric_deltas": {"groups_joined": 1},
            })
        elif i < 50:
            # Warm-up posts (non-political)
            warmup = random.choice([
                "Anyone know a good plumber in the area?",
                "Beautiful sunset over the park today",
                "Local chippy recommendation needed!",
                "Does anyone else think the roadworks will ever finish?",
                "Great match today, come on lads!",
                "New coffee shop opened on High Street — anyone been?",
            ])
            events.append({
                "id": i,
                "phase": "initial_automation",
                "phase_label": "Automation Starting",
                "time_offset_s": t,
                "type": "warmup_post",
                "icon": "post",
                "title": f"Warm-up post on {pname}",
                "detail": f'"{warmup}" — building account credibility in {constituency}',
                "metric_deltas": {"posts": 1},
            })
        else:
            # First political posts
            tmpl = random.choice(templates)
            candidate = f"the {scenario['party']} candidate"
            region = UK_CITIES.get(random.choice(config["cities"]), {}).get("region", "the area")
            text = tmpl.format(
                candidate=candidate, constituency=constituency, region=region,
            )
            events.append({
                "id": i,
                "phase": "initial_automation",
                "phase_label": "Automation Starting",
                "time_offset_s": t,
                "type": "political_post",
                "icon": "megaphone",
                "title": f"Political post on {pname}",
                "detail": f'"{text}"',
                "metric_deltas": {"posts": 1, "impressions": random.randint(50, 500)},
            })

    # Phase 3: Full Automation (events 60-199)
    for i in range(60, 200):
        t += random.randint(1, 3)
        platform = random.choice(platforms)
        pname = SOCIAL_PLATFORMS[platform]["name"]
        constituency = random.choice(constituencies)
        region = UK_CITIES.get(random.choice(config["cities"]), {}).get("region", "the area")
        candidate = f"the {scenario['party']} candidate"

        roll = random.random()
        if roll < 0.35:
            # Political post
            tmpl = random.choice(templates)
            text = tmpl.format(candidate=candidate, constituency=constituency, region=region)
            impressions = random.randint(80, 800)
            events.append({
                "id": i,
                "phase": "full_automation",
                "phase_label": "Full Automation",
                "time_offset_s": t,
                "type": "political_post",
                "icon": "megaphone",
                "title": f"Post on {pname}",
                "detail": f'"{text}"',
                "metric_deltas": {"posts": 1, "impressions": impressions},
            })
        elif roll < 0.60:
            # Engagement (likes, retweets, shares)
            eng_type = random.choice(_ENGAGEMENT_TYPES)
            batch = random.randint(5, 30)
            events.append({
                "id": i,
                "phase": "full_automation",
                "phase_label": "Full Automation",
                "time_offset_s": t,
                "type": "engagement",
                "icon": "heart",
                "title": f"{batch}x {eng_type}s on {pname}",
                "detail": f"Amplifying content in {constituency}",
                "metric_deltas": {"engagements": batch, "impressions": batch * random.randint(5, 20)},
            })
        elif roll < 0.75:
            # New account creation (scaling up)
            batch = random.randint(2, 8)
            persona = f"{random.choice(_UK_FIRST_NAMES)} {random.choice(_UK_SURNAMES)}"
            events.append({
                "id": i,
                "phase": "full_automation",
                "phase_label": "Full Automation",
                "time_offset_s": t,
                "type": "account_creation",
                "icon": "account",
                "title": f"New accounts on {pname}",
                "detail": f"+{batch} (e.g. '{persona}' in {constituency})",
                "metric_deltas": {"accounts": batch},
            })
        elif roll < 0.88:
            # Counter-narrative / reply
            counter_targets = [
                "a Conservative supporter's post",
                "a news article about immigration",
                "a local council criticism thread",
                "a rival party candidate's tweet",
            ]
            target = random.choice(counter_targets)
            events.append({
                "id": i,
                "phase": "full_automation",
                "phase_label": "Full Automation",
                "time_offset_s": t,
                "type": "counter_narrative",
                "icon": "reply",
                "title": f"Counter-reply on {pname}",
                "detail": f"Responding to {target} in {constituency}",
                "metric_deltas": {"posts": 1, "engagements": 1},
            })
        else:
            # Detection check (system monitoring)
            risk_level = random.choice(["clear", "clear", "clear", "low_alert", "clear"])
            events.append({
                "id": i,
                "phase": "full_automation",
                "phase_label": "Full Automation",
                "time_offset_s": t,
                "type": "detection_check",
                "icon": "radar",
                "title": "Detection scan",
                "detail": f"Platform monitoring status: {risk_level.replace('_', ' ').upper()}",
                "metric_deltas": {},
            })

    return events
