"""Utilities for loading optimized models and running benchmark comparisons."""

from __future__ import annotations

import statistics
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import torch
from transformers import AutoModel, AutoTokenizer

from optimum_cli.utils.exceptions import BenchmarkError


def infer_backend_from_path(model_path: Path) -> str:
    """Infer backend type from optimized model artifacts in a directory."""
    if not model_path.exists() or not model_path.is_dir():
        raise BenchmarkError(f"Model path does not exist or is not a directory: {model_path}")

    if (model_path / "openvino_model.xml").exists():
        return "openvino"
    if (model_path / "model.onnx").exists():
        return "onnx"

    raise BenchmarkError(
        f"Could not infer backend from {model_path}. Expected openvino_model.xml or model.onnx"
    )


def load_runtime_model(
    model_path: Path,
    backend: str,
    base_model: str | None = None,
    device: str = "auto",
) -> Tuple[Any, Any]:
    """Load tokenizer and runtime model for ONNX/OpenVINO optimized artifacts."""
    backend = backend.lower()
    device = device.lower()

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_path)
    except Exception:
        if base_model:
            tokenizer = AutoTokenizer.from_pretrained(base_model)
        else:
            raise BenchmarkError(
                "Tokenizer not found in optimized model directory and no base model provided"
            )

    if backend == "onnx":
        from optimum.onnxruntime import ORTModelForMaskedLM

        model = _load_onnx_model_with_device(ORTModelForMaskedLM, model_path, device)
        return tokenizer, model

    if backend == "openvino":
        from optimum.intel import OVModelForMaskedLM

        model = _load_openvino_model_with_device(OVModelForMaskedLM, model_path, device)
        return tokenizer, model

    raise BenchmarkError(f"Unsupported backend for runtime benchmarking: {backend}")


def load_hf_baseline_model(model_id_or_path: str, device: str = "auto") -> Tuple[Any, Any]:
    """Load an unoptimized Hugging Face model checkpoint for baseline benchmarking."""
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id_or_path)
        model = AutoModel.from_pretrained(model_id_or_path)

        target_device = _resolve_torch_device(device)
        if target_device != "cpu":
            model = model.to(target_device)

        model.eval()
        return tokenizer, model
    except Exception as error:
        raise BenchmarkError(f"Failed to load baseline model '{model_id_or_path}': {error}")


def summarize_latencies(latencies_seconds: List[float]) -> Dict[str, float]:
    """Create summary statistics from a list of latency measurements."""
    if not latencies_seconds:
        raise BenchmarkError("No latency samples were collected")

    ordered = sorted(latencies_seconds)
    count = len(ordered)

    def percentile(p: float) -> float:
        index = max(0, min(count - 1, int(round((count - 1) * p))))
        return ordered[index]

    mean_latency = statistics.fmean(ordered)
    return {
        "runs": count,
        "mean_latency_s": mean_latency,
        "p50_latency_s": percentile(0.50),
        "p95_latency_s": percentile(0.95),
        "p99_latency_s": percentile(0.99),
        "min_latency_s": ordered[0],
        "max_latency_s": ordered[-1],
        "throughput_rps": 1.0 / mean_latency if mean_latency > 0 else 0.0,
    }


def benchmark_model_inference(
    model: Any,
    tokenizer: Any,
    input_text: str,
    runs: int = 50,
    warmup_runs: int = 3,
    batch_size: int = 1,
    device: str = "auto",
) -> Dict[str, float]:
    """Benchmark model inference and return latency/throughput metrics."""
    if runs <= 0:
        raise BenchmarkError("runs must be greater than 0")
    if warmup_runs < 0:
        raise BenchmarkError("warmup_runs cannot be negative")
    if batch_size <= 0:
        raise BenchmarkError("batch_size must be greater than 0")

    inputs = tokenizer([input_text] * batch_size, return_tensors="pt", padding=True)
    inputs = _move_inputs_for_torch_model(model, inputs, device)

    with torch.no_grad():
        for _ in range(warmup_runs):
            _ = model(**inputs)

        latencies: List[float] = []
        for _ in range(runs):
            start = time.perf_counter()
            _ = model(**inputs)
            latencies.append(time.perf_counter() - start)

    return summarize_latencies(latencies)


def masked_token_predictions(model: Any, tokenizer: Any, input_text: str, top_k: int = 5) -> List[Dict[str, float]]:
    """Get top-k token predictions for a masked language modeling input."""
    if tokenizer.mask_token_id is None:
        return []

    inputs = tokenizer(input_text, return_tensors="pt")
    mask_positions = (inputs["input_ids"] == tokenizer.mask_token_id).nonzero(as_tuple=False)

    if mask_positions.numel() == 0:
        return []

    with torch.no_grad():
        outputs = model(**inputs)

    first_mask_index = int(mask_positions[0, 1].item())
    mask_logits = outputs.logits[0, first_mask_index, :]
    scores, token_ids = torch.topk(mask_logits, k=min(top_k, mask_logits.shape[-1]))

    predictions: List[Dict[str, float]] = []
    for score, token_id in zip(scores.tolist(), token_ids.tolist()):
        predictions.append({
            "token": tokenizer.decode([token_id]).strip(),
            "score": float(score),
        })

    return predictions


def _resolve_torch_device(device: str) -> str:
    requested = (device or "auto").lower().strip()
    if requested == "gpu":
        return "cuda" if torch.cuda.is_available() else "cpu"
    if requested == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return "cpu"


def _move_inputs_for_torch_model(model: Any, inputs: Dict[str, Any], device: str) -> Dict[str, Any]:
    target_device = _resolve_torch_device(device)

    try:
        model_device = getattr(model, "device", None)
        if model_device is not None and str(model_device).startswith("cuda"):
            target_device = "cuda"
    except Exception:
        pass

    if target_device == "cpu":
        return inputs

    moved: Dict[str, Any] = {}
    for key, value in inputs.items():
        if hasattr(value, "to"):
            moved[key] = value.to(target_device)
        else:
            moved[key] = value
    return moved


def _load_onnx_model_with_device(model_cls: Any, model_path: Path, device: str) -> Any:
    requested = (device or "auto").lower().strip()

    if requested in ("auto", "gpu") and torch.cuda.is_available():
        try:
            return model_cls.from_pretrained(model_path, provider="CUDAExecutionProvider")
        except Exception:
            if requested == "gpu":
                raise BenchmarkError(
                    "GPU was requested but CUDAExecutionProvider is unavailable. "
                    "Install onnxruntime-gpu and NVIDIA CUDA drivers, or use --device cpu."
                )

    return model_cls.from_pretrained(model_path, provider="CPUExecutionProvider")


def _load_openvino_model_with_device(model_cls: Any, model_path: Path, device: str) -> Any:
    requested = (device or "auto").lower().strip()

    if requested in ("auto", "gpu"):
        try:
            return model_cls.from_pretrained(model_path, device="GPU")
        except Exception:
            if requested == "gpu":
                raise BenchmarkError(
                    "GPU was requested but OpenVINO GPU device is unavailable. "
                    "Use --device cpu or configure OpenVINO GPU runtime."
                )

    return model_cls.from_pretrained(model_path, device="CPU")
