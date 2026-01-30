"""Test configuration and fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def test_model_id():
    """Return a small test model ID."""
    return "prajjwal1/bert-tiny"


@pytest.fixture
def test_output_dir(tmp_path):
    """Create a temporary output directory."""
    output_dir = tmp_path / "optimized_models"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def mock_model_config():
    """Return a mock model configuration."""
    return {
        "model_type": "bert",
        "architectures": ["BertForSequenceClassification"],
        "hidden_size": 768,
        "num_hidden_layers": 12,
        "vocab_size": 30522,
    }
