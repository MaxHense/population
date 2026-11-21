"""CORS origins come only from CORS_ORIGINS (comma separated). Unset = no cross-origin access."""
import importlib

import pytest
from fastapi.testclient import TestClient

import app.main

FRONTEND = "https://population.example.org"


@pytest.fixture
def client_with(monkeypatch):
    def build(origins):
        if origins is None:
            monkeypatch.delenv("CORS_ORIGINS", raising=False)
        else:
            monkeypatch.setenv("CORS_ORIGINS", origins)
        return TestClient(importlib.reload(app.main).app)  # middleware is set up at import
    yield build
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    importlib.reload(app.main)


def preflight(client, origin):
    return client.options("/", headers={
        "Origin": origin,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
    })


def test_configured_origin_is_allowed(client_with):
    response = preflight(client_with(FRONTEND), FRONTEND)
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == FRONTEND
    assert "content-type" in response.headers["access-control-allow-headers"].lower()


def test_several_origins_with_spaces(client_with):
    client = client_with(f"http://localhost:5173, {FRONTEND}")
    assert preflight(client, FRONTEND).headers["access-control-allow-origin"] == FRONTEND
    assert preflight(client, "http://localhost:5173").headers["access-control-allow-origin"] == "http://localhost:5173"


def test_other_origin_is_not_allowed(client_with):
    response = preflight(client_with(FRONTEND), "https://evil.example.com")
    assert "access-control-allow-origin" not in response.headers


@pytest.mark.parametrize("origins", [None, ""])
def test_no_cross_origin_access_by_default(client_with, origins):
    response = preflight(client_with(origins), "http://localhost:5173")
    assert "access-control-allow-origin" not in response.headers
