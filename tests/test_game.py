"""Tests for backend.phishing.game."""

from __future__ import annotations

from backend.phishing.game import (
    EVIDENCE_CATALOG,
    NPC_PROFILES,
    GameState,
    _evaluate_email_quality,
    create_game_session,
    get_company_directory,
    get_game_status,
    send_phishing_email,
    submit_final_report,
)


class TestEvaluateEmailQuality:
    def test_baseline(self):
        score = _evaluate_email_quality("Subject", "Body text", "pretext")
        assert 0.0 <= score <= 1.0

    def test_personalization_bonus(self):
        s1 = _evaluate_email_quality("S", "Generic body that is long enough to measure.", "p")
        s2 = _evaluate_email_quality("S", "I love your work on the project, and your role is amazing.", "p")
        assert s2 > s1

    def test_professional_length_bonus(self):
        short = _evaluate_email_quality("S", "Hi.", "p")
        good = _evaluate_email_quality("Re: Follow-up", "I wanted to reach out regarding your team's recent work. " * 3 + "Thanks.", "security_audit")
        assert good > short

    def test_all_caps_penalty(self):
        normal = _evaluate_email_quality("S", "Please review this document at your convenience.", "p")
        caps = _evaluate_email_quality("S", "PLEASE REVIEW THIS DOCUMENT at your convenience.", "p")
        assert caps < normal

    def test_generic_greeting_penalty(self):
        normal = _evaluate_email_quality("S", "Hi Viktor, I wanted to discuss your project.", "p")
        generic = _evaluate_email_quality("S", "Dear Sir/Madam, I wanted to discuss.", "p")
        assert generic < normal

    def test_bounded(self):
        score = _evaluate_email_quality(
            "Re: Urgent follow-up",
            "I love your work and your role in the team. Please review ASAP. " * 10,
            "security_audit_pretext_long_enough",
        )
        assert score <= 1.0

        score = _evaluate_email_quality("", "x", "")
        assert score >= 0.0


class TestCreateGameSession:
    def test_returns_state(self):
        state = create_game_session()
        assert isinstance(state, GameState)
        assert len(state.session_id) > 0
        assert state.attempts == []
        assert state.evidence_collected == []
        assert state.score == 0
        assert state.game_over is False
        assert state.max_attempts == 8


class TestSendPhishingEmail:
    def _fresh_state(self) -> GameState:
        return create_game_session()

    def test_unknown_target(self):
        state = self._fresh_state()
        result = send_phishing_email(
            state, "nobody@example.com", "Hi", "Body", "Alias", "pretext"
        )
        assert result["success"] is False
        assert "bounced" in result["response"]

    def test_game_over_state(self):
        state = self._fresh_state()
        state.game_over = True
        result = send_phishing_email(
            state, "j.park@novacomdigital.com", "Hi", "Body", "A", "p"
        )
        assert result["game_over"] is True

    def test_max_attempts_reached(self):
        state = self._fresh_state()
        state.max_attempts = 0
        result = send_phishing_email(
            state, "j.park@novacomdigital.com", "Hi", "Body", "A", "p"
        )
        assert result["game_over"] is True

    def test_ceo_always_detects(self):
        state = self._fresh_state()
        result = send_phishing_email(
            state, "e.rossi@novacomdigital.com", "Hi", "Nice body.", "A", "p"
        )
        assert result["success"] is False
        assert state.detected is True
        assert len(state.messages) > 0

    def test_detection_triggers(self):
        state = self._fresh_state()
        result = send_phishing_email(
            state, "j.park@novacomdigital.com",
            "Police investigation",
            "We are conducting a police investigation into your arrest.",
            "Agent", "police",
        )
        assert result["success"] is False
        assert "suspicious" in result["response"].lower() or "tip" in result

    def test_successful_phish_james(self):
        state = self._fresh_state()
        result = send_phishing_email(
            state,
            "j.park@novacomdigital.com",
            "Re: Mentorship opportunity at Google",
            "I love your work on your project. Your role at NovaCom is exactly the kind of experience we look for. I'd like to mentor you on your team's architecture.",
            "Senior Engineer at Google",
            "mentorship",
        )
        assert result["success"] is True
        assert len(result.get("evidence_obtained", [])) > 0

    def test_neutral_response(self):
        state = self._fresh_state()
        result = send_phishing_email(
            state,
            "e.rossi@novacomdigital.com",
            "Hello",
            "Hi.",
            "Random Person",
            "random",
        )
        # CEO always detects
        assert result["success"] is False
        assert result.get("game_over") is False

    def test_attempt_tracking(self):
        state = self._fresh_state()
        send_phishing_email(state, "j.park@novacomdigital.com", "S", "B", "A", "p")
        send_phishing_email(state, "j.park@novacomdigital.com", "S", "B", "A", "p")
        assert len(state.attempts) == 2


class TestGetCompanyDirectory:
    def test_returns_list(self):
        directory = get_company_directory()
        assert len(directory) == 5
        names = {d["name"] for d in directory}
        assert "James Park" in names
        assert "Elena Rossi" in names

    def test_structure(self):
        for entry in get_company_directory():
            assert "name" in entry
            assert "role" in entry
            assert "email" in entry
            assert "social_media_hint" in entry


class TestGetGameStatus:
    def test_initial(self):
        state = create_game_session()
        status = get_game_status(state)
        assert status["attempts_used"] == 0
        assert status["attempts_remaining"] == 8
        assert status["can_submit_report"] is False
        assert status["score"] == 0

    def test_after_collecting_evidence(self):
        state = create_game_session()
        state.evidence_collected = [
            {"name": "A", "type": "critical"},
            {"name": "B", "type": "high"},
        ]
        status = get_game_status(state)
        assert status["critical_evidence"] == 1
        assert status["total_evidence"] == 2
        assert status["can_submit_report"] is True


class TestSubmitFinalReport:
    def test_insufficient_evidence(self):
        state = create_game_session()
        result = submit_final_report(state, "Some report")
        assert result["accepted"] is False

    def test_accepted_report(self):
        state = create_game_session()
        state.evidence_collected = [
            {"name": "SIM Inventory Spreadsheet", "type": "critical", "points": 250},
            {"name": "Client Invoice", "type": "high", "points": 150},
        ]
        state.score = 400
        report = (
            "NovaCom Digital Solutions is operating a SIM farm with 100 lines "
            "at 1847 Industrial Parkway in Long Island City. They service "
            "BulkVerify LLC for SMS verification using SMPP."
        )
        result = submit_final_report(state, report)
        assert result["accepted"] is True
        assert result["grade"] in ("S", "A", "B", "C")
        assert result["total_score"] > 0
        assert len(result["findings_identified"]) > 0
        assert state.game_over is True

    def test_low_score_report(self):
        state = create_game_session()
        state.evidence_collected = [
            {"name": "A", "type": "critical"},
            {"name": "B", "type": "high"},
        ]
        state.score = 50
        result = submit_final_report(state, "vague report about something suspicious")
        assert result["accepted"] is True
        assert result["grade"] == "C"
