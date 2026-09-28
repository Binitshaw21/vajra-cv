from engine.api_gateway import app
from engine.security import ROLE_LEVELS


def test_security_headers_present():
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.get('/healthz')
    assert response.status_code == 200
    assert 'Strict-Transport-Security' in response.headers
    assert 'X-Content-Type-Options' in response.headers
    assert 'X-Frame-Options' in response.headers


def test_rbac_roles_are_hierarchical():
    assert ROLE_LEVELS["admin"] > ROLE_LEVELS["operator"] > ROLE_LEVELS["viewer"]
