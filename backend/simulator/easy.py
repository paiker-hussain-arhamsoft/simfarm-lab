"""Easy level SIM farm simulator — 'The Hidden Network'.

More sophisticated SIM farm that requires statistical analysis:
- SIMs distributed across multiple cell towers
- Staggered activation over 2 weeks
- Mixed traffic types (voice + SMS + data)
- IMEI rotation every 48 hours
- Multiple IPs via VPN
- Behavioral variation in timing
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

CITY_TOWERS = [
    CellTower("TWR-101", 40.7128, -74.0060, "Financial District", "A"),
    CellTower("TWR-102", 40.7580, -73.9855, "Midtown West", "B"),
    CellTower("TWR-103", 40.7484, -73.9857, "Murray Hill", "A"),
    CellTower("TWR-104", 40.7306, -73.9352, "East Village", "C"),
    CellTower("TWR-105", 40.6892, -74.0445, "Red Hook", "B"),
    CellTower("TWR-106", 40.7614, -73.9776, "Rockefeller", "A"),
    CellTower("TWR-107", 40.7282, -73.7949, "Queens Hub", "B"),
    CellTower("TWR-108", 40.6501, -73.9496, "Flatbush", "C"),
    CellTower("TWR-109", 40.8448, -73.8648, "Bronx Central", "A"),
    CellTower("TWR-110", 40.5795, -74.1502, "Staten Island", "B"),
    CellTower("TWR-111", 40.7489, -73.9680, "Grand Central", "A"),
    CellTower("TWR-112", 40.6782, -73.9442, "Crown Heights", "C"),
    CellTower("TWR-113", 40.7061, -73.9969, "Chinatown", "B"),
    CellTower("TWR-114", 40.7831, -73.9712, "Upper West Side", "A"),
    CellTower("TWR-115", 40.7736, -73.9566, "Lenox Hill", "B"),
]

# Farm uses a subset of towers (clusters)
FARM_TOWER_IDS = [t.tower_id for t in CITY_TOWERS[:8]]

VPN_IPS = [
    "104.16.51.111", "172.67.182.33", "198.41.215.9",
    "104.21.44.72", "172.67.139.88", "104.16.52.222",
    "198.41.216.77", "172.67.201.15",
]

DEVICE_MODELS = [
    "Samsung Galaxy A13", "Samsung Galaxy A14", "Xiaomi Redmi 10",
    "Xiaomi Redmi Note 11", "Motorola Moto G22", "Nokia G21",
    "Realme C35", "OPPO A57", "Tecno Spark 9",
]

LEGIT_MODELS = [
    "iPhone 15 Pro Max", "Samsung Galaxy S24 Ultra", "Google Pixel 8 Pro",
    "iPhone 14", "Samsung Galaxy S23", "OnePlus 12",
    "iPhone 13 mini", "Google Pixel 7a",
]


def _generate_imei_pool(count: int) -> list[str]:
    """Pre-generate IMEI pool for rotation."""
    return [f"{random.randint(35000000, 35999999)}{random.randint(1000000, 9999999)}" for _ in range(count)]


def generate_sim_cards(count: int = 150) -> tuple[list[SIMCard], dict]:
    """Generate farm SIMs with staggered activation and tower distribution."""
    cards: list[SIMCard] = []
    imei_pool = _generate_imei_pool(count * 3)  # 3x for rotation
    imei_rotation_map: dict[str, list[str]] = {}

    base_activation = datetime(2026, 5, 1)
    for i in range(count):
        # Stagger activation over 14 days
        activation_offset = random.randint(0, 13)
        activation = base_activation + timedelta(days=activation_offset)

        # Distribute across farm towers (not evenly — some clustering)
        tower_id = random.choice(FARM_TOWER_IDS)

        # Each SIM gets 3 IMEIs for rotation
        sim_imeis = imei_pool[i * 3:(i + 1) * 3]
        msisdn = random_us_msisdn()
        imei_rotation_map[msisdn] = sim_imeis

        cards.append(
            SIMCard(
                iccid=f"8901260{random.randint(10**12, 10**13-1)}",
                msisdn=msisdn,
                imsi=f"310260{random.randint(10**8, 10**9-1)}",
                imei=sim_imeis[0],  # current IMEI
                activation_date=activation.strftime("%Y-%m-%d"),
                cell_tower_id=tower_id,
                ip_address=random.choice(VPN_IPS),
                device_model=random.choice(DEVICE_MODELS),
                is_sim_farm=True,
                metadata={"activation_batch": activation_offset // 3},
            )
        )

    return cards, imei_rotation_map


def generate_legitimate_sims(count: int = 100) -> list[SIMCard]:
    cards: list[SIMCard] = []
    all_towers = [t.tower_id for t in CITY_TOWERS]
    for i in range(count):
        activation = datetime(2025, 1, 1) + timedelta(days=random.randint(0, 500))
        cards.append(
            SIMCard(
                iccid=f"8901550{random.randint(10**12, 10**13-1)}",
                msisdn=random_us_msisdn(),
                imsi=f"310550{random.randint(10**8, 10**9-1)}",
                imei=f"{random.randint(10**14, 10**15-1)}",
                activation_date=activation.strftime("%Y-%m-%d"),
                cell_tower_id=random.choice(all_towers),
                ip_address=random_public_ipv4(),
                device_model=random.choice(LEGIT_MODELS),
                is_sim_farm=False,
            )
        )
    return cards


def generate_cdrs(
    farm_sims: list[SIMCard],
    legit_sims: list[SIMCard],
    imei_map: dict[str, list[str]],
    hours: int = 72,
) -> list[CDR]:
    records: list[CDR] = []
    base_time = datetime(2026, 5, 15, 0, 0, 0)

    # Farm traffic: varied intervals, mixed types, IMEI rotation
    for sim in farm_sims:
        imeis = imei_map.get(sim.msisdn, [sim.imei])
        num_events = random.randint(20, 80)

        for j in range(num_events):
            ts = random_timestamp(base_time, hours)
            # Rotate IMEI every ~48h
            hour_offset = (ts - base_time).total_seconds() / 3600
            imei_idx = min(int(hour_offset / 48), len(imeis) - 1)
            current_imei = imeis[imei_idx]

            # Mostly SMS but some voice/data to look more legit
            traffic = random.choices(
                [TrafficType.SMS_OUT, TrafficType.VOICE_OUT, TrafficType.DATA],
                weights=[0.65, 0.15, 0.20],
            )[0]

            duration = 0
            data_bytes = 0
            sms_hash = ""
            if traffic == TrafficType.VOICE_OUT:
                duration = random.randint(5, 120)  # short calls
            elif traffic == TrafficType.DATA:
                data_bytes = random.randint(512, 500_000)
            else:
                content = f"VERIFY-{random.randint(100000,999999)}"
                sms_hash = sms_content_hash(content)

            # Occasionally switch VPN IP
            ip = random.choice(VPN_IPS) if random.random() < 0.3 else sim.ip_address

            records.append(
                CDR(
                    record_id=str(uuid.uuid4()),
                    timestamp=ts.isoformat(),
                    source_msisdn=sim.msisdn,
                    destination_msisdn=random_us_msisdn(),
                    traffic_type=traffic,
                    duration_seconds=duration,
                    cell_tower_id=sim.cell_tower_id,
                    imei=current_imei,
                    ip_address=ip,
                    data_bytes=data_bytes,
                    sms_content_hash=sms_hash,
                    metadata={"vpn_detected": ip in VPN_IPS},
                )
            )

    # Legitimate traffic
    for sim in legit_sims:
        num_events = random.randint(10, 60)
        for _ in range(num_events):
            ts = random_timestamp(base_time, hours)
            traffic = random.choices(
                [TrafficType.SMS_OUT, TrafficType.SMS_IN, TrafficType.VOICE_OUT,
                 TrafficType.VOICE_IN, TrafficType.DATA],
                weights=[0.15, 0.15, 0.20, 0.15, 0.35],
            )[0]
            duration = random.randint(15, 900) if "voice" in traffic.value else 0
            data_bytes = random.randint(1024, 50_000_000) if traffic == TrafficType.DATA else 0

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
    hours: int = 72,
) -> list[NetworkLog]:
    base_time = datetime(2026, 5, 15, 0, 0, 0)
    logs: list[NetworkLog] = []

    sms_gateways = ["10.0.0.1", "10.0.0.2", "10.0.1.1"]
    vpn_endpoints = ["45.33.32.156", "45.33.32.157"]

    for sim in farm_sims[:30]:
        num_logs = random.randint(10, 50)
        for _ in range(num_logs):
            ts = random_timestamp(base_time, hours, with_seconds=False)
            # Mix of SMPP and VPN tunnel traffic
            if random.random() < 0.6:
                dest = random.choice(sms_gateways)
                port = 2775
            else:
                dest = random.choice(vpn_endpoints)
                port = random.choice([1194, 443, 51820])

            logs.append(
                NetworkLog(
                    timestamp=ts.isoformat(),
                    source_ip=sim.ip_address,
                    dest_ip=dest,
                    protocol=random.choice(["TCP", "UDP"]),
                    port=port,
                    payload_size=random.randint(64, 4096),
                    flags="PSH,ACK" if port == 2775 else "SYN",
                )
            )

    return sort_by_timestamp(logs)


def get_cell_towers() -> list[CellTower]:
    return CITY_TOWERS


def generate_scenario() -> dict:
    farm_sims, imei_map = generate_sim_cards(150)
    legit_sims = generate_legitimate_sims(100)
    all_sims = farm_sims + legit_sims
    random.shuffle(all_sims)

    cdrs = generate_cdrs(farm_sims, legit_sims, imei_map, hours=72)
    net_logs = generate_network_logs(farm_sims, hours=72)
    towers = get_cell_towers()

    return {
        "level": Level.EASY.value,
        "name": "The Hidden Network",
        "description": (
            "Intelligence suggests a SIM farm is operating in the metropolitan area. "
            "The operators have taken steps to avoid detection — SIMs are spread across "
            "multiple towers, IMEIs are rotated, and VPNs mask their traffic. "
            "You'll need statistical analysis and correlation to find them."
        ),
        "briefing": (
            "CLASSIFIED BRIEF: Multiple telecom providers have reported anomalous but "
            "individually inconclusive patterns. The suspected farm uses IMEI rotation, "
            "VPN tunneling, and distributed tower registration. Standard pattern matching "
            "won't cut it. Apply statistical clustering, temporal analysis, and cross-reference "
            "SIM-to-IMEI mappings to uncover the operation."
        ),
        "sim_cards": [s.to_dict() for s in all_sims],
        "cdrs": [c.to_dict() for c in cdrs[:8000]],
        "network_logs": [n.to_dict() for n in net_logs[:3000]],
        "cell_towers": [t.to_dict() for t in towers],
        "farm_sim_count": len(farm_sims),
        "legit_sim_count": len(legit_sims),
        "total_cdrs": len(cdrs),
        "imei_rotation_active": True,
        "vpn_ips": VPN_IPS,
        "detection_hints": {
            "clustering": "Group SIMs by activation date batches",
            "imei_anomaly": "Track IMEI changes per MSISDN over time",
            "traffic_ratio": "Compare SMS-to-voice ratio against baseline",
            "ip_correlation": "Identify shared VPN exit nodes",
            "tower_density": "Map SIM concentration per tower vs population density",
        },
    }
