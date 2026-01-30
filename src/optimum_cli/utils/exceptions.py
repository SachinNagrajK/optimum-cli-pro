"""Custom exceptions for Optimum CLI Pro."""


class OptimumCLIError(Exception):
    """Base exception for Optimum CLI Pro."""
    pass


class BackendNotSupportedError(OptimumCLIError):
    """Raised when backend is not supported."""
    pass


class ModelLoadError(OptimumCLIError):
    """Raised when model loading fails."""
    pass


class OptimizationError(OptimumCLIError):
    """Raised when optimization fails."""
    pass


class BenchmarkError(OptimumCLIError):
    """Raised when benchmarking fails."""
    pass


class StorageError(OptimumCLIError):
    """Raised when storage operation fails."""
    pass


class RegistryError(OptimumCLIError):
    """Raised when registry operation fails."""
    pass


class HardwareDetectionError(OptimumCLIError):
    """Raised when hardware detection fails."""
    pass


class ValidationError(OptimumCLIError):
    """Raised when validation fails."""
    pass


class ConfigurationError(OptimumCLIError):
    """Raised when configuration is invalid."""
    pass
