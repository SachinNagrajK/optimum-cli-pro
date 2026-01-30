"""Basic test file."""

import pytest
from optimum_cli import __version__


def test_version():
    """Test version is set."""
    assert __version__ == "1.0.0"


def test_imports():
    """Test that main modules can be imported."""
    from optimum_cli.core.optimizer import ModelOptimizer
    from optimum_cli.core.backend_manager import BackendManager
    from optimum_cli.backends.base import BaseBackend
    
    assert ModelOptimizer is not None
    assert BackendManager is not None
    assert BaseBackend is not None
