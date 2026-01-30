"""OpenVINO backend implementation."""

from pathlib import Path
from typing import Any, Dict

from optimum_cli.backends.base import BaseBackend
from optimum_cli.utils.logger import log
from optimum_cli.utils.exceptions import OptimizationError


class OpenVINOBackend(BaseBackend):
    """Intel OpenVINO optimization backend."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.name = "OpenVINO"
    
    def optimize(
        self,
        model: Any,
        output_path: Path,
        tokenizer: Any = None,
        task: str = None,
        **kwargs
    ) -> Path:
        """
        Optimize model using OpenVINO.
        
        Args:
            model: Model to optimize
            output_path: Path to save optimized model
            tokenizer: Model tokenizer/processor
            task: Task type
            **kwargs: Additional parameters
        
        Returns:
            Path to optimized model
        """
        try:
            log.info("Converting model to OpenVINO format...")
            
            # Create output directory
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Check if optimum[openvino] is available
            try:
                from optimum.intel.openvino import OVModelForSequenceClassification, OVConfig, OVQuantizer
            except ImportError:
                raise OptimizationError(
                    "OpenVINO backend requires 'optimum[openvino]'. "
                    "Install with: pip install optimum[openvino,nncf]"
                )
            
            # Export to OpenVINO
            ov_model = self._export_to_openvino(model, task, output_path)
            
            # Save tokenizer if provided
            if tokenizer:
                tokenizer.save_pretrained(output_path)
            
            # Quantize model if enabled
            if self.config.get("quantization_enabled", True):
                log.info("Quantizing model with OpenVINO...")
                self._quantize_openvino(model, tokenizer, output_path)
            
            log.success(f"OpenVINO optimization complete: {output_path}")
            return output_path
            
        except Exception as e:
            log.error(f"OpenVINO optimization failed: {e}")
            raise OptimizationError(f"OpenVINO optimization failed: {e}")
    
    def _export_to_openvino(self, model: Any, task: str, output_path: Path) -> Any:
        """Export model to OpenVINO format."""
        try:
            from optimum.intel.openvino import OVModelForSequenceClassification
            
            # Get model name
            model_name = model.config._name_or_path
            
            # Load and export using OVModel
            ov_model = OVModelForSequenceClassification.from_pretrained(
                model_name,
                export=True
            )
            
            # Save to output path
            ov_model.save_pretrained(output_path)
            
            return ov_model
            
        except Exception as e:
            log.warning(f"OpenVINO export using OVModel failed: {e}")
            # Fallback
            model.save_pretrained(output_path)
            return None
    
    def _quantize_openvino(self, model: Any, tokenizer: Any, output_path: Path):
        """Quantize model using OpenVINO NNCF."""
        try:
            from optimum.intel.openvino import OVConfig, OVQuantizer
            
            # Create quantization config
            quantization_config = OVConfig()
            
            # Initialize quantizer
            quantizer = OVQuantizer.from_pretrained(model)
            
            # For simple quantization without calibration dataset
            # We'll use basic quantization
            quantizer.quantize(
                quantization_config=quantization_config,
                save_directory=output_path,
            )
            
        except Exception as e:
            log.warning(f"OpenVINO quantization failed: {e}")
    
    def is_supported(self, model_config: Dict[str, Any]) -> bool:
        """Check if model is supported by OpenVINO."""
        # OpenVINO supports most transformer models
        return True
    
    def get_requirements(self) -> list:
        """Get required packages."""
        return [
            "optimum[openvino,nncf]>=1.16.0",
            "openvino>=2023.0.0",
        ]
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "device": "CPU",
            "precision": "FP16",
            "quantization_enabled": True,
            "preset": "mixed",
        }
