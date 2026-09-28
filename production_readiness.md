# VAJRA-CV Production Readiness

## Scope
This document defines the production baseline for the VAJRA-CV ML security platform.

## Deployment baseline
- API service runs from Docker or Docker Compose in an air-gapped environment.
- Runtime configuration is environment-driven.
- Production secrets are sourced from a secure secret manager and injected at runtime. Local fallback credentials are not supported.
- Model registry and audit logs are persistently stored.
- Prometheus and Grafana provide metrics and dashboards.

## Security baseline
- API keys are required for protected routes.
- Role-based access control is enforced for operator, auditor, and admin actions.
- Model uploads are validated for type and size.
- Registry entries are hashed and tracked.
- Audit events are logged for each modeled action.

## Operational baseline
- CI pipeline validates code quality and tests before release.
- Container orchestration is defined through docker-compose and environment variables.
- Logs and metrics are emitted for monitoring.
- Rollback and redeploy operations are supported through image-based deployments.

## Required secret provisioning
- Docker Compose requires `VAJRA_API_KEY`, `VAJRA_MODEL_SECRET`, and `GRAFANA_ADMIN_PASSWORD` to be set before startup.
- Kubernetes requires a `vajra-secrets` Secret containing `api-key` and `model-secret`; use an external-secrets controller or your cloud secret manager to create it.
- `VAJRA_KMS_MASTER_SECRET` is required when the local KMS abstraction is used for signing tests or air-gapped operation.

Example Kubernetes Secret creation (values are supplied interactively by the operator):

```powershell
kubectl create secret generic vajra-secrets `
	--from-literal=api-key=$env:VAJRA_API_KEY `
	--from-literal=model-secret=$env:VAJRA_MODEL_SECRET
```

## Release gate
The project should only ship when:
1. All tests pass.
2. Artifact validation is enforced.
3. Audit logging is active.
4. Signed model registry entries are preserved.
5. Deployment config is verified in CI.
