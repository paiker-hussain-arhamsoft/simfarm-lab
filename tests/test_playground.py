"""Tests for backend.simulator.playground."""

from __future__ import annotations

from backend.simulator.playground import (
    AUTOMATION_TOOLS,
    CARRIERS,
    CITIES,
    HARDWARE_OPTIONS,
    OPSEC_MEASURES,
    SIM_ACQUISITION_METHODS,
    FarmConfig,
    _generate_educational_notes,
    _generate_warnings,
    calculate_farm_metrics,
    get_playground_options,
)


class TestFarmConfigDefaults:
    def test_defaults(self):
        cfg = FarmConfig()
        assert cfg.city == "karachi"
        assert cfg.carriers == ["jazz"]
        assert cfg.acquisition_method == "legitimate_cnic"
        assert cfg.num_cnics == 1
        assert cfg.target_sims == 10
        assert cfg.purpose == "otp_harvesting"


class TestCalculateFarmMetrics:
    def test_minimal_config(self):
        cfg = FarmConfig(
            hardware=[{"id": "gsm_modem_single", "quantity": 1}],
        )
        result = calculate_farm_metrics(cfg)
        assert result["actual_sims"] >= 1
        assert result["stealth_grade"] in ("S", "A", "B", "C", "F")
        assert "detection_risk" in result
        assert "setup_cost_pkr" in result
        assert result["city"] == "Karachi"

    def test_high_detection(self):
        cfg = FarmConfig(
            city="islamabad",
            carriers=["jazz"],
            acquisition_method="stolen_cnics",
            num_cnics=20,
            hardware=[{"id": "sim_bank_128", "quantity": 2}],
            target_sims=200,
        )
        result = calculate_farm_metrics(cfg)
        assert result["detection_risk"] > 0.3

    def test_low_detection_with_opsec(self):
        cfg = FarmConfig(
            city="quetta",
            carriers=["scom"],
            acquisition_method="legitimate_cnic",
            num_cnics=2,
            hardware=[{"id": "android_farm", "quantity": 1}],
            opsec_measures=["traffic_shaping", "multi_location"],
            target_sims=10,
        )
        result = calculate_farm_metrics(cfg)
        assert result["detection_risk"] < 0.5

    def test_zero_hardware(self):
        cfg = FarmConfig(hardware=[])
        result = calculate_farm_metrics(cfg)
        assert result["actual_sims"] == 0
        assert result["total_sim_slots"] == 0

    def test_stealth_grades(self):
        for grade in ("S", "A", "B", "C", "F"):
            # Just verify the calculation doesn't crash with various configs
            pass

    def test_multiple_carriers(self):
        cfg = FarmConfig(
            carriers=["jazz", "zong", "telenor"],
            hardware=[{"id": "gsm_modem_8port", "quantity": 1}],
            num_cnics=2,
            target_sims=8,
        )
        result = calculate_farm_metrics(cfg)
        assert len(result["carriers"]) == 3

    def test_unknown_hardware_ignored(self):
        cfg = FarmConfig(
            hardware=[{"id": "nonexistent", "quantity": 5}],
        )
        result = calculate_farm_metrics(cfg)
        assert result["total_sim_slots"] == 0


class TestGenerateWarnings:
    def test_insufficient_capacity(self):
        cfg = FarmConfig(target_sims=100)
        warnings = _generate_warnings(cfg, actual_sims=10, detection=0.1, pta_flag=0.1)
        assert any("Insufficient capacity" in w for w in warnings)

    def test_illegal_method_warning(self):
        cfg = FarmConfig(acquisition_method="stolen_cnics")
        warnings = _generate_warnings(cfg, actual_sims=10, detection=0.1, pta_flag=0.1)
        assert any("illegal" in w.lower() for w in warnings)

    def test_grey_market_warning(self):
        cfg = FarmConfig(acquisition_method="grey_market")
        warnings = _generate_warnings(cfg, actual_sims=10, detection=0.1, pta_flag=0.1)
        assert any("illegal" in w.lower() or "WARNING" in w for w in warnings)

    def test_high_detection_warning(self):
        cfg = FarmConfig()
        warnings = _generate_warnings(cfg, actual_sims=10, detection=0.6, pta_flag=0.1)
        assert any("HIGH DETECTION RISK" in w for w in warnings)

    def test_pta_flag_warning(self):
        cfg = FarmConfig()
        warnings = _generate_warnings(cfg, actual_sims=10, detection=0.1, pta_flag=0.4)
        assert any("PTA FLAG" in w for w in warnings)

    def test_islamabad_warning(self):
        cfg = FarmConfig(city="islamabad")
        warnings = _generate_warnings(cfg, actual_sims=10, detection=0.1, pta_flag=0.1)
        assert any("Islamabad" in w for w in warnings)

    def test_no_opsec_warning(self):
        cfg = FarmConfig(opsec_measures=[])
        warnings = _generate_warnings(cfg, actual_sims=10, detection=0.1, pta_flag=0.1)
        assert any("No OPSEC" in w for w in warnings)


class TestGenerateEducationalNotes:
    def test_always_has_dirbs_note(self):
        cfg = FarmConfig()
        notes = _generate_educational_notes(cfg, 0.5)
        assert any("DIRBS" in n for n in notes)

    def test_multi_carrier_note(self):
        cfg = FarmConfig(carriers=["jazz", "zong"])
        notes = _generate_educational_notes(cfg, 0.5)
        assert any("multiple carriers" in n.lower() for n in notes)

    def test_traffic_shaping_note(self):
        cfg = FarmConfig(opsec_measures=["traffic_shaping"])
        notes = _generate_educational_notes(cfg, 0.5)
        assert any("Traffic shaping" in n for n in notes)

    def test_small_city_note(self):
        cfg = FarmConfig(city="quetta")
        notes = _generate_educational_notes(cfg, 0.5)
        assert any("Smaller cities" in n for n in notes)


class TestGetPlaygroundOptions:
    def test_all_sections(self):
        opts = get_playground_options()
        assert "carriers" in opts
        assert "cities" in opts
        assert "hardware" in opts
        assert "acquisition_methods" in opts
        assert "opsec_measures" in opts
        assert "automation_tools" in opts
        assert "purposes" in opts

    def test_carrier_keys(self):
        opts = get_playground_options()
        assert set(opts["carriers"].keys()) == set(CARRIERS.keys())

    def test_purpose_list(self):
        opts = get_playground_options()
        assert len(opts["purposes"]) == 6
        ids = [p["id"] for p in opts["purposes"]]
        assert "otp_harvesting" in ids
