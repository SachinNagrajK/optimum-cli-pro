"""BetterTransformer backend implementation."""

from pathlib import Path
from typing import Any, Dict

from optimum_cli.backends.base import BaseBackend
from optimum_cli.utils.logger import log
from optimum_cli.utils.exceptions import OptimizationError


class BetterTransformerBackend(BaseBackend):
    """BetterTransformer optimization backend."""
    
    SUPPORTED_MODELS = [
        "bert", "roberta", "distilbert", "vit", "albert",
        "bart", "mbart", "electra", "gpt2", "t5"
    ]
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.name = "BetterTransformer"
    
    def optimize(
        self,
        model: Any,
        output_path: Path,
        **kwargs
    ) -> Path:
        """
        Optimize model using BetterTransformer.
        
        Args:
            model: PyTorch model to optimize
            output_path: Path to save optimized model
            **kwargs: Additional parameters
        
        Returns:
            Path to optimized model
        """
        try:
            from optimum.bettertransformer import BetterTransformer
            
            log.info("Applying BetterTransformer optimization...")
            
            # Transform model
            optimized_model = BetterTransformer.transform(model)
            
            # Save optimized model
            output_path.mkdir(parents=True, exist_ok=True)
            optimized_model.save_pretrained(output_path)
            
            log.success(f"BetterTransformer optimization complete: {output_path}")
            return output_path
            
        except Exception as e:
            log.error(f"BetterTransformer optimization failed: {e}")
            raise OptimizationError(f"BetterTransformer optimization failed: {e}")
    
    def is_supported(self, model_config: Dict[str, Any]) -> bool:
        """Check if model is supported by BetterTransformer."""
        model_type = model_config.get("model_type", "").lower()
        architectures = model_config.get("architectures", [])
        
        # Check model type
        if any(supported in model_type for supported in self.SUPPORTED_MODELS):
            return True
        
        # Check architectures
        if architectures:
            arch_str = " ".join(architectures).lower()
            if any(supported in arch_str for supported in self.SUPPORTED_MODELS):
                return True
        
        return False
    
    def get_requirements(self) -> list:
        """Get required packages."""
        return ["torch>=1.12.0", "optimum>=1.5.0", "transformers>=4.22.0"]
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "validate_model": True,
            "keep_original_model": True,
        }
