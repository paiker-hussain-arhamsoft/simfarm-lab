"""Tests for backend.detection.engine."""

from __future__ import annotations

from backend.detection.engine import (
    ANALYSIS_TOOLS,
    _date_spread,
    analyze_activation_dates,
    analyze_contact_graph,
    analyze_imei_changes,
    analyze_imei_patterns,
    analyze_ip_distribution,
    analyze_temporal_patterns,
    analyze_tower_distribution,
    analyze_traffic_patterns,
)


def _make_sims(tower_ids: list[str], ips: list[str] | None = None) -> list[dict]:
    sims = []
    for i, tid in enumerate(tower_ids):
        sims.append({
            "cell_tower_id": tid,
            "imei": f"356672000000{i:03d}",
            "device_model": "TestPhone" if i % 2 == 0 else "OtherPhone",
            "activation_date": "2026-05-01" if i < len(tower_ids) // 2 else "2026-05-10",
            "ip_address": (ips[i] if ips else f"10.0.0.{i}"),
        })
    return sims


class TestAnalyzeTowerDistribution:
    def test_basic(self):
        sims = _make_sims(["TWR-001"] * 10 + ["TWR-002"] * 3)
        result = analyze_tower_distribution(sims)
        assert result["total_sims"] == 13
        assert result["unique_towers"] == 2
        assert result["tower_distribution"]["TWR-001"] == 10

    def test_empty(self):
        result = analyze_tower_distribution([])
        assert result["total_sims"] == 0
        assert result["unique_towers"] == 0


class TestAnalyzeImeiPatterns:
    def test_prefix_distribution(self):
        sims = _make_sims(["T"] * 5)
        result = analyze_imei_patterns(sims)
        assert result["total_sims"] == 5
        assert result["unique_imeis"] == 5
        assert result["duplicate_imeis"] == 0

    def test_duplicate_imeis(self):
        sims = [
            {"imei": "1234567890", "device_model": "A"},
            {"imei": "1234567890", "device_model": "A"},
            {"imei": "9999999999", "device_model": "B"},
        ]
        result = analyze_imei_patterns(sims)
        assert result["duplicate_imeis"] == 1


class TestAnalyzeActivationDates:
    def test_basic(self):
        sims = _make_sims(["T"] * 4)
        result = analyze_activation_dates(sims)
        assert result["total_sims"] == 4
        assert result["peak_date"] is not None
        assert result["date_spread_days"] >= 0

    def test_empty(self):
        result = analyze_activation_dates([])
        assert result["peak_date"] is None

    def test_single_date(self):
        sims = [{"activation_date": "2026-01-01"} for _ in range(5)]
        result = analyze_activation_dates(sims)
        assert result["date_spread_days"] == 0


class TestDateSpread:
    def test_zero_for_single(self):
        assert _date_spread([("2026-01-01", 5)]) == 0

    def test_correct_spread(self):
        assert _date_spread([("2026-01-01", 1), ("2026-01-11", 1)]) == 10

    def test_empty(self):
        assert _date_spread([]) == 0


class TestAnalyzeIpDistribution:
    def test_shared_ips(self):
        sims = _make_sims(
            ["T"] * 5,
            ips=["1.1.1.1", "1.1.1.1", "1.1.1.1", "2.2.2.2", "3.3.3.3"],
        )
        result = analyze_ip_distribution(sims)
        assert "1.1.1.1" in result["shared_ips"]
        assert result["shared_ips"]["1.1.1.1"] == 3
        assert result["unique_ips"] == 3
        assert result["sims_on_shared_ips"] == 3

    def test_all_unique(self):
        sims = _make_sims(["T"] * 3)
        result = analyze_ip_distribution(sims)
        assert result["shared_ips"] == {}


class TestAnalyzeTrafficPatterns:
    def test_sms_heavy(self):
        cdrs = [
            {"source_msisdn": "+1000", "traffic_type": "sms_out"} for _ in range(10)
        ]
        result = analyze_traffic_patterns(cdrs)
        assert result["sms_heavy_sims"] == 1
        assert result["total_analyzed"] == 1

    def test_balanced(self):
        cdrs = (
            [{"source_msisdn": "+1000", "traffic_type": "sms_out"}] * 3 +
            [{"source_msisdn": "+1000", "traffic_type": "voice_out"}] * 4 +
            [{"source_msisdn": "+1000", "traffic_type": "data"}] * 3
        )
        result = analyze_traffic_patterns(cdrs)
        assert result["balanced_sims"] == 1

    def test_empty(self):
        result = analyze_traffic_patterns([])
        assert result["total_analyzed"] == 0


class TestAnalyzeTemporalPatterns:
    def test_regular_sender(self):
        # Generate CDRs at exact 5-minute intervals over several hours
        cdrs = []
        for i in range(15):
            hour = i * 5 // 60
            minute = (i * 5) % 60
            cdrs.append({
                "source_msisdn": "+1000",
                "traffic_type": "sms_out",
                "timestamp": f"2026-05-15T{hour:02d}:{minute:02d}:00",
            })
        result = analyze_temporal_patterns(cdrs)
        assert result["regular_senders"] >= 1

    def test_no_sms_out(self):
        cdrs = [{"source_msisdn": "+1", "traffic_type": "voice_out", "timestamp": "2026-01-01T00:00:00"}]
        result = analyze_temporal_patterns(cdrs)
        assert result["regular_senders"] == 0

    def test_too_few_records(self):
        cdrs = [
            {"source_msisdn": "+1000", "traffic_type": "sms_out", "timestamp": f"2026-01-01T00:0{i}:00"}
            for i in range(5)
        ]
        result = analyze_temporal_patterns(cdrs)
        assert result["regular_senders"] == 0


class TestAnalyzeImeiChanges:
    def test_changers(self):
        cdrs = [
            {"source_msisdn": "+1000", "imei": "111"},
            {"source_msisdn": "+1000", "imei": "222"},
            {"source_msisdn": "+2000", "imei": "333"},
        ]
        result = analyze_imei_changes(cdrs)
        assert result["sims_with_imei_changes"] == 1
        assert result["total_analyzed"] == 2

    def test_no_changes(self):
        cdrs = [
            {"source_msisdn": "+1000", "imei": "111"},
            {"source_msisdn": "+1000", "imei": "111"},
        ]
        result = analyze_imei_changes(cdrs)
        assert result["sims_with_imei_changes"] == 0


class TestAnalyzeContactGraph:
    def test_reciprocal_network(self):
        cdrs = [
            {"source_msisdn": "+A", "destination_msisdn": "+B", "traffic_type": "sms_out"},
            {"source_msisdn": "+B", "destination_msisdn": "+A", "traffic_type": "sms_out"},
            {"source_msisdn": "+A", "destination_msisdn": "+C", "traffic_type": "sms_out"},
            {"source_msisdn": "+C", "destination_msisdn": "+A", "traffic_type": "sms_out"},
            {"source_msisdn": "+B", "destination_msisdn": "+C", "traffic_type": "sms_out"},
            {"source_msisdn": "+C", "destination_msisdn": "+B", "traffic_type": "sms_out"},
        ]
        # Need min 5 contacts to be analyzed
        for i in range(10):
            cdrs.append({"source_msisdn": "+A", "destination_msisdn": f"+X{i}", "traffic_type": "sms_out"})
            cdrs.append({"source_msisdn": f"+X{i}", "destination_msisdn": "+A", "traffic_type": "sms_out"})
        result = analyze_contact_graph(cdrs)
        assert result["subscribers_analyzed"] >= 1

    def test_star_network_suspicious(self):
        # One sender contacting many unique targets with no replies
        cdrs = []
        for i in range(20):
            cdrs.append({
                "source_msisdn": "+FARM",
                "destination_msisdn": f"+TARGET{i}",
                "traffic_type": "sms_out",
            })
        result = analyze_contact_graph(cdrs)
        if result["subscribers_analyzed"] > 0:
            assert result["low_reciprocity_count"] >= 1

    def test_ignores_data_traffic(self):
        cdrs = [
            {"source_msisdn": "+A", "destination_msisdn": "", "traffic_type": "data"}
            for _ in range(20)
        ]
        result = analyze_contact_graph(cdrs)
        assert result["subscribers_analyzed"] == 0

    def test_empty(self):
        result = analyze_contact_graph([])
        assert result["subscribers_analyzed"] == 0


class TestAnalysisToolsRegistry:
    def test_all_tools_registered(self):
        expected = {
            "tower_distribution", "imei_patterns", "activation_dates",
            "ip_distribution", "traffic_patterns", "temporal_patterns",
            "imei_changes", "contact_graph",
        }
        assert set(ANALYSIS_TOOLS.keys()) == expected

    def test_all_callable(self):
        for name, fn in ANALYSIS_TOOLS.items():
            assert callable(fn)
