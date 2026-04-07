"""OpenVINO backend implementation."""

from importlib import util
from pathlib import Path
from typing import Any, Dict, Optional

from optimum_cli.backends.base import BaseBackend
from optimum_cli.utils.logger import log
from optimum_cli.utils.exceptions import OptimizationError


class OpenVINOBackend(BaseBackend):
    """Intel OpenVINO optimization backend."""

    TASK_TO_OV_CLASS = {
        "fill-mask": "OVModelForMaskedLM",
        "text-classification": "OVModelForSequenceClassification",
        "token-classification": "OVModelForTokenClassification",
        "question-answering": "OVModelForQuestionAnswering",
        "text-generation": "OVModelForCausalLM",
        "text2text-generation": "OVModelForSeq2SeqLM",
        "summarization": "OVModelForSeq2SeqLM",
        "translation": "OVModelForSeq2SeqLM",
    }
    
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
            
            if util.find_spec("optimum.intel.openvino") is None or util.find_spec("openvino") is None:
                raise OptimizationError(
                    "OpenVINO backend requires 'optimum[openvino]'. "
                    "Install with: pip install optimum[openvino,nncf]"
                )
            
            resolved_task = self._resolve_task(model, task)
            if task and resolved_task != task:
                log.info(f"Resolved task '{task}' to '{resolved_task}' for OpenVINO export")

            # Export to OpenVINO
            self._export_to_openvino(model, resolved_task, output_path)
            
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
    
    def _export_to_openvino(self, model: Any, task: Optional[str], output_path: Path) -> Any:
        """Export model to OpenVINO format."""
        try:
            import optimum.intel.openvino as ov_module

            # Get model name
            model_name = model.config._name_or_path

            class_name = self.TASK_TO_OV_CLASS.get(task or "")
            if not class_name:
                class_name = "OVModelForSequenceClassification"

            model_cls = getattr(ov_module, class_name, None)
            if model_cls is None:
                raise OptimizationError(
                    f"No OpenVINO model class available for task '{task}'. "
                    "Try --task text-classification, text-generation, or text2text-generation."
                )

            # Load and export using task-compatible OVModel
            ov_model = model_cls.from_pretrained(model_name, export=True)
            
            # Save to output path
            ov_model.save_pretrained(output_path)
            
            return ov_model
            
        except Exception as e:
            raise OptimizationError(f"OpenVINO export failed: {e}")

    def _resolve_task(self, model: Any, task: Optional[str]) -> Optional[str]:
        """Resolve task hint into an OpenVINO-friendly task string."""
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
            "optimum-intel>=1.16.0",
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
