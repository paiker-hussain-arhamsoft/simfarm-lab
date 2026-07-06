"""Tests for backend.legendary.detection_scenarios."""

from __future__ import annotations

from backend.legendary.detection_scenarios import (
    SCENARIOS,
    check_answer,
    get_all_scenarios,
    get_scenario_detail,
)


class TestScenarioData:
    def test_scenarios_not_empty(self):
        assert len(SCENARIOS) > 0

    def test_all_have_required_fields(self):
        for s in SCENARIOS:
            assert s.id
            assert s.title
            assert s.difficulty in ("intermediate", "advanced", "expert")
            assert s.briefing
            assert s.context
            assert len(s.evidence) > 0
            assert len(s.questions) > 0


class TestGetAllScenarios:
    def test_returns_list(self):
        result = get_all_scenarios()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_entry_shape(self):
        for entry in get_all_scenarios():
            assert "id" in entry
            assert "title" in entry
            assert "difficulty" in entry
            assert "category" in entry


class TestGetScenarioDetail:
    def test_valid_scenario(self):
        detail = get_scenario_detail("DS-001")
        assert detail is not None
        assert detail["id"] == "DS-001"
        assert "evidence" in detail
        assert "questions" in detail

    def test_unknown_scenario(self):
        assert get_scenario_detail("NONEXISTENT") is None


class TestCheckAnswer:
    def test_correct_multiple_choice(self):
        result = check_answer(
            "DS-001", "DS-001-Q1",
            "The consistent 60-120 minute delay and 3.2s average interval between engagements",
        )
        assert result["correct"] is True
        assert result["points_earned"] > 0

    def test_wrong_multiple_choice(self):
        result = check_answer("DS-001", "DS-001-Q1", "wrong answer")
        assert result["correct"] is False

    def test_free_text_with_keywords(self):
        result = check_answer(
            "DS-001", "DS-001-Q5",
            "We recommend engagement_velocity_limits, content_similarity_scoring, and cib_takedown.",
        )
        assert result["correct"] is True

    def test_free_text_no_keywords(self):
        result = check_answer("DS-001", "DS-001-Q5", "no relevant keywords here")
        assert result["correct"] is False

    def test_unknown_scenario(self):
        result = check_answer("NONE", "Q1", "ans")
        assert "error" in result

    def test_unknown_question(self):
        result = check_answer("DS-001", "NONEXISTENT", "ans")
        assert "error" in result
