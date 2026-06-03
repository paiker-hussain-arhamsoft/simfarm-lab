"""Data models for SIM farm simulation."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class Level(str, Enum):
    BEGINNER = "beginner"
    EASY = "easy"
    LEGENDARY = "legendary"


class TrafficType(str, Enum):
    SMS_OUT = "sms_out"
    SMS_IN = "sms_in"
    VOICE_OUT = "voice_out"
    VOICE_IN = "voice_in"
    DATA = "data"


@dataclass
class SIMCard:
    iccid: str
    msisdn: str  # phone number
    imsi: str
    imei: str
    activation_date: str
    cell_tower_id: str
    ip_address: str
    device_model: str
    is_sim_farm: bool = True
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "iccid": self.iccid,
            "msisdn": self.msisdn,
            "imsi": self.imsi,
            "imei": self.imei,
            "activation_date": self.activation_date,
            "cell_tower_id": self.cell_tower_id,
            "ip_address": self.ip_address,
            "device_model": self.device_model,
            "metadata": self.metadata,
        }


@dataclass
class CDR:
    """Call Detail Record."""
    record_id: str
    timestamp: str
    source_msisdn: str
    destination_msisdn: str
    traffic_type: TrafficType
    duration_seconds: int  # 0 for SMS
    cell_tower_id: str
    imei: str
    ip_address: str
    data_bytes: int = 0
    sms_content_hash: str = ""
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "timestamp": self.timestamp,
            "source_msisdn": self.source_msisdn,
            "destination_msisdn": self.destination_msisdn,
            "traffic_type": self.traffic_type.value,
            "duration_seconds": self.duration_seconds,
            "cell_tower_id": self.cell_tower_id,
            "imei": self.imei,
            "ip_address": self.ip_address,
            "data_bytes": self.data_bytes,
            "sms_content_hash": self.sms_content_hash,
            "metadata": self.metadata,
        }


@dataclass
class CellTower:
    tower_id: str
    lat: float
    lon: float
    name: str
    sector: str

    def to_dict(self) -> dict:
        return {
            "tower_id": self.tower_id,
            "lat": self.lat,
            "lon": self.lon,
            "name": self.name,
            "sector": self.sector,
        }


@dataclass
class NetworkLog:
    timestamp: str
    source_ip: str
    dest_ip: str
    protocol: str
    port: int
    payload_size: int
    flags: str = ""
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "source_ip": self.source_ip,
            "dest_ip": self.dest_ip,
            "protocol": self.protocol,
            "port": self.port,
            "payload_size": self.payload_size,
            "flags": self.flags,
            "metadata": self.metadata,
        }


@dataclass
class Exercise:
    exercise_id: str
    level: Level
    title: str
    description: str
    objective: str
    hints: list[str]
    expected_flags: list[str]
    points: int
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "exercise_id": self.exercise_id,
            "level": self.level.value,
            "title": self.title,
            "description": self.description,
            "objective": self.objective,
            "hints": self.hints,
            "points": self.points,
        }
