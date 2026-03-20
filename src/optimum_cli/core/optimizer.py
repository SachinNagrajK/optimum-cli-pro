"""Main model optimizer class."""

from typing import Any, Dict, Optional
import time

from optimum_cli.core.model_loader import get_model_loader
from optimum_cli.core.backend_manager import get_backend_manager
from optimum_cli.core.config import get_settings
from optimum_cli.utils.logger import log
from optimum_cli.utils.exceptions import OptimizationError
from optimum_cli.utils.tracking import track_optimization_event
from optimum_cli.utils.validators import (
    validate_model_id,
    validate_backend,
    validate_output_dir,
)


class ModelOptimizer:
    """Main class for model optimization operations."""
    
    def __init__(self):
        """Initialize model optimizer."""
        self.settings = get_settings()
        self.model_loader = get_model_loader()
        self.backend_manager = get_backend_manager()
    
    def optimize(
        self,
        model_id: str,
        backend: str = "auto",
        output_dir: str = "./optimized_models",
        task: Optional[str] = None,
        batch_size: Optional[int] = None,
        sequence_length: Optional[int] = None,
        quantization: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Optimize a HuggingFace model.
        
        Args:
            model_id: HuggingFace model ID or local path
            backend: Backend to use (auto, onnx, openvino, bettertransformer)
            output_dir: Directory to save optimized model
            task: Optional task type
            batch_size: Batch size for optimization
            sequence_length: Sequence length for optimization
            quantization: Enable quantization
            **kwargs: Additional backend-specific parameters
        
        Returns:
            Dictionary with optimization results
        """
        start_time = time.time()

        track_mlflow = kwargs.pop("track_mlflow", None)
        track_wandb = kwargs.pop("track_wandb", None)
        tracking_source = kwargs.pop("tracking_source", "optimizer")
        device = kwargs.pop("device", "auto")
        
        try:
            # Validate inputs
            validate_model_id(model_id)
            validate_backend(backend)
            output_path = validate_output_dir(output_dir, create=True)
            
            log.info(f"Starting optimization of model: {model_id}")
            log.info(f"Backend: {backend}")
            log.info(f"Output directory: {output_path}")
            
            # Load model
            log.info("Loading model...")
            model, processor, config = self.model_loader.load_model(
                model_id=model_id,
                task=task
            )
            
            # Infer task if not provided
            if task is None:
                task = self.model_loader._infer_task(config)
            
            # Select backend
            if backend == "auto":
                backend_instance = self.backend_manager.auto_select_backend(config)
                backend_name = backend_instance.name.lower()
            else:
                backend_instance = self.backend_manager.get_backend(backend)
                backend_name = backend

            requested_device = str(device).lower().strip()
            if requested_device in {"auto", "gpu"} and backend_name == "bettertransformer":
                try:
                    import torch

                    if torch.cuda.is_available():
                        model = model.to("cuda")
                    elif requested_device == "gpu":
                        raise OptimizationError("GPU requested but CUDA is not available")
                except ImportError:
                    if requested_device == "gpu":
                        raise OptimizationError("GPU requested but torch is not available")
            
            # Check if model is supported
            if not backend_instance.is_supported(config):
                log.warning(
                    f"Model may not be fully supported by {backend_name} backend"
                )
            
            # Create model-specific output path
            model_name = model_id.replace("/", "_")
            model_output_path = output_path / f"{model_name}_{backend_name}"
            
            # Prepare optimization parameters
            opt_params = {
                "tokenizer": processor,
                "task": task,
                "batch_size": batch_size or self.settings.optimization.batch_size,
                "sequence_length": sequence_length or self.settings.optimization.sequence_length,
                "device": requested_device,
                **kwargs
            }
            
            # Update backend config with quantization setting
            if hasattr(backend_instance, 'config'):
                backend_instance.config["quantization_enabled"] = quantization
            
            # Optimize model
            log.info(f"Optimizing with {backend_name} backend...")
            optimized_path = backend_instance.optimize(
                model=model,
                output_path=model_output_path,
                **opt_params
            )
            
            elapsed_time = time.time() - start_time
            
            # Prepare result
            result = {
                "success": True,
                "model_id": model_id,
                "backend": backend_name,
                "output_path": str(optimized_path),
                "task": task,
                "optimization_time_seconds": round(elapsed_time, 2),
                "config": config,
            }

            tracking = track_optimization_event(
                model_id=model_id,
                requested_backend=backend,
                quantization=quantization,
                requested_task=task,
                success=True,
                result=result,
                track_mlflow=track_mlflow,
                track_wandb=track_wandb,
                source=tracking_source,
            )
            result["tracking"] = tracking
            
            log.success(
                f"✨ Optimization complete in {elapsed_time:.2f}s\n"
                f"   Output: {optimized_path}"
            )
            
            return result
            
        except Exception as e:
            log.error(f"Optimization failed: {e}")
            try:
                track_optimization_event(
                    model_id=model_id,
                    requested_backend=backend,
                    quantization=quantization,
                    requested_task=task,
                    success=False,
                    error=str(e),
                    track_mlflow=track_mlflow,
                    track_wandb=track_wandb,
                    source=tracking_source,
                )
            except Exception as tracking_error:
                log.warning(f"Tracking failed after optimization error: {tracking_error}")
            raise OptimizationError(f"Model optimization failed: {e}")
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """
        Get information about a model without optimizing it.
        
        Args:
            model_id: HuggingFace model ID
        
        Returns:
            Model information dictionary
        """
        try:
            validate_model_id(model_id)
            return self.model_loader.get_model_info(model_id)
        except Exception as e:
            log.error(f"Failed to get model info: {e}")
            raise
    
    def list_backends(self) -> list:
        """List available backends."""
        return self.backend_manager.list_backends()
    
    def get_backend_info(self, backend: str) -> Dict[str, Any]:
        """Get information about a specific backend."""
        return self.backend_manager.get_backend_info(backend)


# Global optimizer instance
_optimizer: Optional[ModelOptimizer] = None


def get_optimizer() -> ModelOptimizer:
    """Get global optimizer instance."""
    global _optimizer
    if _optimizer is None:
        _optimizer = ModelOptimizer()
    return _optimizer
