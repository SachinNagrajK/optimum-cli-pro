"""Tests for backend manager."""

import pytest
from optimum_cli.core.backend_manager import BackendManager
from optimum_cli.backends.bettertransformer import BetterTransformerBackend
from optimum_cli.backends.onnx import ONNXBackend
from optimum_cli.backends.openvino import OpenVINOBackend


def test_backend_manager_initialization():
    """Test backend manager initialization."""
    manager = BackendManager()
    assert manager is not None
    assert len(manager.backends) > 0


def test_list_backends():
    """Test listing backends."""
    manager = BackendManager()
    backends = manager.list_backends()
    
    assert "bettertransformer" in backends
    assert "onnx" in backends
    assert "openvino" in backends


def test_get_backend():
    """Test getting backend by name."""
    manager = BackendManager()
    
    backend = manager.get_backend("onnx")
    assert isinstance(backend, ONNXBackend)


def test_backend_validation(mock_model_config):
    """Test backend model support validation."""
    manager = BackendManager()
    
    backend = manager.backends["bettertransformer"]
    assert backend.is_supported(mock_model_config)
