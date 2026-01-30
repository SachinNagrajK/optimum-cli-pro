"""Backend manager for handling multiple optimization backends."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from optimum_cli.backends.base import BaseBackend
from optimum_cli.backends.bettertransformer import BetterTransformerBackend
from optimum_cli.backends.onnx import ONNXBackend
from optimum_cli.backends.openvino import OpenVINOBackend
from optimum_cli.utils.logger import log
from optimum_cli.utils.exceptions import BackendNotSupportedError
from optimum_cli.utils.hardware import get_hardware_detector
from optimum_cli.core.config import load_config_file


class BackendManager:
    """Manages multiple optimization backends."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize backend manager.
        
        Args:
            config_path: Optional path to backends configuration file
        """
        self.backends: Dict[str, BaseBackend] = {}
        self.config = {}
        
        if config_path:
            self.config = load_config_file(config_path)
        
        self._register_backends()
    
    def _register_backends(self):
        """Register all available backends."""
        # Get backend configs
        bt_config = self.config.get("bettertransformer", {})
        onnx_config = self.config.get("onnx", {}).get("settings", {})
        ov_config = self.config.get("openvino", {}).get("settings", {})
        
        # Register backends
        self.backends["bettertransformer"] = BetterTransformerBackend(bt_config)
        self.backends["onnx"] = ONNXBackend(onnx_config)
        self.backends["openvino"] = OpenVINOBackend(ov_config)
        
        log.info(f"Registered {len(self.backends)} backends")
    
    def get_backend(self, name: str) -> BaseBackend:
        """
        Get backend by name.
        
        Args:
            name: Backend name
        
        Returns:
            Backend instance
        
        Raises:
            BackendNotSupportedError: If backend not found
        """
        name = name.lower()
        
        if name == "auto":
            return self.auto_select_backend()
        
        if name not in self.backends:
            available = ", ".join(self.backends.keys())
            raise BackendNotSupportedError(
                f"Backend '{name}' not found. Available backends: {available}"
            )
        
        backend = self.backends[name]
        
        # Validate environment
        if not backend.validate_environment():
            raise BackendNotSupportedError(
                f"Backend '{name}' environment validation failed. "
                f"Required packages: {backend.get_requirements()}"
            )
        
        return backend
    
    def auto_select_backend(
        self,
        model_config: Optional[Dict[str, Any]] = None
    ) -> BaseBackend:
        """
        Automatically select best backend based on hardware and model.
        
        Args:
            model_config: Optional model configuration
        
        Returns:
            Best backend for current environment
        """
        log.info("Auto-selecting best backend...")
        
        # Get hardware info
        detector = get_hardware_detector()
        recommended = detector.recommend_backend()
        
        log.info(f"Hardware-based recommendation: {recommended}")
        
        # Try recommended backend
        try:
            backend = self.get_backend(recommended)
            if model_config and backend.is_supported(model_config):
                log.info(f"Selected backend: {recommended}")
                return backend
        except Exception as e:
            log.warning(f"Recommended backend '{recommended}' not available: {e}")
        
        # Fallback: try backends in order of preference
        fallback_order = ["onnx", "bettertransformer", "openvino"]
        
        for name in fallback_order:
            try:
                backend = self.backends[name]
                if backend.validate_environment():
                    if not model_config or backend.is_supported(model_config):
                        log.info(f"Selected fallback backend: {name}")
                        return backend
            except Exception as e:
                log.debug(f"Backend '{name}' not available: {e}")
                continue
        
        raise BackendNotSupportedError("No suitable backend found")
    
    def list_backends(self) -> List[str]:
        """Get list of available backend names."""
        return list(self.backends.keys())
    
    def get_backend_info(self, name: str) -> Dict[str, Any]:
        """
        Get information about a backend.
        
        Args:
            name: Backend name
        
        Returns:
            Backend information dictionary
        """
        backend = self.get_backend(name)
        
        return {
            "name": backend.name,
            "available": backend.validate_environment(),
            "requirements": backend.get_requirements(),
            "config": backend.get_default_config(),
        }
    
    def optimize_model(
        self,
        model: Any,
        backend_name: str,
        output_path: Path,
        **kwargs
    ) -> Path:
        """
        Optimize model using specified backend.
        
        Args:
            model: Model to optimize
            backend_name: Name of backend to use
            output_path: Path to save optimized model
            **kwargs: Additional backend-specific parameters
        
        Returns:
            Path to optimized model
        """
        backend = self.get_backend(backend_name)
        
        log.info(f"Optimizing model with {backend.name} backend...")
        
        return backend.optimize(model, output_path, **kwargs)


# Global backend manager instance
_manager: Optional[BackendManager] = None


def get_backend_manager(config_path: Optional[str] = None) -> BackendManager:
    """Get global backend manager instance."""
    global _manager
    if _manager is None:
        _manager = BackendManager(config_path)
    return _manager
