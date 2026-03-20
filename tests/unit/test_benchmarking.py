"""Tests for benchmarking utilities."""

import pytest

from optimum_cli.core.benchmarking import infer_backend_from_path, summarize_latencies
from optimum_cli.utils.exceptions import BenchmarkError


def test_infer_backend_from_path_openvino(tmp_path):
    """Detect OpenVINO artifacts by xml file."""
    model_dir = tmp_path / "model_openvino"
    model_dir.mkdir(parents=True)
    (model_dir / "openvino_model.xml").write_text("<xml />", encoding="utf-8")

    assert infer_backend_from_path(model_dir) == "openvino"


def test_infer_backend_from_path_onnx(tmp_path):
    """Detect ONNX artifacts by model.onnx file."""
    model_dir = tmp_path / "model_onnx"
    model_dir.mkdir(parents=True)
    (model_dir / "model.onnx").write_bytes(b"onnx")

    assert infer_backend_from_path(model_dir) == "onnx"


def test_infer_backend_from_path_raises_when_unknown(tmp_path):
    """Raise a benchmark error for unknown artifact layout."""
    model_dir = tmp_path / "unknown_model"
    model_dir.mkdir(parents=True)

    with pytest.raises(BenchmarkError):
        infer_backend_from_path(model_dir)


def test_summarize_latencies_metrics_shape():
    """Return expected aggregate keys and monotonic percentile ordering."""
    metrics = summarize_latencies([0.01, 0.02, 0.03, 0.05, 0.04])

    assert metrics["runs"] == 5
    assert metrics["mean_latency_s"] > 0
    assert metrics["throughput_rps"] > 0
    assert metrics["p50_latency_s"] <= metrics["p95_latency_s"] <= metrics["p99_latency_s"]


def test_summarize_latencies_raises_for_empty_input():
    """Raise for empty latency samples."""
    with pytest.raises(BenchmarkError):
        summarize_latencies([])
