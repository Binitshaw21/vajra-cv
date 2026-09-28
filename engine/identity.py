import base64
import hashlib
import hmac
import json
from datetime import datetime, timezone


def validate_jwt_claims(token: str, issuer: str, audience: str, secret: str) -> dict:
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
        if not (header_b64 and payload_b64 and signature_b64):
            raise ValueError("Malformed JWT")
        header = json.loads(base64.urlsafe_b64decode(header_b64 + "=" * (-len(header_b64) % 4)))
        payload = json.loads(base64.urlsafe_b64decode(payload_b64 + "=" * (-len(payload_b64) % 4)))
        if header.get("alg") != "HS256":
            raise ValueError("Unsupported JWT algorithm")
        expected = hmac.new(secret.encode("utf-8"), f"{header_b64}.{payload_b64}".encode("ascii"), hashlib.sha256).digest()
        supplied = base64.urlsafe_b64decode(signature_b64 + "=" * (-len(signature_b64) % 4))
        if not hmac.compare_digest(supplied, expected):
            raise ValueError("Invalid JWT signature")
    except Exception as exc:  # pragma: no cover - defensive boundary
        raise ValueError(f"Invalid JWT: {exc}") from exc

    if payload.get("iss") != issuer:
        raise ValueError("Invalid issuer")
    audiences = payload.get("aud", [])
    audiences = audiences if isinstance(audiences, list) else [audiences]
    if audience not in audiences:
        raise ValueError("Invalid audience")
    if payload.get("exp", 0) < int(datetime.now(timezone.utc).timestamp()):
        raise ValueError("JWT expired")
    if "roles" not in payload or not isinstance(payload["roles"], list):
        raise ValueError("JWT missing roles")
    return payload
