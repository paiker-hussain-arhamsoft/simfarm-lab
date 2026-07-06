"""Tests for backend.simulator.beginner."""

from __future__ import annotations

from backend.simulator.beginner import (
    ACTIVATION_DATE,
    FARM_IP,
    FARM_TOWER,
    _generate_msisdn,
    _seq_imei,
    generate_cdrs,
    generate_legitimate_sims,
    generate_network_logs,
    generate_scenario,
    generate_sim_cards,
    get_cell_towers,
)
from backend.simulator.models import TrafficType


class TestSeqImei:
    def test_length(self):
        imei = _seq_imei(0)
        assert len(imei) == 15

    def test_sequential(self):
        imei0 = _seq_imei(0)
        imei1 = _seq_imei(1)
        assert imei0 != imei1
        assert imei0.startswith("3566720")


class TestGenerateMsisdn:
    def test_format(self):
        msisdn = _generate_msisdn(0)
        assert msisdn.startswith("+1555")
        assert len(msisdn) == 12


class TestGenerateSimCards:
    def test_default_count(self):
        cards = generate_sim_cards()
        assert len(cards) == 200

    def test_custom_count(self):
        cards = generate_sim_cards(10)
        assert len(cards) == 10

    def test_all_on_farm_tower(self):
        cards = generate_sim_cards(5)
        for card in cards:
            assert card.cell_tower_id == FARM_TOWER.tower_id
            assert card.ip_address == FARM_IP
            assert card.activation_date == ACTIVATION_DATE
            assert card.is_sim_farm is True


class TestGenerateLegitSims:
    def test_default_count(self):
        cards = generate_legitimate_sims()
        assert len(cards) == 50

    def test_not_sim_farm(self):
        cards = generate_legitimate_sims(5)
        for card in cards:
            assert card.is_sim_farm is False

    def test_varied_towers(self):
        cards = generate_legitimate_sims(20)
        towers = {c.cell_tower_id for c in cards}
        assert len(towers) > 1


class TestGenerateCdrs:
    def test_returns_sorted_records(self):
        farm = generate_sim_cards(2)
        legit = generate_legitimate_sims(2)
        cdrs = generate_cdrs(farm, legit, hours=1)
        assert len(cdrs) > 0
        timestamps = [c.timestamp for c in cdrs]
        assert timestamps == sorted(timestamps)

    def test_farm_traffic_is_sms_out(self):
        farm = generate_sim_cards(2)
        cdrs = generate_cdrs(farm, [], hours=1)
        for cdr in cdrs:
            assert cdr.traffic_type == TrafficType.SMS_OUT


class TestGenerateNetworkLogs:
    def test_returns_logs(self):
        farm = generate_sim_cards(25)
        logs = generate_network_logs(farm, hours=1)
        assert len(logs) > 0

    def test_sorted(self):
        farm = generate_sim_cards(25)
        logs = generate_network_logs(farm, hours=1)
        timestamps = [l.timestamp for l in logs]
        assert timestamps == sorted(timestamps)


class TestGetCellTowers:
    def test_includes_farm_tower(self):
        towers = get_cell_towers()
        ids = [t.tower_id for t in towers]
        assert "TWR-001" in ids
        assert len(towers) == 5


class TestGenerateScenario:
    def test_scenario_structure(self):
        scenario = generate_scenario()
        assert scenario["level"] == "beginner"
        assert scenario["name"] == "The Obvious Farm"
        assert "sim_cards" in scenario
        assert "cdrs" in scenario
        assert "network_logs" in scenario
        assert "cell_towers" in scenario
        assert scenario["farm_sim_count"] == 200
        assert scenario["legit_sim_count"] == 50

    def test_sim_cards_are_dicts(self):
        scenario = generate_scenario()
        for sim in scenario["sim_cards"][:3]:
            assert isinstance(sim, dict)
            assert "iccid" in sim

    def test_cdrs_capped(self):
        scenario = generate_scenario()
        assert len(scenario["cdrs"]) <= 5000
