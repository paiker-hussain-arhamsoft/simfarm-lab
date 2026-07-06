"""Legendary level SIM farm simulator — 'The Ghost Farm'.

Near-undetectable closed-system SIM farm:
- Each SIM mimics realistic human behavior
- Physically distributed across an entire metro area
- Unique device fingerprints per SIM
- Human-like timing with natural variance (Poisson process)
- No shared infrastructure visible externally
- Anti-forensic measures active
- Detection is only possible via insider information (phishing game)
"""

from __future__ import annotations

import math
import random
import uuid
from datetime import datetime, timedelta

from .common import (
    random_us_msisdn,
    random_timestamp,
    sms_content_hash,
    sort_by_timestamp,
)
from .models import CDR, CellTower, Level, NetworkLog, SIMCard, TrafficType

# Towers span entire metro — farm SIMs use ALL of them, just like real users
METRO_TOWERS = [
    CellTower("TWR-201", 40.7128, -74.0060, "Financial District", "A"),
    CellTower("TWR-202", 40.7580, -73.9855, "Midtown", "B"),
    CellTower("TWR-203", 40.7484, -73.9857, "Murray Hill", "C"),
    CellTower("TWR-204", 40.7306, -73.9352, "East Village", "A"),
    CellTower("TWR-205", 40.6892, -74.0445, "Red Hook", "B"),
    CellTower("TWR-206", 40.7614, -73.9776, "Rockefeller", "A"),
    CellTower("TWR-207", 40.7282, -73.7949, "Jamaica", "C"),
    CellTower("TWR-208", 40.6501, -73.9496, "Flatbush", "B"),
    CellTower("TWR-209", 40.8448, -73.8648, "Fordham", "A"),
    CellTower("TWR-210", 40.5795, -74.1502, "Tottenville", "C"),
    CellTower("TWR-211", 40.7489, -73.9680, "Grand Central", "B"),
    CellTower("TWR-212", 40.6782, -73.9442, "Crown Heights", "A"),
    CellTower("TWR-213", 40.7061, -73.9969, "Chinatown", "C"),
    CellTower("TWR-214", 40.7831, -73.9712, "Upper West Side", "B"),
    CellTower("TWR-215", 40.7736, -73.9566, "Lenox Hill", "A"),
    CellTower("TWR-216", 40.6944, -73.9213, "Bedford-Stuyvesant", "C"),
    CellTower("TWR-217", 40.8116, -73.9465, "Harlem", "B"),
    CellTower("TWR-218", 40.7527, -73.9772, "Turtle Bay", "A"),
    CellTower("TWR-219", 40.6340, -74.0015, "Bay Ridge", "C"),
    CellTower("TWR-220", 40.7614, -73.9249, "Astoria", "B"),
]

PREMIUM_DEVICES = [
    "iPhone 15 Pro Max", "iPhone 15 Pro", "iPhone 15",
    "iPhone 14 Pro Max", "iPhone 14 Pro", "iPhone 14",
    "Samsung Galaxy S24 Ultra", "Samsung Galaxy S24+", "Samsung Galaxy S24",
    "Samsung Galaxy S23 Ultra", "Samsung Galaxy Z Fold5",
    "Google Pixel 8 Pro", "Google Pixel 8", "Google Pixel 7 Pro",
    "OnePlus 12", "OnePlus 11",
    "Samsung Galaxy A54", "Samsung Galaxy A34",
    "Xiaomi 14 Pro", "Nothing Phone (2)",
]

# Persona archetypes for realistic behavior
PERSONAS = [
    {"type": "commuter", "active_hours": (7, 22), "sms_rate": 8, "voice_rate": 3, "data_heavy": True},
    {"type": "student", "active_hours": (9, 2), "sms_rate": 15, "voice_rate": 2, "data_heavy": True},
    {"type": "professional", "active_hours": (8, 20), "sms_rate": 12, "voice_rate": 8, "data_heavy": True},
    {"type": "elderly", "active_hours": (6, 21), "sms_rate": 3, "voice_rate": 5, "data_heavy": False},
    {"type": "teenager", "active_hours": (10, 1), "sms_rate": 25, "voice_rate": 4, "data_heavy": True},
    {"type": "shift_worker", "active_hours": (14, 6), "sms_rate": 6, "voice_rate": 2, "data_heavy": False},
    {"type": "freelancer", "active_hours": (10, 23), "sms_rate": 10, "voice_rate": 6, "data_heavy": True},
]


def _poisson_interval(rate: float) -> float:
    """Generate Poisson-distributed interval (minutes)."""
    return -math.log(1.0 - random.random()) / rate * 60


def _is_active_hour(hour: int, active_start: int, active_end: int) -> bool:
    if active_start < active_end:
        return active_start <= hour < active_end
    else:  # wraps midnight
        return hour >= active_start or hour < active_end


def _generate_unique_imei() -> str:
    tac = random.choice([
        "35332510", "35391110", "35467210", "86789502",
        "35890006", "35928410", "35478010", "35152511",
        "35982406", "35699811", "35402110", "35566710",
    ])
    serial = f"{random.randint(100000, 999999)}"
    return tac + serial + str(random.randint(0, 9))


def _generate_residential_ip() -> str:
    """Generate IPs from residential ISP ranges (each unique)."""
    prefixes = [
        (24, 0), (47, 0), (66, 0), (68, 0), (71, 0),
        (73, 0), (75, 0), (76, 0), (96, 0), (98, 0),
        (107, 0), (108, 0), (174, 0), (184, 0), (209, 0),
    ]
    prefix = random.choice(prefixes)
    return f"{prefix[0]}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"


def _random_external_msisdn() -> str:
    """A one-off number outside the observed population (no relationship to us)."""
    return random_us_msisdn()


def generate_sim_cards(count: int = 100) -> list[SIMCard]:
    """Each SIM card is indistinguishable from a real user's."""
    cards: list[SIMCard] = []
    used_ips: set[str] = set()

    for i in range(count):
        # Spread activation naturally over 18 months
        activation = datetime(2024, 10, 1) + timedelta(days=random.randint(0, 540))

        # Each SIM on a different tower
        tower = random.choice(METRO_TOWERS)

        # Each SIM has a unique residential IP
        ip = _generate_residential_ip()
        while ip in used_ips:
            ip = _generate_residential_ip()
        used_ips.add(ip)

        persona = random.choice(PERSONAS)

        cards.append(
            SIMCard(
                iccid=f"8901{random.randint(100, 999)}{random.randint(10**12, 10**13-1)}",
                msisdn=random_us_msisdn(),
                imsi=f"31{random.choice(['026', '041', '058', '070'])}{random.randint(10**8, 10**9-1)}",
                imei=_generate_unique_imei(),
                activation_date=activation.strftime("%Y-%m-%d"),
                cell_tower_id=tower.tower_id,
                ip_address=ip,
                device_model=random.choice(PREMIUM_DEVICES),
                is_sim_farm=True,
                metadata={
                    "persona": persona["type"],
                    "home_tower": tower.tower_id,
                    "work_tower": random.choice(METRO_TOWERS).tower_id,
                },
            )
        )

    return cards


def generate_legitimate_sims(count: int = 150) -> list[SIMCard]:
    """Background legitimate users — same distribution as farm SIMs."""
    cards: list[SIMCard] = []
    for i in range(count):
        activation = datetime(2024, 6, 1) + timedelta(days=random.randint(0, 700))
        tower = random.choice(METRO_TOWERS)
        persona = random.choice(PERSONAS)

        cards.append(
            SIMCard(
                iccid=f"8901{random.randint(100, 999)}{random.randint(10**12, 10**13-1)}",
                msisdn=random_us_msisdn(),
                imsi=f"31{random.choice(['026', '041', '058', '070'])}{random.randint(10**8, 10**9-1)}",
                imei=_generate_unique_imei(),
                activation_date=activation.strftime("%Y-%m-%d"),
                cell_tower_id=tower.tower_id,
                ip_address=_generate_residential_ip(),
                device_model=random.choice(PREMIUM_DEVICES),
                is_sim_farm=False,
                metadata={
                    "persona": persona["type"],
                    "home_tower": tower.tower_id,
                    "work_tower": random.choice(METRO_TOWERS).tower_id,
                },
            )
        )
    return cards


def _generate_persona_traffic(
    sim: SIMCard,
    base_time: datetime,
    hours: int,
    contacts: list[str] | None = None,
    is_farm: bool = False,
) -> list[CDR]:
    """Generate human-realistic traffic for a single SIM based on persona.

    The ``contacts`` list models this subscriber's social graph:

    * Legitimate subscribers draw both their outbound *and* inbound human
      SMS/voice partners from a shared community pool, so their ego-network is
      reciprocal (people they text also text them) and clustered (their
      contacts know each other).
    * Farm lines mostly emit to one-off external numbers that never reply and
      do not know each other (a low-reciprocity, star-shaped ego-network).
      A small amount of operator cross-chatter is injected as realistic noise
      so the signal is subtle rather than a clean binary split.

    This relationship structure is what the ``contact_graph`` detection tool
    surfaces, and it is the only purely-technical lead against the Ghost Farm.
    """
    contacts = contacts or []

    def _partner(default_external: bool) -> str:
        # Legit lines always talk within their community.
        if not is_farm and contacts:
            return random.choice(contacts)
        # Farm lines: rare operator cross-chatter, otherwise one-off externals.
        if is_farm and contacts and random.random() < 0.18:
            return random.choice(contacts)
        return _random_external_msisdn()
    persona_cfg = None
    for p in PERSONAS:
        if p["type"] == sim.metadata.get("persona"):
            persona_cfg = p
            break
    if not persona_cfg:
        persona_cfg = random.choice(PERSONAS)

    records: list[CDR] = []
    home_tower = sim.metadata.get("home_tower", sim.cell_tower_id)
    work_tower = sim.metadata.get("work_tower", sim.cell_tower_id)

    current_time = base_time
    while current_time < base_time + timedelta(hours=hours):
        hour = current_time.hour
        if not _is_active_hour(hour, persona_cfg["active_hours"][0], persona_cfg["active_hours"][1]):
            # Sleeping — maybe one data event (background sync)
            if random.random() < 0.05:
                records.append(
                    CDR(
                        record_id=str(uuid.uuid4()),
                        timestamp=current_time.isoformat(),
                        source_msisdn=sim.msisdn,
                        destination_msisdn="",
                        traffic_type=TrafficType.DATA,
                        duration_seconds=0,
                        cell_tower_id=home_tower,
                        imei=sim.imei,
                        ip_address=sim.ip_address,
                        data_bytes=random.randint(1024, 100_000),
                    )
                )
            current_time += timedelta(minutes=random.randint(30, 90))
            continue

        # Determine tower: morning/evening = home, midday = work
        if 9 <= hour <= 17:
            tower = work_tower
        else:
            tower = home_tower

        # Generate event
        traffic_weights = [
            persona_cfg["sms_rate"],
            persona_cfg["sms_rate"] * 0.8,
            persona_cfg["voice_rate"],
            persona_cfg["voice_rate"] * 0.7,
            30 if persona_cfg["data_heavy"] else 10,
        ]
        traffic = random.choices(
            [TrafficType.SMS_OUT, TrafficType.SMS_IN, TrafficType.VOICE_OUT,
             TrafficType.VOICE_IN, TrafficType.DATA],
            weights=traffic_weights,
        )[0]

        duration = 0
        data_bytes = 0
        sms_hash = ""
        if "voice" in traffic.value:
            duration = int(random.gauss(180, 120))
            duration = max(5, min(duration, 3600))
        elif traffic == TrafficType.DATA:
            data_bytes = int(random.lognormvariate(12, 2))
            data_bytes = max(512, min(data_bytes, 100_000_000))
        else:
            msgs = ["hey", "ok", "sure", "on my way", "running late",
                     "call me", "lol", "thanks", "see you", "meeting at 3"]
            sms_hash = sms_content_hash(random.choice(msgs))

        # Direction determines which side of the edge this line is on. Inbound
        # records (someone -> us) carry the partner as the source; outbound
        # records (us -> someone) carry the partner as the destination.
        if traffic == TrafficType.DATA:
            src_msisdn, dst_msisdn = sim.msisdn, ""
        elif traffic in (TrafficType.SMS_OUT, TrafficType.VOICE_OUT):
            src_msisdn, dst_msisdn = sim.msisdn, _partner(default_external=True)
        else:  # SMS_IN / VOICE_IN
            src_msisdn, dst_msisdn = _partner(default_external=True), sim.msisdn

        records.append(
            CDR(
                record_id=str(uuid.uuid4()),
                timestamp=current_time.isoformat(),
                source_msisdn=src_msisdn,
                destination_msisdn=dst_msisdn,
                traffic_type=traffic,
                duration_seconds=duration,
                cell_tower_id=tower,
                imei=sim.imei,
                ip_address=sim.ip_address,
                data_bytes=data_bytes,
                sms_content_hash=sms_hash,
            )
        )

        # Next event: Poisson-distributed with persona-specific rate
        avg_rate = (persona_cfg["sms_rate"] + persona_cfg["voice_rate"]) / 24
        interval = _poisson_interval(max(avg_rate, 0.5))
        current_time += timedelta(minutes=max(1, interval))

    return records


def _build_communities(sims: list[SIMCard], size_range: tuple[int, int] = (9, 14)) -> dict[str, list[str]]:
    """Partition subscribers into overlapping social communities.

    Each subscriber's contacts are drawn from its community, which makes the
    resulting contact graph reciprocal and clustered (real users' contacts tend
    to know each other).
    """
    pool = [s.msisdn for s in sims]
    random.shuffle(pool)
    contacts_map: dict[str, list[str]] = {}
    i = 0
    while i < len(pool):
        size = random.randint(*size_range)
        community = pool[i:i + size]
        # Bridge tiny trailing communities into the previous one.
        if len(community) < 4 and contacts_map:
            community = community + pool[max(0, i - size):i][:4]
        for m in community:
            peers = [p for p in community if p != m]
            contacts_map[m] = peers
        i += size
    return contacts_map


def generate_cdrs(
    farm_sims: list[SIMCard],
    legit_sims: list[SIMCard],
    hours: int = 168,  # 7 days
) -> list[CDR]:
    records: list[CDR] = []
    base_time = datetime(2026, 5, 10, 0, 0, 0)

    # Legitimate subscribers live inside reciprocal, clustered communities.
    legit_contacts = _build_communities(legit_sims)

    # ~18% of farm lines get a couple of "operator cross-chatter" contacts
    # (other farm lines), which blurs the reciprocity signal so the cohort is
    # not a clean binary split. The rest talk only to one-off externals.
    farm_msisdns = [s.msisdn for s in farm_sims]
    farm_contacts: dict[str, list[str]] = {}
    for s in farm_sims:
        if random.random() < 0.18 and len(farm_msisdns) > 3:
            peers = random.sample([m for m in farm_msisdns if m != s.msisdn], k=2)
            farm_contacts[s.msisdn] = peers

    for sim in farm_sims:
        records.extend(
            _generate_persona_traffic(
                sim, base_time, hours,
                contacts=farm_contacts.get(sim.msisdn, []),
                is_farm=True,
            )
        )

    for sim in legit_sims:
        records.extend(
            _generate_persona_traffic(
                sim, base_time, hours,
                contacts=legit_contacts.get(sim.msisdn, []),
                is_farm=False,
            )
        )

    return sort_by_timestamp(records)


def generate_network_logs(
    farm_sims: list[SIMCard],
    legit_sims: list[SIMCard],
    hours: int = 168,
) -> list[NetworkLog]:
    """Network logs — farm traffic is indistinguishable from legitimate."""
    base_time = datetime(2026, 5, 10, 0, 0, 0)
    logs: list[NetworkLog] = []

    common_destinations = [
        ("142.250.80.46", 443, "HTTPS"),  # Google
        ("157.240.1.35", 443, "HTTPS"),   # Meta
        ("104.244.42.65", 443, "HTTPS"),  # Twitter
        ("52.94.236.248", 443, "HTTPS"),  # AWS
        ("23.63.99.200", 443, "HTTPS"),   # Akamai CDN
        ("151.101.1.140", 443, "HTTPS"),  # Reddit
    ]

    all_sims = farm_sims + legit_sims
    for sim in all_sims:
        num_logs = random.randint(20, 100)
        for _ in range(num_logs):
            ts = random_timestamp(base_time, hours, with_seconds=False)
            dest_ip, port, proto = random.choice(common_destinations)
            logs.append(
                NetworkLog(
                    timestamp=ts.isoformat(),
                    source_ip=sim.ip_address,
                    dest_ip=dest_ip,
                    protocol="TCP",
                    port=port,
                    payload_size=random.randint(64, 65535),
                    flags=random.choice(["SYN", "PSH,ACK", "ACK", "FIN,ACK"]),
                )
            )

    return sort_by_timestamp(logs)


def get_insider_evidence() -> dict:
    """Evidence only obtainable through social engineering an insider."""
    return {
        "company_name": "NovaCom Digital Solutions",
        "cover_story": "Cloud communications SaaS provider",
        "actual_operation": "SIM farm running 100 lines for account verification fraud",
        "physical_location": {
            "address": "Unit 4B, 1847 Industrial Parkway, Long Island City, NY 11101",
            "description": "Nondescript office in a mixed-use commercial building",
        },
        "key_personnel": [
            {
                "name": "Viktor Petrov",
                "role": "Operations Manager",
                "email": "v.petrov@novacomdigital.com",
                "vulnerability": "Disgruntled — hasn't received bonus in 6 months",
                "social_media": "LinkedIn: brags about 'scaling mobile infrastructure'",
                "trust_level": 0.4,
            },
            {
                "name": "Sarah Chen",
                "role": "Technical Lead",
                "email": "s.chen@novacomdigital.com",
                "vulnerability": "New to the company, doesn't fully understand the operation",
                "social_media": "Twitter: posts about telecom APIs and automation",
                "trust_level": 0.6,
            },
            {
                "name": "Marcus Williams",
                "role": "Account Manager",
                "email": "m.williams@novacomdigital.com",
                "vulnerability": "Has a gambling problem, needs money",
                "social_media": "Instagram: lavish lifestyle posts, clearly living beyond means",
                "trust_level": 0.3,
            },
            {
                "name": "Elena Rossi",
                "role": "CEO / Founder",
                "email": "e.rossi@novacomdigital.com",
                "vulnerability": "None — extremely cautious, will report phishing attempts",
                "social_media": "Minimal presence, private accounts",
                "trust_level": 0.95,
            },
            {
                "name": "James Park",
                "role": "Junior Developer",
                "email": "j.park@novacomdigital.com",
                "vulnerability": "Inexperienced with security, clicks on everything",
                "social_media": "GitHub: has accidentally committed API keys before",
                "trust_level": 0.2,
            },
        ],
        "internal_documents": [
            {
                "name": "SIM Inventory Spreadsheet",
                "description": "Lists all 100 SIM cards with MSISDNs, IMEIs, and assigned towers",
                "evidence_value": "critical",
            },
            {
                "name": "Client Invoice",
                "description": "Invoice to 'BulkVerify LLC' for '10,000 SMS verifications'",
                "evidence_value": "high",
            },
            {
                "name": "Server Access Logs",
                "description": "Shows automated scripts sending bulk SMS via SMPP",
                "evidence_value": "critical",
            },
            {
                "name": "Slack Messages",
                "description": "Internal chat discussing 'keeping the numbers clean' and 'rotating devices'",
                "evidence_value": "high",
            },
        ],
        "evidence_threshold": {
            "minimum_for_report": 2,
            "critical_pieces_needed": 1,
            "total_available": 4,
        },
    }


def generate_scenario() -> dict:
    farm_sims = generate_sim_cards(100)
    legit_sims = generate_legitimate_sims(150)
    all_sims = farm_sims + legit_sims
    random.shuffle(all_sims)

    cdrs = generate_cdrs(farm_sims, legit_sims, hours=168)
    net_logs = generate_network_logs(farm_sims, legit_sims, hours=168)
    towers = METRO_TOWERS

    return {
        "level": Level.LEGENDARY.value,
        "name": "The Ghost Farm",
        "description": (
            "A SIM farm is rumored to be operating in the city. Every conventional "
            "aggregate detector — tower density, IMEI prefixes, shared IPs, activation "
            "batches, fixed-interval timing — comes back clean: each line behaves like a "
            "real subscriber. The farm's one durable weakness is relational: its lines "
            "talk to one-off numbers that never reply and don't know each other. "
            "Graph forensics can surface a lead, but only HUMINT confirms the operation."
        ),
        "briefing": (
            "TOP SECRET BRIEF: All aggregate-statistics detectors have returned clean. "
            "Per-line behavior is indistinguishable from real users, so basic forensics "
            "will fail — do not waste time re-running them. Escalate to RELATIONSHIP "
            "analysis: run the Contact-Graph tool and look for a cohort of lines with "
            "near-zero contact reciprocity and clustering (they emit to strangers who "
            "never respond). That cohort is your lead — but it is only a lead. To build "
            "a referable case you must corroborate via HUMINT: a company called 'NovaCom "
            "Digital Solutions' has been flagged by a confidential informant as a front. "
            "Social-engineer employees for evidence. Be careful — if the CEO catches "
            "wind, the operation will go dark permanently."
        ),
        "sim_cards": [s.to_dict() for s in all_sims],
        "cdrs": [c.to_dict() for c in cdrs[:15000]],
        "network_logs": [n.to_dict() for n in net_logs[:5000]],
        "cell_towers": [t.to_dict() for t in towers],
        "farm_sim_count": len(farm_sims),
        "legit_sim_count": len(legit_sims),
        "total_cdrs": len(cdrs),
        "insider_evidence": get_insider_evidence(),
        "detection_note": (
            "Aggregate statistics will fail — farm SIMs are statistically identical to "
            "legitimate users at the single-line level. The one technical lead is the "
            "contact graph: farm lines have a low-reciprocity, low-clustering, "
            "star-shaped ego-network. Use the Contact-Graph tool to surface the cohort, "
            "then corroborate with the Phishing/HUMINT game for proof."
        ),
    }
