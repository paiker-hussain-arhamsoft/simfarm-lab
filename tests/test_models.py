"""Tests for backend.simulator.models."""

from __future__ import annotations

from backend.simulator.models import (
    CDR,
    CellTower,
    Exercise,
    Level,
    NetworkLog,
    SIMCard,
    TrafficType,
)


class TestLevel:
    def test_values(self):
        assert Level.BEGINNER.value == "beginner"
        assert Level.EASY.value == "easy"
        assert Level.LEGENDARY.value == "legendary"

    def test_from_string(self):
        assert Level("beginner") is Level.BEGINNER
        assert Level("easy") is Level.EASY
        assert Level("legendary") is Level.LEGENDARY


class TestTrafficType:
    def test_values(self):
        assert TrafficType.SMS_OUT.value == "sms_out"
        assert TrafficType.SMS_IN.value == "sms_in"
        assert TrafficType.VOICE_OUT.value == "voice_out"
        assert TrafficType.VOICE_IN.value == "voice_in"
        assert TrafficType.DATA.value == "data"


class TestSIMCard:
    def test_defaults(self):
        card = SIMCard(
            iccid="iccid1",
            msisdn="+15550000001",
            imsi="imsi1",
            imei="imei1",
            activation_date="2026-01-01",
            cell_tower_id="TWR-001",
            ip_address="1.2.3.4",
            device_model="TestPhone",
        )
        assert card.is_sim_farm is True
        assert card.metadata == {}

    def test_to_dict_excludes_is_sim_farm(self):
        card = SIMCard(
            iccid="iccid1",
            msisdn="+15550000001",
            imsi="imsi1",
            imei="imei1",
            activation_date="2026-01-01",
            cell_tower_id="TWR-001",
            ip_address="1.2.3.4",
            device_model="TestPhone",
            is_sim_farm=False,
        )
        d = card.to_dict()
        assert "is_sim_farm" not in d
        assert d["iccid"] == "iccid1"
        assert d["msisdn"] == "+15550000001"
        assert d["imei"] == "imei1"
        assert d["metadata"] == {}

    def test_to_dict_includes_metadata(self):
        card = SIMCard(
            iccid="i", msisdn="m", imsi="s", imei="e",
            activation_date="d", cell_tower_id="t", ip_address="ip",
            device_model="dm", metadata={"key": "value"},
        )
        assert card.to_dict()["metadata"] == {"key": "value"}


class TestCDR:
    def test_to_dict(self):
        cdr = CDR(
            record_id="r1",
            timestamp="2026-01-01T00:00:00",
            source_msisdn="+1000",
            destination_msisdn="+2000",
            traffic_type=TrafficType.SMS_OUT,
            duration_seconds=0,
            cell_tower_id="TWR-001",
            imei="imei1",
            ip_address="1.2.3.4",
        )
        d = cdr.to_dict()
        assert d["traffic_type"] == "sms_out"
        assert d["duration_seconds"] == 0
        assert d["data_bytes"] == 0
        assert d["sms_content_hash"] == ""

    def test_voice_cdr(self):
        cdr = CDR(
            record_id="r2",
            timestamp="2026-01-01T00:00:00",
            source_msisdn="+1000",
            destination_msisdn="+2000",
            traffic_type=TrafficType.VOICE_OUT,
            duration_seconds=120,
            cell_tower_id="TWR-001",
            imei="imei1",
            ip_address="1.2.3.4",
        )
        assert cdr.to_dict()["duration_seconds"] == 120


class TestCellTower:
    def test_to_dict(self):
        tower = CellTower("TWR-001", 40.7, -74.0, "Test Tower", "A")
        d = tower.to_dict()
        assert d["tower_id"] == "TWR-001"
        assert d["lat"] == 40.7
        assert d["lon"] == -74.0
        assert d["name"] == "Test Tower"
        assert d["sector"] == "A"


class TestNetworkLog:
    def test_to_dict(self):
        log = NetworkLog(
            timestamp="2026-01-01T00:00:00",
            source_ip="10.0.0.1",
            dest_ip="10.0.0.2",
            protocol="TCP",
            port=80,
            payload_size=1024,
        )
        d = log.to_dict()
        assert d["flags"] == ""
        assert d["metadata"] == {}
        assert d["port"] == 80

    def test_with_flags(self):
        log = NetworkLog(
            timestamp="t", source_ip="s", dest_ip="d",
            protocol="TCP", port=443, payload_size=100,
            flags="PSH,ACK",
        )
        assert log.to_dict()["flags"] == "PSH,ACK"


class TestExercise:
    def test_to_dict_excludes_expected_flags(self):
        ex = Exercise(
            exercise_id="ex-01",
            level=Level.BEGINNER,
            title="Test Exercise",
            description="desc",
            objective="obj",
            hints=["hint1"],
            expected_flags=["FLAG"],
            points=100,
        )
        d = ex.to_dict()
        assert "expected_flags" not in d
        assert d["exercise_id"] == "ex-01"
        assert d["level"] == "beginner"
        assert d["points"] == 100
        assert d["hints"] == ["hint1"]
