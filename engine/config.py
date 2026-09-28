from dataclasses import dataclass, field
import os
from typing import List, Optional


@dataclass
class Settings:
    app_name: str = "VAJRA-CV"
    environment: str = "production"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    api_key: Optional[str] = None
    require_api_key: bool = True
    cors_origins: List[str] = field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "tauri://localhost",
        ]
    )
    allowed_model_formats: List[str] = field(default_factory=lambda: [".pth", ".pt", ".onnx"])
    max_model_bytes: int = 512 * 1024 * 1024
    log_level: str = "INFO"

    def validate(self) -> None:
        if not self.app_name:
            raise ValueError("app_name cannot be empty")
        if self.backend_port <= 0:
            raise ValueError("backend_port must be positive")
        if self.max_model_bytes <= 0:
            raise ValueError("max_model_bytes must be positive")
        if not self.allowed_model_formats:
            raise ValueError("allowed_model_formats cannot be empty")
        if "*" in self.cors_origins:
            raise ValueError("wildcard CORS is not allowed")


def get_settings(
    app_name: str = "VAJRA-CV",
    environment: str = "production",
    backend_host: str = "0.0.0.0",
    backend_port: int = 8000,
    api_key: Optional[str] = None,
    require_api_key: bool = True,
    cors_origins: Optional[List[str]] = None,
    allowed_model_formats: Optional[List[str]] = None,
    max_model_bytes: int = 512 * 1024 * 1024,
    log_level: str = "INFO",
) -> Settings:
    configured_origins = os.getenv("VAJRA_CORS_ORIGINS")
    configured_formats = os.getenv("VAJRA_MODEL_FORMATS")
    settings = Settings(
        app_name=os.getenv("VAJRA_APP_NAME", app_name),
        environment=os.getenv("VAJRA_ENVIRONMENT", environment),
        backend_host=os.getenv("VAJRA_BACKEND_HOST", backend_host),
        backend_port=int(os.getenv("VAJRA_BACKEND_PORT", backend_port)),
        api_key=api_key or os.getenv("VAJRA_API_KEY"),
        require_api_key=os.getenv("VAJRA_REQUIRE_API_KEY", str(require_api_key)).lower() == "true",
        cors_origins=cors_origins or (configured_origins.split(",") if configured_origins else [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "tauri://localhost",
        ]),
        allowed_model_formats=allowed_model_formats or (configured_formats.split(",") if configured_formats else [".pth", ".pt", ".onnx"]),
        max_model_bytes=int(os.getenv("VAJRA_MAX_MODEL_BYTES", max_model_bytes)),
        log_level=os.getenv("VAJRA_LOG_LEVEL", log_level),
    )
    settings.validate()
    return settings
