"""Tests for hardware detection."""

import pytest
from optimum_cli.utils.hardware import HardwareDetector


def test_hardware_detector_initialization():
    """Test hardware detector initialization."""
    detector = HardwareDetector()
    assert detector is not None


def test_detect_cpu():
    """Test CPU detection."""
    detector = HardwareDetector()
    cpu_info = detector.detect_cpu()
    
    assert "cores_physical" in cpu_info
    assert "cores_logical" in cpu_info
    assert "vendor" in cpu_info


def test_detect_memory():
    """Test memory detection."""
    detector = HardwareDetector()
    mem_info = detector.detect_memory()
    
    assert "total_gb" in mem_info
    assert "available_gb" in mem_info
    assert mem_info["total_gb"] > 0


def test_detect_platform():
    """Test platform detection."""
    detector = HardwareDetector()
    platform_info = detector.detect_platform()
    
    assert "system" in platform_info
    assert "python_version" in platform_info


def test_recommend_backend():
    """Test backend recommendation."""
    detector = HardwareDetector()
    backend = detector.recommend_backend()
    
    assert backend in ["onnx", "openvino", "bettertransformer"]
