"""ONNX Runtime backend implementation."""

from pathlib import Path
from typing import Any, Dict, Optional

from optimum_cli.backends.base import BaseBackend
from optimum_cli.utils.logger import log
from optimum_cli.utils.exceptions import OptimizationError


class ONNXBackend(BaseBackend):
    """ONNX Runtime optimization backend."""

    TASK_TO_ORT_CLASS = {
        "fill-mask": "ORTModelForMaskedLM",
        "text-classification": "ORTModelForSequenceClassification",
        "token-classification": "ORTModelForTokenClassification",
        "question-answering": "ORTModelForQuestionAnswering",
        "text-generation": "ORTModelForCausalLM",
        "text2text-generation": "ORTModelForSeq2SeqLM",
        "summarization": "ORTModelForSeq2SeqLM",
        "translation": "ORTModelForSeq2SeqLM",
    }
    
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
            log.info("Converting model to ONNX...")
            
            # Create output directory
            output_path.mkdir(parents=True, exist_ok=True)
            
            resolved_task = self._resolve_task(model, task)
            if task and resolved_task != task:
                log.info(f"Resolved task '{task}' to '{resolved_task}' for ONNX export")

            # Export to ONNX
            self._export_to_onnx(model, resolved_task, output_path)

            ort_model = self._load_ort_model_for_task(output_path, resolved_task)
            
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
    
    def _export_to_onnx(self, model: Any, task: Optional[str], output_path: Path) -> None:
        """Export model to ONNX format."""
        try:
            # Use generic export
            from optimum.exporters.onnx import main_export
            
            # Get model name
            model_name = model.config._name_or_path
            
            # Export using optimum CLI equivalent
            main_export(
                model_name_or_path=model_name,
                output=output_path,
                task=task or "auto",
            )

        except Exception as e:
            raise OptimizationError(f"ONNX export failed: {e}")

    def _load_ort_model_for_task(self, output_path: Path, task: Optional[str]) -> Any:
        """Try to load exported ONNX artifact with a task-compatible ORT class."""
        try:
            import optimum.onnxruntime as ort_module

            class_name = self.TASK_TO_ORT_CLASS.get(task or "")
            if not class_name:
                return None

            model_cls = getattr(ort_module, class_name, None)
            if model_cls is None:
                return None

            return model_cls.from_pretrained(output_path)
        except Exception as error:
            log.warning(f"Could not load ORT model class for task '{task}': {error}")
            return None

    def _resolve_task(self, model: Any, task: Optional[str]) -> Optional[str]:
        """Resolve task hint into an exporter-friendly task string."""
        if task and task != "unknown":
            return task

        model_type = str(getattr(model.config, "model_type", "")).lower()
        architectures = [arch.lower() for arch in getattr(model.config, "architectures", [])]
        arch_blob = " ".join(architectures)

        if model_type in {"bart", "mbart", "t5", "mt5", "pegasus"}:
            return "text2text-generation"
        if "forconditionalgeneration" in arch_blob or "forseq2seq" in arch_blob:
            return "text2text-generation"
        if "forcausallm" in arch_blob:
            return "text-generation"
        if "forsequenceclassification" in arch_blob:
            return "text-classification"
        if "formaskedlm" in arch_blob:
            return "fill-mask"

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
