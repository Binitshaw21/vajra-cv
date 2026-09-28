import os
from dataclasses import dataclass
from typing import Iterable, Optional

from fastapi import Header, HTTPException

from engine.config import get_settings


@dataclass(frozen=True)
class AuthContext:
    api_key: str
    role: str


ROLE_ALLOWLIST = {"admin", "operator", "auditor", "viewer"}
ROLE_LEVELS = {"viewer": 10, "auditor": 20, "operator": 30, "admin": 40}


def _normalize_roles(raw_roles: Optional[str]) -> set[str]:
    if not raw_roles:
        return {"operator"}
    roles = {item.strip().lower() for item in raw_roles.split(",") if item.strip()}
    return roles & ROLE_ALLOWLIST or {"operator"}


def require_role(required_role: str = "operator"):
    def _dependency(
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
        x_role: str | None = Header(default=None, alias="X-Role"),
    ) -> AuthContext:
        settings = get_settings()
        expected_key = settings.api_key or os.getenv("VAJRA_API_KEY")
        if not settings.require_api_key:
            return AuthContext(api_key=x_api_key or "", role=(x_role or required_role).lower())
        if not expected_key:
            raise HTTPException(status_code=500, detail="API key is not configured on the server.")
        if not x_api_key or x_api_key != expected_key:
            raise HTTPException(status_code=401, detail="Invalid or missing API key.")

        role_name = os.getenv("VAJRA_API_ROLE", "operator").strip().lower()
        if role_name not in ROLE_ALLOWLIST:
            raise HTTPException(status_code=403, detail=f"Unsupported role: {role_name}")
        if required_role not in ROLE_ALLOWLIST:
            raise HTTPException(status_code=500, detail="Server misconfiguration: invalid required role.")
        if ROLE_LEVELS[role_name] < ROLE_LEVELS[required_role]:
            raise HTTPException(status_code=403, detail=f"Role '{role_name}' does not satisfy required role '{required_role}'.")
        return AuthContext(api_key=x_api_key, role=role_name)

    return _dependency


def authorize(required_role: str = "operator"):
    return require_role(required_role)
