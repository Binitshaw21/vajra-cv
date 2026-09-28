import os

import pytest
from fastapi.testclient import TestClient

from engine.api_gateway import app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("VAJRA_API_KEY", "local-test-key")
    monkeypatch.setenv("VAJRA_API_ROLE", "operator")
    return TestClient(app)


def test_health_section_is_public(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_system_status_requires_api_key(client):
    response = client.get("/api/system/status", headers={"X-API-Key": "local-test-key"})
    assert response.status_code == 200
    assert response.json()["status"] == "SECURE"


def test_client_cannot_escalate_role_with_header(client):
    response = client.post(
        "/api/sota/self-heal",
        headers={"X-API-Key": "local-test-key", "X-Role": "admin"},
    )
    assert response.status_code == 403


def test_poison_scan_rejects_malformed_upload(client):
    response = client.post(
        "/api/module1/svd-scan",
        headers={"X-API-Key": "local-test-key"},
        files={"features": ("features.csv", b"not,a,numeric,array", "text/csv")},
    )
    assert response.status_code == 400


def test_ledger_section_returns_integrity_status(client):
    response = client.post(
        "/api/module3/verify-ledger",
        headers={"X-API-Key": "local-test-key"},
    )
    assert response.status_code == 200
    assert response.json()["integrity_status"] in {"INTACT", "COMPROMISED"}


def test_missing_api_key_is_rejected(client):
    response = client.get("/api/system/status")
    assert response.status_code == 401
