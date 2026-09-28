import base64
import json
import os
from datetime import datetime, timedelta, timezone

from engine.artifacts import ArtifactRegistry
from engine.kms import KMSProvider
from engine.identity import validate_jwt_claims


def _jwt(payload: dict, secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    enc = lambda part: base64.urlsafe_b64encode(json.dumps(part, separators=(",", ":")).encode()).rstrip(b"=").decode()
    signing_input = f"{enc(header)}.{enc(payload)}".encode()
    sig = __import__("hmac").new(secret.encode(), signing_input, __import__("hashlib").sha256).digest()
    return f"{enc(header)}.{enc(payload)}.{base64.urlsafe_b64encode(sig).rstrip(b'=').decode()}"


def test_kms_provider_sign_and_verify():
    os.environ["VAJRA_KMS_MASTER_SECRET"] = "enterprise-kms-secret"
    provider = KMSProvider(kms_key_id="kv-prod-01")
    payload = b"model-release:artifact-42"
    signature = provider.sign(payload)
    assert provider.verify(payload, signature) is True
    assert provider.key_id == "kv-prod-01"


def test_jwt_claim_validation_enforces_role():
    secret = "idp-rotating-secret"
    token = _jwt({
        "sub": "svc-ops",
        "iss": "https://login.example.com",
        "aud": "vajra-enterprise",
        "roles": ["operator", "auditor"],
        "exp": int((datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp()),
    }, secret)
    claims = validate_jwt_claims(token, issuer="https://login.example.com", audience="vajra-enterprise", secret=secret)
    assert claims["roles"] == ["operator", "auditor"]
    assert "operator" in claims["roles"]


def test_jwt_claim_validation_rejects_tampered_signature():
    token = _jwt({"iss": "issuer", "aud": "aud", "roles": ["viewer"], "exp": int((datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp())}, "secret")
    tampered = f"{token[:-1]}{'a' if token[-1] != 'a' else 'b'}"
    try:
        validate_jwt_claims(tampered, issuer="issuer", audience="aud", secret="secret")
    except ValueError as exc:
        assert "signature" in str(exc).lower()
    else:
        raise AssertionError("tampered JWT was accepted")


def test_artifact_registry_retention_prunes_expired_items():
    registry = ArtifactRegistry(storage_path="data/test_artifact_registry.json", retention_days=30)
    old = {"sha256": "old-artifact", "created_at": (datetime.now(timezone.utc) - timedelta(days=45)).isoformat()}
    new = {"sha256": "new-artifact", "created_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()}
    registry.add(old)
    registry.add(new)
    pruned = registry.prune_expired()
    assert "old-artifact" in pruned
    assert "new-artifact" not in pruned
