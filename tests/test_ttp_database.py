"""Tests for backend.legendary.ttp_database."""

from __future__ import annotations

from backend.legendary.ttp_database import (
    TTP_DATABASE,
    get_all_ttps,
    get_categories,
    get_ttp_by_id,
    get_ttps_by_category,
)


class TestTTPDatabase:
    def test_not_empty(self):
        assert len(TTP_DATABASE) > 0

    def test_all_have_ids(self):
        for entry in TTP_DATABASE:
            assert entry.id.startswith("SF-T")
            assert entry.name
            assert entry.category
            assert entry.summary


class TestGetAllTTPs:
    def test_returns_list(self):
        result = get_all_ttps()
        assert isinstance(result, list)
        assert len(result) == len(TTP_DATABASE)

    def test_entry_shape(self):
        for entry in get_all_ttps():
            assert "id" in entry
            assert "name" in entry
            assert "category" in entry


class TestGetCategories:
    def test_returns_categories(self):
        cats = get_categories()
        assert isinstance(cats, list)
        assert len(cats) > 0

    def test_category_shape(self):
        for cat in get_categories():
            assert "id" in cat
            assert "name" in cat
            assert "count" in cat
            assert cat["count"] > 0


class TestGetTTPById:
    def test_valid_id(self):
        ttp = get_ttp_by_id("SF-T1001")
        assert ttp is not None
        assert ttp["id"] == "SF-T1001"
        assert "name" in ttp

    def test_unknown_id(self):
        assert get_ttp_by_id("NONEXISTENT") is None


class TestGetTTPsByCategory:
    def test_valid_category(self):
        result = get_ttps_by_category("infrastructure")
        assert isinstance(result, list)
        assert len(result) > 0
        for entry in result:
            assert entry["category"] == "infrastructure"

    def test_empty_category(self):
        result = get_ttps_by_category("nonexistent_category")
        assert result == []
