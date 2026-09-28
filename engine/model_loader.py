import hashlib
import io
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
import torch


@dataclass
class ModelArtifact:
    """Normalized metadata for an uploaded or local ML model artifact."""
    filename: str
    extension: str
    sha256: str
    size_bytes: int
    format_name: str
    valid: bool
    warning: Optional[str] = None


def classify_model_type(filename: str) -> str:
    lower = (filename or "").lower()
    if lower.endswith((".pth", ".pt")):
        return "pytorch"
    if lower.endswith(".onnx"):
        return "onnx"
    raise ValueError(f"Unsupported model format: {filename}")


def compute_sha256(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()


def validate_artifact_bytes(file_bytes: bytes, filename: str, max_bytes: int = 512 * 1024 * 1024) -> ModelArtifact:
    if not file_bytes:
        raise ValueError("Artifact is empty.")
    if len(file_bytes) > max_bytes:
        raise ValueError(f"Artifact exceeds maximum allowed size of {max_bytes} bytes.")

    extension = Path(filename).suffix.lower()
    if extension not in {".pth", ".pt", ".onnx"}:
        raise ValueError("Unsupported model format. Allowed: .pth, .pt, .onnx")

    artifact = ModelArtifact(
        filename=filename,
        extension=extension,
        sha256=compute_sha256(file_bytes),
        size_bytes=len(file_bytes),
        format_name=classify_model_type(filename),
        valid=True,
    )
    return artifact


def _load_pytorch_module(file_bytes: bytes) -> Any:
    try:
        buffer = io.BytesIO(file_bytes)
        obj = torch.load(buffer, map_location="cpu", weights_only=True)
    except Exception as exc:  # pragma: no cover - defensive fallback
        raise ValueError(f"Could not deserialize PyTorch model artifact: {exc}") from exc

    if isinstance(obj, dict):
        architecture = obj.get("architecture")
        state_dict = obj.get("state_dict")
        if architecture == "vajra_demo_classifier" and isinstance(state_dict, dict):
            model = torch.nn.Sequential(
                torch.nn.Flatten(),
                torch.nn.Linear(3 * 32 * 32, 64),
                torch.nn.ReLU(),
                torch.nn.Linear(64, 4),
            )
            try:
                model.load_state_dict(state_dict, strict=True)
            except (RuntimeError, TypeError) as exc:
                raise ValueError(f"Demo classifier state dictionary is invalid: {exc}") from exc
            return model
    raise ValueError("PyTorch artifact must be a safe tensor state dictionary.")


def _load_onnx_module(file_bytes: bytes) -> Any:
    try:
        import onnx
    except ImportError as exc:  # pragma: no cover
        raise ValueError("onnx is required to load ONNX artifacts.") from exc

    try:
        return onnx.load_model_from_string(file_bytes)
    except Exception as exc:  # pragma: no cover
        try:
            return onnx.load(io.BytesIO(file_bytes))
        except Exception:
            raise ValueError(f"Could not deserialize ONNX artifact: {exc}") from exc


def load_model_from_bytes(file_bytes: bytes, filename: str) -> Tuple[ModelArtifact, Any]:
    artifact = validate_artifact_bytes(file_bytes, filename)
    if artifact.format_name == "pytorch":
        return artifact, _load_pytorch_module(file_bytes)
    if artifact.format_name == "onnx":
        return artifact, _load_onnx_module(file_bytes)
    raise ValueError(f"Unsupported model format: {filename}")


def load_local_reference_model(model_path: str) -> Tuple[ModelArtifact, Any]:
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(f"Model reference not found: {model_path}")
    file_bytes = path.read_bytes()
    return load_model_from_bytes(file_bytes, path.name)


__all__ = [
    "ModelArtifact",
    "classify_model_type",
    "compute_sha256",
    "validate_artifact_bytes",
    "load_model_from_bytes",
    "load_local_reference_model",
]
