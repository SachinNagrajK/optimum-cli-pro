"""Pydantic schemas for API."""

from typing import Optional, List
from pydantic import BaseModel, Field


class OptimizeRequest(BaseModel):
    """Request schema for model optimization."""
    
    model_id: str = Field(..., description="HuggingFace model ID or local path")
    backend: str = Field("auto", description="Backend to use: auto, onnx, openvino")
    output_dir: str = Field("./optimized_models", description="Output directory")
    task: Optional[str] = Field(None, description="Task type (auto-detected if not provided)")
    batch_size: Optional[int] = Field(None, description="Batch size")
    sequence_length: Optional[int] = Field(None, description="Sequence length")
    device: str = Field("auto", description="Execution device: auto, cpu, gpu")
    quantization: bool = Field(True, description="Enable quantization")
    track_mlflow: Optional[bool] = Field(None, description="Override MLflow tracking for this request")
    track_wandb: Optional[bool] = Field(None, description="Override Weights & Biases tracking for this request")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_id": "bert-base-uncased",
                "backend": "onnx",
                "device": "auto",
                "quantization": True,
                "track_mlflow": False,
                "track_wandb": False,
            }
        }


class OptimizeResponse(BaseModel):
    """Response schema for model optimization."""
    
    success: bool
    model_id: str
    backend: str
    output_path: str
    task: str
    optimization_time_seconds: float
    message: Optional[str] = None


class ModelInfo(BaseModel):
    """Model information schema."""
    
    model_id: str
    task: str
    model_type: str
    architectures: List[str]
    num_parameters: Optional[int] = None
    hidden_size: Optional[int] = None
    num_layers: Optional[int] = None


class HealthResponse(BaseModel):
    """Health check response schema."""
    
    status: str
    version: str
    backends_available: List[str]


class ErrorResponse(BaseModel):
    """Error response schema."""
    
    error: str
    detail: Optional[str] = None
