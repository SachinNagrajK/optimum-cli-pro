"""Registry API routes."""

from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from optimum_cli.core.benchmarking import load_runtime_model, masked_token_predictions
from optimum_cli.core.registry import ModelRegistry

router = APIRouter()


class ModelInfo(BaseModel):
    """Model information response."""

    id: int
    name: str
    version: str
    backend: str
    model_path: str
    base_model: Optional[str]
    task: Optional[str]
    size_mb: float
    created_at: str


class InferenceRequest(BaseModel):
    """Inference request."""

    input_text: str


class InferenceResponse(BaseModel):
    """Inference response."""

    model_name: str
    model_version: str
    backend: str
    predictions: list
    inference_time: float


@router.get("/registry/models", response_model=List[ModelInfo])
async def list_registry_models(name: Optional[str] = None):
    """List all models in registry."""
    registry = ModelRegistry()
    await registry.initialize()
    models = await registry.list_models(name)
    return models


@router.get("/registry/models/{name}", response_model=ModelInfo)
async def get_registry_model(name: str, version: str = "latest"):
    """Get specific model from registry."""
    registry = ModelRegistry()
    await registry.initialize()
    model = await registry.get_model(name, version)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Model {name}:{version} not found"
        )
    return model


@router.post("/registry/models/{name}/predict", response_model=InferenceResponse)
async def predict(name: str, request: InferenceRequest, version: str = "latest"):
    """Run inference with a registered model."""
    import time

    # Get model from registry
    registry = ModelRegistry()
    await registry.initialize()
    model_info = await registry.get_model(name, version)

    if not model_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Model {name}:{version} not found"
        )

    try:
        tokenizer, model = load_runtime_model(
            Path(model_info["model_path"]),
            model_info["backend"],
            base_model=model_info.get("base_model"),
            device="auto",
        )

        # Run inference
        inputs = tokenizer(request.input_text, return_tensors="pt")

        start_time = time.perf_counter()
        _ = model(**inputs)
        inference_time = time.perf_counter() - start_time

        predictions = masked_token_predictions(model, tokenizer, request.input_text, top_k=5)

        return InferenceResponse(
            model_name=model_info["name"],
            model_version=model_info["version"],
            backend=model_info["backend"],
            predictions=predictions,
            inference_time=inference_time,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
