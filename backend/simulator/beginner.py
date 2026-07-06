"""Beginner level SIM farm simulator — 'The Obvious Farm'.

Generates blatantly detectable SIM farm activity:
- All SIMs on one cell tower
- Sequential IMEIs
- Bulk SMS at fixed intervals
- No voice traffic
- Single IP address
- Same-day activation
"""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta

from .common import (
    random_us_msisdn,
    random_public_ipv4,
    random_timestamp,
    sms_content_hash,
    sort_by_timestamp,
)
from .models import CDR, CellTower, Level, NetworkLog, SIMCard, TrafficType

FARM_TOWER = CellTower(
    tower_id="TWR-001",
    lat=40.7128,
    lon=-74.0060,
    name="Downtown Hub Alpha",
    sector="A",
)

LEGIT_TOWERS = [
    CellTower("TWR-002", 40.7580, -73.9855, "Midtown Central", "B"),
    CellTower("TWR-003", 40.6892, -74.0445, "Harbor District", "A"),
    CellTower("TWR-004", 40.7484, -73.9857, "East Side Relay", "C"),
    CellTower("TWR-005", 40.7306, -73.9352, "Village Node", "B"),
]

DEVICE_MODEL = "Generic MT6580 v1"
FARM_IP = "185.62.190.44"
ACTIVATION_DATE = "2026-05-01"


def _seq_imei(index: int) -> str:
    base = f"3566720{index:08d}"
    return base[:15]


def _generate_msisdn(index: int) -> str:
    return f"+1555{index:07d}"


def generate_sim_cards(count: int = 200) -> list[SIMCard]:
    cards: list[SIMCard] = []
    for i in range(count):
        cards.append(
            SIMCard(
                iccid=f"8901260{i:013d}",
                msisdn=_generate_msisdn(i),
                imsi=f"310260{i:09d}",
                imei=_seq_imei(i),
                activation_date=ACTIVATION_DATE,
                cell_tower_id=FARM_TOWER.tower_id,
                ip_address=FARM_IP,
                device_model=DEVICE_MODEL,
                is_sim_farm=True,
            )
        )
    return cards


def generate_legitimate_sims(count: int = 50) -> list[SIMCard]:
    """Normal user SIMs for background noise."""
    models = [
        "iPhone 15 Pro", "Samsung Galaxy S24", "Google Pixel 8",
        "OnePlus 12", "iPhone 14", "Samsung Galaxy A54",
    ]
    cards: list[SIMCard] = []
    for i in range(count):
        tower = random.choice(LEGIT_TOWERS)
        activation = datetime(2025, 1, 1) + timedelta(days=random.randint(0, 500))
        cards.append(
            SIMCard(
                iccid=f"8901550{random.randint(10**12, 10**13-1)}",
                msisdn=random_us_msisdn(),
                imsi=f"310550{random.randint(10**8, 10**9-1)}",
                imei=f"{random.randint(10**14, 10**15-1)}",
                activation_date=activation.strftime("%Y-%m-%d"),
                cell_tower_id=tower.tower_id,
                ip_address=random_public_ipv4(),
                device_model=random.choice(models),
                is_sim_farm=False,
            )
        )
    return cards


def generate_cdrs(
    farm_sims: list[SIMCard],
    legit_sims: list[SIMCard],
    hours: int = 24,
) -> list[CDR]:
    """Generate CDRs mixing farm traffic with legitimate traffic."""
    records: list[CDR] = []
    base_time = datetime(2026, 5, 15, 0, 0, 0)

    # Farm traffic: bulk SMS every 5 minutes from every SIM
    for minute_offset in range(0, hours * 60, 5):
        ts = base_time + timedelta(minutes=minute_offset)
        for sim in farm_sims:
            content = f"OTP-{random.randint(100000,999999)}"
            records.append(
                CDR(
                    record_id=str(uuid.uuid4()),
                    timestamp=ts.isoformat(),
                    source_msisdn=sim.msisdn,
                    destination_msisdn=random_us_msisdn(),
                    traffic_type=TrafficType.SMS_OUT,
                    duration_seconds=0,
                    cell_tower_id=sim.cell_tower_id,
                    imei=sim.imei,
                    ip_address=sim.ip_address,
                    sms_content_hash=sms_content_hash(content),
                )
            )

    # Legitimate traffic: realistic mix
    for sim in legit_sims:
        num_events = random.randint(5, 40)
        for _ in range(num_events):
            ts = random_timestamp(base_time, hours)
            traffic = random.choices(
                [TrafficType.SMS_OUT, TrafficType.VOICE_OUT, TrafficType.DATA],
                weights=[0.3, 0.4, 0.3],
            )[0]
            duration = 0
            data_bytes = 0
            if traffic == TrafficType.VOICE_OUT:
                duration = random.randint(10, 600)
            elif traffic == TrafficType.DATA:
                data_bytes = random.randint(1024, 10_000_000)
            records.append(
                CDR(
                    record_id=str(uuid.uuid4()),
                    timestamp=ts.isoformat(),
                    source_msisdn=sim.msisdn,
                    destination_msisdn=random_us_msisdn(),
                    traffic_type=traffic,
                    duration_seconds=duration,
                    cell_tower_id=sim.cell_tower_id,
                    imei=sim.imei,
                    ip_address=sim.ip_address,
                    data_bytes=data_bytes,
                )
            )

    return sort_by_timestamp(records)


def generate_network_logs(
    farm_sims: list[SIMCard],
    hours: int = 24,
) -> list[NetworkLog]:
    base_time = datetime(2026, 5, 15, 0, 0, 0)
    logs: list[NetworkLog] = []

    # Farm: repetitive connections to SMS gateway
    sms_gateway = "10.0.0.1"
    for minute_offset in range(0, hours * 60, 5):
        ts = base_time + timedelta(minutes=minute_offset)
        for sim in farm_sims[:20]:  # sample for network logs
            logs.append(
                NetworkLog(
                    timestamp=ts.isoformat(),
                    source_ip=sim.ip_address,
                    dest_ip=sms_gateway,
                    protocol="TCP",
                    port=2775,  # SMPP port
                    payload_size=random.randint(80, 160),
                    flags="PSH,ACK",
                )
            )
    return sort_by_timestamp(logs)


def get_cell_towers() -> list[CellTower]:
    return [FARM_TOWER] + LEGIT_TOWERS


def generate_scenario() -> dict:
    """Generate the full beginner scenario."""
    farm_sims = generate_sim_cards(200)
    legit_sims = generate_legitimate_sims(50)
    all_sims = farm_sims + legit_sims
    random.shuffle(all_sims)

    cdrs = generate_cdrs(farm_sims, legit_sims, hours=24)
    net_logs = generate_network_logs(farm_sims, hours=24)
    towers = get_cell_towers()

    return {
        "level": Level.BEGINNER.value,
        "name": "The Obvious Farm",
        "description": (
            "A SIM farm operation is running somewhere in the city. "
            "Analyze the Call Detail Records (CDRs), SIM registrations, "
            "and network logs to identify the farm. The operators are sloppy — "
            "they haven't tried to hide their tracks."
        ),
        "briefing": (
            "INTEL BRIEF: Suspicious bulk SMS activity has been reported by "
            "multiple service providers. Your task is to analyze the provided "
            "telecom data and identify the SIM farm operation. Look for patterns "
            "in device registration, traffic volume, and network behavior."
        ),
        "sim_cards": [s.to_dict() for s in all_sims],
        "cdrs": [c.to_dict() for c in cdrs[:5000]],  # cap for performance
        "network_logs": [n.to_dict() for n in net_logs[:2000]],
        "cell_towers": [t.to_dict() for t in towers],
        "farm_sim_count": len(farm_sims),
        "legit_sim_count": len(legit_sims),
        "total_cdrs": len(cdrs),
    }
