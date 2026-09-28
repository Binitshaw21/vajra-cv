r"""Smoke-test a running VAJRA-CV API from a local machine.

PowerShell:
    $env:VAJRA_API_KEY = "local-api-key"
    .\venv\Scripts\python.exe tools\local_smoke_test.py --api-key $env:VAJRA_API_KEY
"""

import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def request(base_url: str, path: str, api_key: str, method: str = "GET") -> tuple[int, dict]:
    request = Request(
        f"{base_url.rstrip('/')}{path}",
        headers={"X-API-Key": api_key, "Accept": "application/json"},
        method=method,
    )
    try:
        with urlopen(request, timeout=10) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        try:
            return error.code, json.loads(body)
        except json.JSONDecodeError:
            return error.code, {"detail": body}


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test VAJRA-CV API sections")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--api-key", required=True)
    args = parser.parse_args()

    checks = [
        ("health", "/healthz", "GET", False),
        ("system status", "/api/system/status", "GET", True),
        ("ledger verification", "/api/module3/verify-ledger", "POST", True),
    ]
    failures = 0
    for name, path, method, protected in checks:
        try:
            status, body = request(args.base_url, path, args.api_key if protected else "", method)
            expected = 200
            passed = status == expected
            print(f"[{'PASS' if passed else 'FAIL'}] {name}: HTTP {status} {body}")
            failures += int(not passed)
        except URLError as error:
            print(f"[FAIL] {name}: backend unavailable: {error}")
            failures += 1

    return failures


if __name__ == "__main__":
    sys.exit(main())
