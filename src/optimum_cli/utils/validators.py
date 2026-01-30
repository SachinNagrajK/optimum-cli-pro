"""Input validation utilities."""

import re
from pathlib import Path
from typing import Optional

from optimum_cli.utils.exceptions import ValidationError


def validate_model_id(model_id: str) -> bool:
    """Validate HuggingFace model ID format."""
    # Format: organization/model-name or model-name
    pattern = r"^[\w-]+(\/[\w-]+)?$"
    if not re.match(pattern, model_id):
        raise ValidationError(
            f"Invalid model ID format: '{model_id}'. "
            "Expected format: 'organization/model-name' or 'model-name'"
        )
    return True


def validate_backend(backend: str) -> bool:
    """Validate backend name."""
    valid_backends = ["auto", "onnx", "openvino", "bettertransformer"]
    if backend not in valid_backends:
        raise ValidationError(
            f"Invalid backend: '{backend}'. "
            f"Must be one of: {', '.join(valid_backends)}"
        )
    return True


def validate_path(path: str, must_exist: bool = False) -> Path:
    """Validate and normalize path."""
    try:
        p = Path(path).resolve()
        if must_exist and not p.exists():
            raise ValidationError(f"Path does not exist: {path}")
        return p
    except Exception as e:
        raise ValidationError(f"Invalid path: {path} - {e}")


def validate_batch_size(batch_size: int) -> bool:
    """Validate batch size."""
    if batch_size < 1 or batch_size > 128:
        raise ValidationError(
            f"Invalid batch size: {batch_size}. Must be between 1 and 128."
        )
    return True


def validate_sequence_length(sequence_length: int) -> bool:
    """Validate sequence length."""
    if sequence_length < 1 or sequence_length > 4096:
        raise ValidationError(
            f"Invalid sequence length: {sequence_length}. Must be between 1 and 4096."
        )
    return True


def validate_quantization_bits(bits: int) -> bool:
    """Validate quantization bits."""
    valid_bits = [4, 8, 16]
    if bits not in valid_bits:
        raise ValidationError(
            f"Invalid quantization bits: {bits}. Must be one of: {valid_bits}"
        )
    return True


def validate_output_dir(output_dir: str, create: bool = True) -> Path:
    """Validate output directory and optionally create it."""
    path = validate_path(output_dir, must_exist=False)
    
    if create and not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    
    return path


def validate_port(port: int) -> bool:
    """Validate port number."""
    if port < 1 or port > 65535:
        raise ValidationError(f"Invalid port: {port}. Must be between 1 and 65535.")
    return True


def validate_model_name(name: str) -> bool:
    """Validate model name for registry."""
    # Allow alphanumeric, hyphens, underscores
    pattern = r"^[a-zA-Z0-9_-]+$"
    if not re.match(pattern, name):
        raise ValidationError(
            f"Invalid model name: '{name}'. "
            "Only alphanumeric characters, hyphens, and underscores allowed."
        )
    return True


def validate_version(version: str) -> bool:
    """Validate version string."""
    # Semver-like: v1.0.0 or 1.0.0
    pattern = r"^v?\d+\.\d+\.\d+$"
    if not re.match(pattern, version):
        raise ValidationError(
            f"Invalid version format: '{version}'. "
            "Expected format: 'v1.0.0' or '1.0.0'"
        )
    return True
