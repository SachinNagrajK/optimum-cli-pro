"""Registry API routes."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

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
    from optimum.intel import OVModelForMaskedLM
    from optimum.onnxruntime import ORTModelForMaskedLM
    from transformers import AutoTokenizer

    # Get model from registry
    registry = ModelRegistry()
    await registry.initialize()
    model_info = await registry.get_model(name, version)

    if not model_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Model {name}:{version} not found"
        )

    try:
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            model_info["base_model"] or "bert-base-uncased"
        )

        # Load model based on backend
        if model_info["backend"] == "onnx":
            model = ORTModelForMaskedLM.from_pretrained(model_info["model_path"])
        elif model_info["backend"] == "openvino":
            model = OVModelForMaskedLM.from_pretrained(model_info["model_path"])
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported backend: {model_info['backend']}",
            )

        # Run inference
        inputs = tokenizer(request.input_text, return_tensors="pt")

        start_time = time.perf_counter()
        outputs = model(**inputs)
        inference_time = time.perf_counter() - start_time

        # Get predictions
        logits = outputs.logits
        mask_token_index = (inputs["input_ids"] == tokenizer.mask_token_id)[0].nonzero(
            as_tuple=True
        )[0]
        
        if len(mask_token_index) > 0:
            mask_token_logits = logits[0, mask_token_index, :]
            top_tokens = mask_token_logits.topk(5, dim=-1).indices[0].tolist()
            predictions = [
                {"token": tokenizer.decode([token]), "score": float(mask_token_logits[0, i])}
                for i, token in enumerate(top_tokens)
            ]
        else:
            predictions = []

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
