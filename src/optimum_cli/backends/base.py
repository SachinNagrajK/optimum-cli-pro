"""Base backend interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

from optimum_cli.utils.logger import log


class BaseBackend(ABC):
    """Abstract base class for optimization backends."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize backend.
        
        Args:
            config: Backend-specific configuration
        """
        self.config = config or {}
        self.name = self.__class__.__name__
    
    @abstractmethod
    def optimize(
        self,
        model: Any,
        output_path: Path,
        **kwargs
    ) -> Path:
        """
        Optimize model using this backend.
        
        Args:
            model: Model to optimize
            output_path: Path to save optimized model
            **kwargs: Backend-specific parameters
        
        Returns:
            Path to optimized model
        """
        pass
    
    @abstractmethod
    def is_supported(self, model_config: Dict[str, Any]) -> bool:
        """
        Check if model is supported by this backend.
        
        Args:
            model_config: Model configuration dictionary
        
        Returns:
            True if supported, False otherwise
        """
        pass
    
    @abstractmethod
    def get_requirements(self) -> list:
        """
        Get list of required packages for this backend.
        
        Returns:
            List of package names
        """
        pass
    
    def validate_environment(self) -> bool:
        """
        Validate that backend environment is properly set up.
        
        Returns:
            True if environment is valid
        """
        try:
            requirements = self.get_requirements()
            for package in requirements:
                try:
                    # Extract package name without version specifiers or extras
                    pkg_name = package.split("[")[0].split(">=")[0].split("==")[0].split(">")[0].split("<")[0].strip()
                    __import__(pkg_name)
                except ImportError:
                    log.error(f"Required package not found: {pkg_name} (from {package})")
                    return False
            return True
        except Exception as e:
            log.error(f"Environment validation failed: {e}")
            return False
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for this backend."""
        return {}
    
    def __str__(self) -> str:
        return f"{self.name}Backend"
    
    def __repr__(self) -> str:
        return f"{self.name}Backend(config={self.config})"
