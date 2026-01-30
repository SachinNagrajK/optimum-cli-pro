"""Utils module initialization."""

from optimum_cli.utils.logger import get_logger, log
from optimum_cli.utils.exceptions import (
    OptimumCLIError,
    BackendNotSupportedError,
    ModelLoadError,
    OptimizationError,
    BenchmarkError,
    StorageError,
    RegistryError,
    HardwareDetectionError,
    ValidationError,
    ConfigurationError,
)

__all__ = [
    "get_logger",
    "log",
    "OptimumCLIError",
    "BackendNotSupportedError",
    "ModelLoadError",
    "OptimizationError",
    "BenchmarkError",
    "StorageError",
    "RegistryError",
    "HardwareDetectionError",
    "ValidationError",
    "ConfigurationError",
]
