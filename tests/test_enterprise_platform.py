from engine.release import create_release_manifest, verify_release_manifest
from engine.api_gateway import healthz, metrics_endpoint


def test_release_manifest_verifies():
    manifest = create_release_manifest(
        service="VAJRA-CV",
        version="1.5.0",
        build_id="build-042",
        artifact_sha256="abc123",
    ).signed_record(secret="test-secret")
    assert verify_release_manifest(manifest, secret="test-secret") is True


def test_health_and_metrics_endpoints_are_exposed():
    health = healthz()
    metrics = metrics_endpoint()

    assert health["status"] == "ok"
    assert metrics.status_code == 200
    assert "vajra_model_scan_total" in metrics.body.decode("utf-8")
