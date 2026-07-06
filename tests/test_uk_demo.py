"""Tests for backend.simulator.uk_demo."""

from __future__ import annotations

from backend.simulator.uk_demo import (
    DEMO_SCENARIOS,
    SOCIAL_PLATFORMS,
    UK_AUTOMATION,
    UK_CARRIERS,
    UK_CITIES,
    UK_HARDWARE,
    UK_OPSEC,
    UK_SIM_ACQUISITION,
    _generate_uk_legal_notes,
    _generate_uk_warnings,
    build_uk_farm,
    calculate_uk_demo_metrics,
    generate_simulation_events,
    get_uk_demo_scenarios,
    get_uk_playground_options,
)


# ── Constants ────────────────────────────────────────────────────────

class TestConstants:
    def test_carriers_have_required_keys(self):
        for cid, c in UK_CARRIERS.items():
            assert "name" in c
            assert "mcc_mnc" in c
            assert c["id_required"] is False  # UK has no mandatory SIM registration

    def test_cities_have_required_keys(self):
        for city_id, city in UK_CITIES.items():
            assert "name" in city
            assert "country" in city
            assert city["country"] in ("England", "Wales", "Scotland")
            assert city["towers"] > 0

    def test_hardware_sim_capacity(self):
        for hw_id, hw in UK_HARDWARE.items():
            assert hw["sim_capacity"] > 0
            assert hw["cost_gbp"] >= 0
            assert 0 < hw["detectability"] <= 1.0

    def test_acquisition_methods(self):
        for k, v in UK_SIM_ACQUISITION.items():
            assert v["sims_per_trip"] > 0
            assert v["cost_multiplier"] > 0

    def test_opsec_effectiveness_bounded(self):
        for k, v in UK_OPSEC.items():
            assert 0 < v["effectiveness"] <= 1.0

    def test_demo_scenarios_exist(self):
        assert "labour_ge_2024" in DEMO_SCENARIOS
        assert "reform_local_2026" in DEMO_SCENARIOS


# ── calculate_uk_demo_metrics ────────────────────────────────────────

class TestCalculateUKDemoMetrics:
    def test_labour_scenario(self):
        result = calculate_uk_demo_metrics("labour_ge_2024")
        assert result["scenario_id"] == "labour_ge_2024"
        assert result["party"] == "Labour Party"
        assert result["total_sims"] > 0
        assert result["total_accounts"] > 0
        assert result["stealth_grade"] in ("S", "A", "B", "C", "F")
        assert "warnings" in result
        assert "legal_notes" in result

    def test_reform_scenario(self):
        result = calculate_uk_demo_metrics("reform_local_2026")
        assert result["scenario_id"] == "reform_local_2026"
        assert result["party"] == "Reform UK"
        assert result["total_sims"] > 0

    def test_unknown_scenario(self):
        result = calculate_uk_demo_metrics("nonexistent")
        assert "error" in result

    def test_cost_breakdown(self):
        result = calculate_uk_demo_metrics("labour_ge_2024")
        assert result["hardware_cost_gbp"] > 0
        assert result["sim_cost_gbp"] > 0
        assert result["monthly_operating_cost_gbp"] > 0
        assert result["total_campaign_cost_gbp"] > 0

    def test_detection_fields(self):
        result = calculate_uk_demo_metrics("reform_local_2026")
        assert 0 < result["network_detection_risk"] < 1
        assert 0 < result["platform_detection_risk"] < 1
        assert result["electoral_commission_risk"] > 0
        assert result["estimated_detection_timeline"]

    def test_campaign_reach(self):
        result = calculate_uk_demo_metrics("labour_ge_2024")
        assert result["daily_posts"] > 0
        assert result["daily_impressions"] > 0
        assert result["total_campaign_impressions"] > 0


# ── _generate_uk_warnings ────────────────────────────────────────────

class TestGenerateUKWarnings:
    def test_insufficient_hardware(self):
        config = {"num_sims": 100, "opsec": ["account_aging", "residential_proxies"], "platforms": ["x_twitter", "facebook", "tiktok"]}
        warnings = _generate_uk_warnings(config, actual_sims=10, risk=0.1, ec_risk=0.1, scenario={"id": "test"})
        assert any("Insufficient" in w for w in warnings)

    def test_high_risk_warning(self):
        config = {"num_sims": 10, "opsec": ["account_aging", "residential_proxies"], "platforms": ["x_twitter", "facebook", "tiktok"]}
        warnings = _generate_uk_warnings(config, actual_sims=10, risk=0.5, ec_risk=0.1, scenario={"id": "test"})
        assert any("HIGH COMBINED RISK" in w for w in warnings)

    def test_ec_scrutiny_warning(self):
        config = {"num_sims": 10, "opsec": ["account_aging", "residential_proxies"], "platforms": ["x_twitter", "facebook", "tiktok"]}
        warnings = _generate_uk_warnings(config, actual_sims=10, risk=0.1, ec_risk=0.3, scenario={"id": "test"})
        assert any("Electoral Commission" in w for w in warnings)

    def test_no_account_aging(self):
        config = {"num_sims": 10, "opsec": ["residential_proxies"], "platforms": ["x_twitter", "facebook", "tiktok"]}
        warnings = _generate_uk_warnings(config, actual_sims=10, risk=0.1, ec_risk=0.1, scenario={"id": "test"})
        assert any("account aging" in w.lower() for w in warnings)

    def test_no_residential_proxies(self):
        config = {"num_sims": 10, "opsec": ["account_aging"], "platforms": ["x_twitter", "facebook", "tiktok"]}
        warnings = _generate_uk_warnings(config, actual_sims=10, risk=0.1, ec_risk=0.1, scenario={"id": "test"})
        assert any("proxy" in w.lower() for w in warnings)

    def test_few_platforms(self):
        config = {"num_sims": 10, "opsec": ["account_aging", "residential_proxies"], "platforms": ["x_twitter"]}
        warnings = _generate_uk_warnings(config, actual_sims=10, risk=0.1, ec_risk=0.1, scenario={"id": "test"})
        assert any("fewer than 3" in w for w in warnings)


# ── _generate_uk_legal_notes ─────────────────────────────────────────

class TestGenerateUKLegalNotes:
    def test_common_notes(self):
        notes = _generate_uk_legal_notes({"id": "test"})
        assert len(notes) >= 5
        assert any("SIM registration" in n for n in notes)
        assert any("Online Safety Act" in n for n in notes)

    def test_labour_specific_notes(self):
        notes = _generate_uk_legal_notes({"id": "labour_ge_2024"})
        assert any("2024 UK General Election" in n for n in notes)

    def test_reform_specific_notes(self):
        notes = _generate_uk_legal_notes({"id": "reform_local_2026"})
        assert any("Local elections" in n for n in notes)
        assert any("Wales" in n for n in notes)


# ── get_uk_demo_scenarios ────────────────────────────────────────────

class TestGetUKDemoScenarios:
    def test_returns_all_sections(self):
        result = get_uk_demo_scenarios()
        assert "scenarios" in result
        assert "carriers" in result
        assert "cities" in result
        assert "platforms" in result
        assert "regulatory_context" in result

    def test_scenario_list(self):
        result = get_uk_demo_scenarios()
        ids = [s["id"] for s in result["scenarios"]]
        assert "labour_ge_2024" in ids
        assert "reform_local_2026" in ids


# ── get_uk_playground_options ────────────────────────────────────────

class TestGetUKPlaygroundOptions:
    def test_all_sections(self):
        opts = get_uk_playground_options()
        assert "carriers" in opts
        assert "cities" in opts
        assert "hardware" in opts
        assert "acquisition_methods" in opts
        assert "opsec_measures" in opts
        assert "automation_tools" in opts
        assert "platforms" in opts

    def test_carrier_details(self):
        opts = get_uk_playground_options()
        for cid, c in opts["carriers"].items():
            assert "name" in c
            assert "sms_rate_gbp" in c


# ── build_uk_farm ────────────────────────────────────────────────────

class TestBuildUKFarm:
    def test_basic_build(self):
        result = build_uk_farm({
            "name": "Test Op",
            "city": "cardiff",
            "carriers": ["giffgaff", "three"],
            "acquisition_method": "payg_walk_in",
            "hardware": [{"id": "android_farm_10", "quantity": 2}],
            "opsec_measures": ["residential_proxies", "account_aging"],
            "platforms": ["x_twitter", "facebook"],
            "target_sims": 20,
        })
        assert result["farm_name"] == "Test Op"
        assert result["city"] == "Cardiff"
        assert result["total_sims"] == 20
        assert result["total_sim_slots"] == 20
        assert result["total_accounts"] == 40  # 20 sims * 2 platforms
        assert result["stealth_grade"] in ("S", "A", "B", "C", "F")

    def test_no_hardware(self):
        result = build_uk_farm({"hardware": []})
        assert result["total_sims"] == 0
        assert result["total_sim_slots"] == 0

    def test_no_opsec_warnings(self):
        result = build_uk_farm({
            "hardware": [{"id": "android_farm_10", "quantity": 1}],
            "target_sims": 5,
        })
        assert any("No OPSEC" in w for w in result["warnings"])

    def test_insufficient_capacity(self):
        result = build_uk_farm({
            "hardware": [{"id": "android_farm_10", "quantity": 1}],
            "target_sims": 100,
        })
        assert result["total_sims"] == 10
        assert any("Insufficient" in w for w in result["warnings"])

    def test_unknown_hardware_ignored(self):
        result = build_uk_farm({
            "hardware": [{"id": "fake_device", "quantity": 5}],
            "target_sims": 10,
        })
        assert result["total_sim_slots"] == 0


# ── generate_simulation_events ───────────────────────────────────────

class TestGenerateSimulationEvents:
    def test_labour_events(self):
        events = generate_simulation_events("labour_ge_2024")
        assert len(events) == 200
        phases = {e["phase"] for e in events}
        assert "manual_setup" in phases
        assert "initial_automation" in phases
        assert "full_automation" in phases

    def test_reform_events(self):
        events = generate_simulation_events("reform_local_2026")
        assert len(events) == 200

    def test_unknown_scenario(self):
        events = generate_simulation_events("nonexistent")
        assert events == []

    def test_event_structure(self):
        events = generate_simulation_events("labour_ge_2024")
        for e in events:
            assert "id" in e
            assert "phase" in e
            assert "time_offset_s" in e
            assert "type" in e
            assert "title" in e
            assert "detail" in e
            assert "metric_deltas" in e

    def test_time_offsets_increasing(self):
        events = generate_simulation_events("reform_local_2026")
        offsets = [e["time_offset_s"] for e in events]
        assert offsets == sorted(offsets)
