"""Model loading utilities for HuggingFace models."""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from transformers import AutoConfig, AutoModel, AutoTokenizer, AutoFeatureExtractor
from optimum_cli.utils.logger import log
from optimum_cli.utils.exceptions import ModelLoadError
from optimum_cli.utils.validators import validate_model_id, validate_path


class ModelLoader:
    """Handles loading of HuggingFace models and tokenizers."""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
    
    def load_model(
        self,
        model_id: str,
        task: Optional[str] = None,
        **kwargs
    ) -> Tuple[Any, Any, Dict[str, Any]]:
        """
        Load model, processor, and config from HuggingFace.
        
        Args:
            model_id: HuggingFace model ID or local path
            task: Optional task type hint
            **kwargs: Additional arguments for model loading
        
        Returns:
            Tuple of (model, processor, config_dict)
        """
        cache_key = f"{model_id}_{task}"
        if cache_key in self._cache:
            log.info(f"Loading model from cache: {model_id}")
            return self._cache[cache_key]
        
        try:
            log.info(f"Loading model: {model_id}")
            
            # Load config
            config = AutoConfig.from_pretrained(model_id, **kwargs)
            config_dict = config.to_dict()
            
            # Detect task from config if not provided
            if task is None:
                task = self._infer_task(config_dict)
            
            log.info(f"Detected task: {task}")
            
            # Load model
            model = AutoModel.from_pretrained(model_id, **kwargs)
            
            # Load processor (tokenizer or feature extractor)
            processor = self._load_processor(model_id, config_dict, **kwargs)
            
            result = (model, processor, config_dict)
            self._cache[cache_key] = result
            
            log.success(f"Successfully loaded model: {model_id}")
            return result
            
        except Exception as e:
            log.error(f"Failed to load model {model_id}: {e}")
            raise ModelLoadError(f"Failed to load model '{model_id}': {e}")
    
    def _load_processor(
        self,
        model_id: str,
        config: Dict[str, Any],
        **kwargs
    ) -> Any:
        """Load appropriate processor (tokenizer or feature extractor)."""
        try:
            # Try tokenizer first (for text models)
            try:
                processor = AutoTokenizer.from_pretrained(model_id, **kwargs)
                log.debug("Loaded tokenizer")
                return processor
            except Exception:
                pass
            
            # Try feature extractor (for vision/audio models)
            try:
                processor = AutoFeatureExtractor.from_pretrained(model_id, **kwargs)
                log.debug("Loaded feature extractor")
                return processor
            except Exception:
                pass
            
            log.warning("No processor (tokenizer/feature extractor) found")
            return None
            
        except Exception as e:
            log.warning(f"Failed to load processor: {e}")
            return None
    
    def _infer_task(self, config: Dict[str, Any]) -> str:
        """Infer task type from model config."""
        # Check architectures field
        architectures = config.get("architectures", [])
        if not architectures:
            return "unknown"
        
        arch = architectures[0].lower()
        
        # Text tasks
        if "formaskedlm" in arch:
            return "fill-mask"
        elif "forsequenceclassification" in arch:
            return "text-classification"
        elif "fortokenclassification" in arch:
            return "token-classification"
        elif "forcausallm" in arch or "forgpt" in arch:
            return "text-generation"
        elif "forquestionanswering" in arch:
            return "question-answering"
        
        # Vision tasks
        elif "forimageclassification" in arch:
            return "image-classification"
        elif "forobjectdetection" in arch:
            return "object-detection"
        elif "forimagesegmentation" in arch:
            return "image-segmentation"
        
        # Multimodal
        elif "clip" in arch:
            return "zero-shot-image-classification"
        
        return "unknown"
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """Get model information without loading full model."""
        try:
            validate_model_id(model_id)
            config = AutoConfig.from_pretrained(model_id)
            config_dict = config.to_dict()
            
            return {
                "model_id": model_id,
                "task": self._infer_task(config_dict),
                "architectures": config_dict.get("architectures", []),
                "model_type": config_dict.get("model_type", "unknown"),
                "num_parameters": self._estimate_parameters(config_dict),
                "hidden_size": config_dict.get("hidden_size"),
                "num_layers": config_dict.get("num_hidden_layers") or config_dict.get("num_layers"),
            }
        except Exception as e:
            log.error(f"Failed to get model info: {e}")
            raise ModelLoadError(f"Failed to get model info: {e}")
    
    def _estimate_parameters(self, config: Dict[str, Any]) -> Optional[int]:
        """Estimate number of parameters from config."""
        try:
            # This is a rough estimation
            vocab_size = config.get("vocab_size", 30000)
            hidden_size = config.get("hidden_size", 768)
            num_layers = config.get("num_hidden_layers") or config.get("num_layers", 12)
            
            # Rough formula for transformer models
            # Embedding + layers + output layer
            params = vocab_size * hidden_size  # Embeddings
            params += num_layers * (hidden_size * hidden_size * 4)  # Layers
            params += vocab_size * hidden_size  # Output
            
            return params
        except Exception:
            return None
    
    def validate_model_path(self, path: str) -> bool:
        """Validate if path contains a valid model."""
        try:
            model_path = validate_path(path, must_exist=True)
            
            # Check for config.json
            config_path = model_path / "config.json"
            if not config_path.exists():
                raise ModelLoadError(f"No config.json found in {path}")
            
            # Check for model files
            has_pytorch = (model_path / "pytorch_model.bin").exists() or \
                         (model_path / "model.safetensors").exists()
            has_onnx = (model_path / "model.onnx").exists()
            has_openvino = (model_path / "openvino_model.xml").exists()
            
            if not (has_pytorch or has_onnx or has_openvino):
                raise ModelLoadError(f"No model files found in {path}")
            
            return True
            
        except Exception as e:
            raise ModelLoadError(f"Invalid model path: {e}")
    
    def clear_cache(self):
        """Clear model cache."""
        self._cache.clear()
        log.info("Model cache cleared")


# Global model loader instance
_loader: Optional[ModelLoader] = None


def get_model_loader() -> ModelLoader:
    """Get global model loader instance."""
    global _loader
    if _loader is None:
        _loader = ModelLoader()
    return _loader
