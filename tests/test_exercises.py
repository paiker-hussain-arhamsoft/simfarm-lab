"""Tests for backend.detection.exercises."""

from __future__ import annotations

from backend.detection.exercises import (
    BEGINNER_EXERCISES,
    EASY_EXERCISES,
    LEGENDARY_EXERCISES,
    get_exercises,
    validate_flag,
)
from backend.simulator.models import Level


class TestGetExercises:
    def test_beginner(self):
        exs = get_exercises(Level.BEGINNER)
        assert len(exs) == 5
        for e in exs:
            assert e["level"] == "beginner"

    def test_easy(self):
        exs = get_exercises(Level.EASY)
        assert len(exs) == 5

    def test_legendary(self):
        exs = get_exercises(Level.LEGENDARY)
        assert len(exs) == 3

    def test_returns_dicts(self):
        for level in Level:
            exs = get_exercises(level)
            for e in exs:
                assert isinstance(e, dict)
                assert "exercise_id" in e
                assert "expected_flags" not in e


class TestValidateFlag:
    # Beginner exercises
    def test_beginner_01_correct(self):
        result = validate_flag("beginner-01", "TWR-001")
        assert result["valid"] is True
        assert result["points"] == 100

    def test_beginner_01_wrong(self):
        result = validate_flag("beginner-01", "TWR-999")
        assert result["valid"] is False

    def test_beginner_02_correct(self):
        result = validate_flag("beginner-02", "5")
        assert result["valid"] is True

    def test_beginner_03_correct(self):
        result = validate_flag("beginner-03", "3566720")
        assert result["valid"] is True

    def test_beginner_04_correct(self):
        result = validate_flag("beginner-04", "185.62.190.44")
        assert result["valid"] is True

    def test_beginner_05_correct(self):
        result = validate_flag("beginner-05", "2026-05-01")
        assert result["valid"] is True

    def test_case_insensitive(self):
        result = validate_flag("beginner-01", "twr-001")
        assert result["valid"] is True

    # Easy exercises
    def test_easy_01_partial_match(self):
        result = validate_flag("easy-01", "TWR-101, TWR-102, TWR-103")
        assert result["valid"] is True

    def test_easy_01_insufficient(self):
        result = validate_flag("easy-01", "TWR-101, TWR-102")
        assert result["valid"] is False

    def test_easy_02_dynamic(self):
        result = validate_flag("easy-02", "+12005551234")
        assert result["valid"] is True

    def test_easy_02_bad_format(self):
        result = validate_flag("easy-02", "bad")
        assert result["valid"] is False

    def test_easy_03_vpn_ips(self):
        result = validate_flag("easy-03", "104.16.51.111, 172.67.182.33")
        assert result["valid"] is True

    def test_easy_03_insufficient(self):
        result = validate_flag("easy-03", "8.8.8.8")
        assert result["valid"] is False

    def test_easy_04_correct(self):
        result = validate_flag("easy-04", "65")
        assert result["valid"] is True

    def test_easy_05_correct(self):
        result = validate_flag("easy-05", "5")
        assert result["valid"] is True

    def test_easy_05_also_4(self):
        result = validate_flag("easy-05", "4")
        assert result["valid"] is True

    # Legendary exercises
    def test_legendary_01_freeform_long(self):
        text = "a" * 60
        result = validate_flag("legendary-01", text)
        assert result["valid"] is True

    def test_legendary_01_freeform_short(self):
        result = validate_flag("legendary-01", "too short")
        assert result["valid"] is False

    def test_legendary_02_phishing(self):
        result = validate_flag("legendary-02", "anything")
        assert result["valid"] is False
        assert "Phishing Game" in result["message"]

    def test_legendary_03_graph_count_correct(self):
        result = validate_flag("legendary-03", "100")
        assert result["valid"] is True
        assert result["points"] == 300

    def test_legendary_03_graph_count_range(self):
        assert validate_flag("legendary-03", "80")["valid"] is True
        assert validate_flag("legendary-03", "125")["valid"] is True
        assert validate_flag("legendary-03", "79")["valid"] is False
        assert validate_flag("legendary-03", "126")["valid"] is False

    def test_legendary_03_graph_count_non_numeric(self):
        result = validate_flag("legendary-03", "abc")
        assert result["valid"] is False

    # Unknown exercise
    def test_unknown_exercise(self):
        result = validate_flag("nonexistent", "flag")
        assert result["valid"] is False
        assert "Unknown" in result["message"]
