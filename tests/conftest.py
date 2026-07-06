"""Shared fixtures for SimFarm Lab tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture()
def client():
    """FastAPI test client."""
    return TestClient(app)
