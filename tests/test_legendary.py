"""Tests for backend.simulator.legendary."""

from __future__ import annotations

from backend.simulator.legendary import (
    METRO_TOWERS,
    PERSONAS,
    _build_communities,
    _generate_residential_ip,
    _generate_unique_imei,
    _is_active_hour,
    _poisson_interval,
    generate_cdrs,
    generate_legitimate_sims,
    generate_network_logs,
    generate_scenario,
    generate_sim_cards,
    get_insider_evidence,
)


class TestPoissonInterval:
    def test_positive(self):
        for _ in range(20):
            val = _poisson_interval(1.0)
            assert val > 0

    def test_higher_rate_shorter_intervals(self):
        low_rate = [_poisson_interval(0.1) for _ in range(200)]
        high_rate = [_poisson_interval(10.0) for _ in range(200)]
        assert sum(low_rate) / len(low_rate) > sum(high_rate) / len(high_rate)


class TestIsActiveHour:
    def test_normal_range(self):
        assert _is_active_hour(10, 8, 20) is True
        assert _is_active_hour(7, 8, 20) is False
        assert _is_active_hour(20, 8, 20) is False

    def test_wrapping_midnight(self):
        assert _is_active_hour(23, 22, 6) is True
        assert _is_active_hour(2, 22, 6) is True
        assert _is_active_hour(10, 22, 6) is False


class TestGenerateUniqueImei:
    def test_length(self):
        imei = _generate_unique_imei()
        assert len(imei) == 15

    def test_uniqueness(self):
        imeis = {_generate_unique_imei() for _ in range(100)}
        assert len(imeis) >= 90  # very high chance of uniqueness


class TestGenerateResidentialIp:
    def test_format(self):
        ip = _generate_residential_ip()
        parts = ip.split(".")
        assert len(parts) == 4

    def test_uniqueness(self):
        ips = {_generate_residential_ip() for _ in range(50)}
        assert len(ips) >= 40


class TestGenerateSimCards:
    def test_default_count(self):
        cards = generate_sim_cards()
        assert len(cards) == 100

    def test_unique_ips(self):
        cards = generate_sim_cards(20)
        ips = [c.ip_address for c in cards]
        assert len(set(ips)) == len(ips)

    def test_persona_metadata(self):
        cards = generate_sim_cards(5)
        for card in cards:
            assert "persona" in card.metadata
            assert "home_tower" in card.metadata
            assert "work_tower" in card.metadata

    def test_all_farm(self):
        cards = generate_sim_cards(5)
        for c in cards:
            assert c.is_sim_farm is True


class TestGenerateLegitSims:
    def test_count(self):
        cards = generate_legitimate_sims(10)
        assert len(cards) == 10

    def test_not_farm(self):
        for c in generate_legitimate_sims(5):
            assert c.is_sim_farm is False


class TestBuildCommunities:
    def test_returns_map(self):
        sims = generate_sim_cards(30)
        contacts = _build_communities(sims)
        assert isinstance(contacts, dict)
        assert len(contacts) > 0

    def test_peers_exclude_self(self):
        sims = generate_sim_cards(20)
        contacts = _build_communities(sims)
        for msisdn, peers in contacts.items():
            assert msisdn not in peers


class TestGenerateCdrs:
    def test_returns_sorted(self):
        farm = generate_sim_cards(5)
        legit = generate_legitimate_sims(5)
        cdrs = generate_cdrs(farm, legit, hours=24)
        assert len(cdrs) > 0
        ts = [c.timestamp for c in cdrs]
        assert ts == sorted(ts)


class TestGenerateNetworkLogs:
    def test_returns_logs(self):
        farm = generate_sim_cards(5)
        legit = generate_legitimate_sims(5)
        logs = generate_network_logs(farm, legit, hours=24)
        assert len(logs) > 0


class TestGetInsiderEvidence:
    def test_structure(self):
        ev = get_insider_evidence()
        assert ev["company_name"] == "NovaCom Digital Solutions"
        assert len(ev["key_personnel"]) == 5
        assert len(ev["internal_documents"]) == 4
        assert "evidence_threshold" in ev


class TestGenerateScenario:
    def test_structure(self):
        s = generate_scenario()
        assert s["level"] == "legendary"
        assert s["name"] == "The Ghost Farm"
        assert s["farm_sim_count"] == 100
        assert s["legit_sim_count"] == 150
        assert "insider_evidence" in s
        assert "detection_note" in s

    def test_cdrs_capped(self):
        s = generate_scenario()
        assert len(s["cdrs"]) <= 15000
