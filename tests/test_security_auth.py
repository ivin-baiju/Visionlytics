"""
Tests for security, authentication, RBAC, and Supabase integration.
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from api.security import hash_password, verify_password, create_access_token, decode_access_token, sanitize_string


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_password_hashing():
    raw = "SuperSecret123!"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_flow():
    payload = {"sub": "analyst1", "role": "analyst", "email": "analyst1@visionlytics.ai"}
    token = create_access_token(payload)
    decoded = decode_access_token(token)
    assert decoded["sub"] == "analyst1"
    assert decoded["role"] == "analyst"


def test_input_sanitization():
    dirty = "<script>alert('xss')</script>Hello <b>World</b>\x00"
    clean = sanitize_string(dirty)
    assert "<script>" not in clean
    assert "&lt;script&gt;" in clean
    assert "\x00" not in clean


def test_login_flow(client):
    # Test seeded default admin
    res = client.post("/auth/login", json={"username": "admin", "password": "Visionlytics@Admin2026!"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["role"] == "admin"


def test_login_invalid_credentials(client):
    res = client.post("/auth/login", json={"username": "admin", "password": "WrongPassword!"})
    assert res.status_code == 401


def test_admin_route_protection_unauthenticated(client):
    res = client.get("/admin/users")
    assert res.status_code == 401


def test_admin_route_protection_forbidden_for_standard_user(client):
    # Log in as testuser (role='user')
    res_login = client.post("/auth/login", json={"username": "testuser", "password": "UserPass2026!"})
    assert res_login.status_code == 200
    token = res_login.json()["access_token"]

    # Attempt to access admin endpoint
    res = client.get("/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403


def test_admin_route_accessible_by_admin(client):
    # Log in as admin
    res_login = client.post("/auth/login", json={"username": "admin", "password": "Visionlytics@Admin2026!"})
    assert res_login.status_code == 200
    token = res_login.json()["access_token"]

    res = client.get("/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert "users" in res.json()


def test_security_headers_present(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.headers["X-Content-Type-Options"] == "nosniff"
    assert res.headers["X-Frame-Options"] == "DENY"
    assert "Strict-Transport-Security" in res.headers
    assert "Content-Security-Policy" in res.headers


def test_consent_record_endpoint(client):
    res = client.post("/consent/record", json={"consent_type": "cookie_banner", "analytics_allowed": False})
    assert res.status_code == 200
    assert res.json()["status"] == "recorded"
