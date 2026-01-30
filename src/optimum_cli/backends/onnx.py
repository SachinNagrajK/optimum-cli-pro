"""ONNX Runtime backend implementation."""

from pathlib import Path
from typing import Any, Dict

from optimum_cli.backends.base import BaseBackend
from optimum_cli.utils.logger import log
from optimum_cli.utils.exceptions import OptimizationError


class ONNXBackend(BaseBackend):
    """ONNX Runtime optimization backend."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.name = "ONNX"
    
    def optimize(
        self,
        model: Any,
        output_path: Path,
        tokenizer: Any = None,
        task: str = None,
        **kwargs
    ) -> Path:
        """
        Optimize model using ONNX Runtime.
        
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
            from optimum.onnxruntime import ORTModelForSequenceClassification, ORTModelForQuestionAnswering
            from optimum.onnxruntime import ORTOptimizer, ORTQuantizer
            from optimum.onnxruntime.configuration import OptimizationConfig, AutoQuantizationConfig
            
            log.info("Converting model to ONNX...")
            
            # Create output directory
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Export to ONNX
            # Determine the appropriate ORT model class based on task
            ort_model = self._export_to_onnx(model, task, output_path)
            
            # Save tokenizer if provided
            if tokenizer:
                tokenizer.save_pretrained(output_path)
            
            # Optimize ONNX model
            if self.config.get("optimization_enabled", True):
                log.info("Optimizing ONNX graph...")
                self._optimize_onnx(ort_model, output_path)
            
            # Quantize model
            if self.config.get("quantization_enabled", True):
                log.info("Quantizing ONNX model...")
                self._quantize_onnx(ort_model, output_path)
            
            log.success(f"ONNX optimization complete: {output_path}")
            return output_path
            
        except Exception as e:
            log.error(f"ONNX optimization failed: {e}")
            raise OptimizationError(f"ONNX optimization failed: {e}")
    
    def _export_to_onnx(self, model: Any, task: str, output_path: Path) -> Any:
        """Export model to ONNX format."""
        try:
            from optimum.onnxruntime import ORTModelForSequenceClassification
            
            # Use generic export
            from optimum.exporters.onnx import main_export
            from transformers import AutoTokenizer
            
            # Get model name
            model_name = model.config._name_or_path
            
            # Export using optimum CLI equivalent
            main_export(
                model_name_or_path=model_name,
                output=output_path,
                task=task or "auto",
            )
            
            # Load the exported model
            ort_model = ORTModelForSequenceClassification.from_pretrained(
                output_path,
                file_name="model.onnx"
            )
            
            return ort_model
            
        except Exception as e:
            log.warning(f"Advanced ONNX export failed, using basic export: {e}")
            # Fallback to simple save
            model.save_pretrained(output_path)
            return None
    
    def _optimize_onnx(self, model: Any, output_path: Path):
        """Apply graph optimizations to ONNX model."""
        try:
            from optimum.onnxruntime import ORTOptimizer
            from optimum.onnxruntime.configuration import OptimizationConfig
            
            if model is None:
                return
            
            optimizer = ORTOptimizer.from_pretrained(model)
            
            optimization_config = OptimizationConfig(
                optimization_level=self.config.get("optimization_level", 99),
            )
            
            optimizer.optimize(
                optimization_config=optimization_config,
                save_dir=output_path,
            )
            
        except Exception as e:
            log.warning(f"ONNX optimization step failed: {e}")
    
    def _quantize_onnx(self, model: Any, output_path: Path):
        """Quantize ONNX model."""
        try:
            from optimum.onnxruntime import ORTQuantizer
            from optimum.onnxruntime.configuration import AutoQuantizationConfig
            
            if model is None:
                return
            
            quantizer = ORTQuantizer.from_pretrained(model)
            
            # Dynamic quantization config
            qconfig = AutoQuantizationConfig.avx512_vnni(
                is_static=False,
                per_channel=self.config.get("per_channel", True)
            )
            
            quantizer.quantize(
                save_dir=output_path,
                quantization_config=qconfig,
            )
            
        except Exception as e:
            log.warning(f"ONNX quantization step failed: {e}")
    
    def is_supported(self, model_config: Dict[str, Any]) -> bool:
        """Check if model is supported by ONNX."""
        # ONNX supports most transformer models
        return True
    
    def get_requirements(self) -> list:
        """Get required packages."""
        return [
            "onnx>=1.15.0",
            "onnxruntime>=1.16.0",
            "optimum>=1.16.0",
        ]
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "opset_version": 14,
            "optimization_enabled": True,
            "optimization_level": 99,
            "quantization_enabled": True,
            "per_channel": True,
            "reduce_range": False,
        }
