"""Optimum CLI Pro - Production-grade model optimization toolkit."""

__version__ = "1.0.0"
__author__ = "Optimum CLI Pro"
__license__ = "Apache-2.0"

from optimum_cli.core.optimizer import ModelOptimizer
from optimum_cli.core.backend_manager import BackendManager
from optimum_cli.core.config import Settings

__all__ = ["ModelOptimizer", "BackendManager", "Settings"]
