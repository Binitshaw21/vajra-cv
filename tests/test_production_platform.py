from engine.config import Settings, get_settings


def test_default_settings_are_production_ready():
    settings = get_settings(
        app_name="VAJRA-CV",
        environment="production",
        api_key="demo-prod-key",
        require_api_key=True,
    )

    assert isinstance(settings, Settings)
    assert settings.app_name == "VAJRA-CV"
    assert settings.environment == "production"
    assert settings.api_key == "demo-prod-key"
    assert settings.require_api_key is True
    assert len(settings.cors_origins) >= 2


def test_settings_validate_runtime_requirements():
    settings = get_settings(
        app_name="VAJRA-CV",
        environment="production",
        max_model_bytes=512 * 1024 * 1024,
        allowed_model_formats=[".pth", ".pt", ".onnx"],
    )

    assert settings.max_model_bytes > 0
    assert ".pth" in settings.allowed_model_formats
    assert ".onnx" in settings.allowed_model_formats
    assert settings.backend_host == "0.0.0.0"
