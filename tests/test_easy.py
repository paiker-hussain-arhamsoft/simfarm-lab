"""Tests for backend.simulator.easy."""

from __future__ import annotations

from backend.simulator.easy import (
    FARM_TOWER_IDS,
    VPN_IPS,
    _generate_imei_pool,
    generate_cdrs,
    generate_legitimate_sims,
    generate_network_logs,
    generate_scenario,
    generate_sim_cards,
    get_cell_towers,
)


class TestGenerateImeiPool:
    def test_count(self):
        pool = _generate_imei_pool(10)
        assert len(pool) == 10

    def test_unique(self):
        pool = _generate_imei_pool(50)
        assert len(set(pool)) == len(pool)


class TestGenerateSimCards:
    def test_returns_tuple(self):
        result = generate_sim_cards(10)
        assert isinstance(result, tuple)
        cards, imei_map = result
        assert len(cards) == 10
        assert isinstance(imei_map, dict)

    def test_imei_rotation_map(self):
        cards, imei_map = generate_sim_cards(5)
        for card in cards:
            assert card.msisdn in imei_map
            assert len(imei_map[card.msisdn]) == 3

    def test_farm_towers(self):
        cards, _ = generate_sim_cards(20)
        for card in cards:
            assert card.cell_tower_id in FARM_TOWER_IDS
            assert card.is_sim_farm is True

    def test_vpn_ips(self):
        cards, _ = generate_sim_cards(20)
        for card in cards:
            assert card.ip_address in VPN_IPS

    def test_staggered_activation(self):
        cards, _ = generate_sim_cards(50)
        dates = {c.activation_date for c in cards}
        assert len(dates) > 1


class TestGenerateLegitSims:
    def test_count(self):
        cards = generate_legitimate_sims(10)
        assert len(cards) == 10

    def test_not_farm(self):
        cards = generate_legitimate_sims(5)
        for c in cards:
            assert c.is_sim_farm is False


class TestGenerateCdrs:
    def test_sorted(self):
        farm, imei_map = generate_sim_cards(5)
        legit = generate_legitimate_sims(5)
        cdrs = generate_cdrs(farm, legit, imei_map, hours=6)
        assert len(cdrs) > 0
        ts = [c.timestamp for c in cdrs]
        assert ts == sorted(ts)

    def test_imei_rotation_in_cdrs(self):
        farm, imei_map = generate_sim_cards(3)
        cdrs = generate_cdrs(farm, [], imei_map, hours=72)
        msisdn_imeis: dict[str, set] = {}
        for cdr in cdrs:
            msisdn_imeis.setdefault(cdr.source_msisdn, set()).add(cdr.imei)
        has_rotation = any(len(imeis) > 1 for imeis in msisdn_imeis.values())
        assert has_rotation


class TestGenerateNetworkLogs:
    def test_returns_logs(self):
        farm, _ = generate_sim_cards(35)
        logs = generate_network_logs(farm, hours=6)
        assert len(logs) > 0

    def test_sorted(self):
        farm, _ = generate_sim_cards(35)
        logs = generate_network_logs(farm, hours=6)
        ts = [l.timestamp for l in logs]
        assert ts == sorted(ts)


class TestGetCellTowers:
    def test_count(self):
        towers = get_cell_towers()
        assert len(towers) == 15


class TestGenerateScenario:
    def test_structure(self):
        s = generate_scenario()
        assert s["level"] == "easy"
        assert s["name"] == "The Hidden Network"
        assert s["imei_rotation_active"] is True
        assert isinstance(s["vpn_ips"], list)
        assert s["farm_sim_count"] == 150
        assert s["legit_sim_count"] == 100
        assert isinstance(s["detection_hints"], dict)

    def test_cdrs_capped(self):
        s = generate_scenario()
        assert len(s["cdrs"]) <= 8000
