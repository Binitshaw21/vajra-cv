# VAJRA-CV

## Air-gapped AI assurance for models you can trust

VAJRA-CV is a security-first computer-vision assurance platform for checking model integrity, poisoned features, backdoor risk, provenance, environmental drift, and edge inference commitments before deployment.

It combines a FastAPI control plane with a responsive React console built for local, air-gapped, and enterprise evaluation workflows.

> **Demo status:** This repository includes deterministic fixtures so reviewers can see clean, flagged, rejected, healed, and tampered outcomes locally.

## What It Checks

| Area | Console section | Example result |
| --- | --- | --- |
| Feature poisoning | Poison scrubber | `SAFE` / `FLAGGED` |
| Model backdoors | Trojan hunter | `CERTIFIED_CLEAN` / `FLAGGED_TROJAN` |
| Memory integrity | ECC monitor | protected weight verification |
| Environment shift | Self-healing | entropy improvement |
| Provenance | Audit ledger | `INTACT` / `COMPROMISED` |
| Frame commitments | Audit ledger | `COMMITMENT_RECORDED` |

## Product Flow

```text
Landing page -> Sign in -> Command center -> Upload artifact -> Review verdict
```

The interface supports day mode and night mode, responsive navigation, a profile menu, desktop/tablet/phone layouts, and clear failure states.

## Quick Start

### 1. Install backend dependencies

PowerShell:

```powershell
Set-Location "C:\Users\YOUR_USER\vajra-cv"
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 2. Start the backend

Use local demo credentials only. Never use these values in production.

```powershell
Set-Location "C:\Users\YOUR_USER\vajra-cv"
$env:VAJRA_API_KEY = "local-api-key"
$env:VAJRA_MODEL_SECRET = "local-model-secret"
$env:VAJRA_KMS_MASTER_SECRET = "local-kms-secret"
$env:VAJRA_API_ROLE = "admin"
$env:VAJRA_LEDGER_DB = "data/ledger_intact.db"
$env:VAJRA_PROVENANCE_KEY_PATH = "data/ledger_intact.key"

.\venv\Scripts\python.exe -m uvicorn engine.api_gateway:app --host 127.0.0.1 --port 8000
```

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/healthz
```

### 3. Start the frontend

Open a second terminal:

```powershell
Set-Location "C:\Users\YOUR_USER\vajra-cv\ui"
npm install
npm run dev
```

Open `http://127.0.0.1:5173/`.

## Demo Login

The local demo login requires all three values:

| Field | Demo value |
| --- | --- |
| Username / email | `admin@vajra.local` |
| Password | Any password with 8 or more characters, for example `local-password` |
| API key | `local-api-key` |

The login screen is a local demo gate. Production deployments should connect it to an OIDC/SSO provider and inject API credentials through a secret manager.

## Demo Fixtures

Generate all local fixtures:

```powershell
Set-Location "C:\Users\YOUR_USER\vajra-cv"
python tools/generate_feature_fixtures.py
python tools/generate_trojan_fixtures.py
python tools/generate_tta_fixtures.py
python tools/generate_frame_fixture.py
python tools/generate_ledger_fixtures.py
```

### Feature poisoning

In **Poison scrubber**, upload:

```text
data/features_safe.npy       -> CLEAN
data/features_flagged.npy    -> COMPROMISED / flagged samples
data/features_invalid.npy    -> HTTP 400 rejected safely
```

### Trojan Hunter

In **Trojan hunter**, upload:

```text
models/model_safe.pth           -> CERTIFIED_CLEAN
models/model_flagged_trojan.pth -> FLAGGED_TROJAN / class 2
```

### Self-healing

In **Self-healing**, upload:

```text
data/tta_nominal.npy
data/tta_drifted.npy
```

The result reports `SELF_HEALING_COMPLETE`, initial entropy, final entropy, and adaptation improvement.

### Audit ledger

In **Audit ledger**, the intact fixture reports `INTACT`:

```powershell
$env:VAJRA_LEDGER_DB = "data/ledger_intact.db"
$env:VAJRA_PROVENANCE_KEY_PATH = "data/ledger_intact.key"
```

The tampered fixture reports `COMPROMISED` at block 1:

```powershell
$env:VAJRA_LEDGER_DB = "data/ledger_tampered.db"
$env:VAJRA_PROVENANCE_KEY_PATH = "data/ledger_tampered.key"
```

Restart the backend after changing either variable, then click the ledger refresh control.

### Real frame commitment

In **Audit ledger**, upload:

```text
data/sample_inference_frame.png
```

The current local implementation records a SHA-256-bound `COMMITMENT_RECORDED` result. It does not claim a real zk-SNARK/PLONK proof until a production proving backend is configured.

## Testing

Run the full backend suite:

```powershell
Set-Location "C:\Users\YOUR_USER\vajra-cv"
$env:VAJRA_MODEL_SECRET = "test-model-secret"
$env:VAJRA_KMS_MASTER_SECRET = "test-kms-secret"
.\venv\Scripts\python.exe -m pytest -q
```

Run the section-level API tests:

```powershell
.\venv\Scripts\python.exe -m pytest tests/test_api_sections.py -q
```

Run the live API smoke test:

```powershell
.\venv\Scripts\python.exe tools/local_smoke_test.py --api-key local-api-key
```

Build the frontend:

```powershell
Set-Location "C:\Users\YOUR_USER\vajra-cv\ui"
npm run build
```

## Security Notes

- Protected API routes require `X-API-Key`.
- API roles are server-authoritative through `VAJRA_API_ROLE`; client role headers do not elevate privileges.
- PyTorch uploads use safe tensor-only deserialization and an allow-listed demo architecture.
- Invalid feature uploads fail closed instead of falling back to demo data.
- Signing secrets must be injected from a secret manager in production.
- Keep the provenance private key and ledger database together across restarts.
- Docker and Kubernetes deployment hardening is documented in [production_readiness.md](production_readiness.md).

## Repository Layout

```text
core/       Detection and assurance modules
engine/     API, auth, registry, signing, metrics, and runtime controls
ui/         React/Vite product console and Tauri shell
tools/      Reproducible local demo fixture generators and smoke tests
tests/      Backend and API regression tests
k8s/        Kubernetes deployment baseline
monitoring/ Prometheus configuration
```

## License

See the repository licensing terms before redistributing this project.
