"""Configuration management using Pydantic."""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerConfig(BaseSettings):
    """Server configuration."""
    
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    reload: bool = False


class OptimizationConfig(BaseSettings):
    """Optimization configuration."""
    
    default_backend: str = "auto"
    batch_size: int = 1
    sequence_length: int = 128
    quantization_enabled: bool = True
    quantization_mode: str = "dynamic"
    quantization_bits: int = 8
    optimization_level: int = 2


class BenchmarkingConfig(BaseSettings):
    """Benchmarking configuration."""
    
    warmup_runs: int = 5
    test_runs: int = 50
    batch_sizes: List[int] = Field(default_factory=lambda: [1, 4, 8, 16])
    sequence_lengths: List[int] = Field(default_factory=lambda: [32, 64, 128, 256])


class StorageConfig(BaseSettings):
    """Storage configuration."""
    
    type: str = "local"
    local_base_path: str = "./data/models"
    s3_bucket: Optional[str] = None
    s3_region: str = "us-east-1"
    s3_prefix: str = "models/"


class DatabaseConfig(BaseSettings):
    """Database configuration."""
    
    type: str = "sqlite"
    path: str = "./data/registry.db"
    echo: bool = False


class LoggingConfig(BaseSettings):
    """Logging configuration."""
    
    level: str = "INFO"
    file_enabled: bool = True
    file_path: str = "./data/logs/app.log"
    file_rotation: str = "100 MB"
    file_retention: str = "30 days"
    console_enabled: bool = True


class MLflowConfig(BaseSettings):
    """MLflow configuration."""
    
    enabled: bool = False
    tracking_uri: str = "./mlruns"
    experiment_name: str = "model-optimization"
    artifact_location: Optional[str] = None


class WandbConfig(BaseSettings):
    """Weights & Biases configuration."""
    
    enabled: bool = False
    project: str = "optimum-cli-pro"
    entity: Optional[str] = None
    api_key: Optional[str] = None


class MLOpsConfig(BaseSettings):
    """MLOps integration configuration."""
    
    mlflow: MLflowConfig = Field(default_factory=MLflowConfig)
    wandb: WandbConfig = Field(default_factory=WandbConfig)


class CostTrackingConfig(BaseSettings):
    """Cost tracking configuration."""
    
    enabled: bool = True
    ec2_t2_micro_hourly: float = 0.0116
    s3_storage_per_gb: float = 0.023
    data_transfer_per_gb: float = 0.09
    warning_threshold: float = 10.0
    critical_threshold: float = 50.0


class Settings(BaseSettings):
    """Main application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    app_name: str = "optimum-cli-pro"
    app_version: str = "1.0.0"
    environment: str = "production"
    debug: bool = False
    
    # Registry path
    @property
    def registry_path(self) -> Path:
        """Get registry storage path."""
        path = Path("./data/registry")
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    server: ServerConfig = Field(default_factory=ServerConfig)
    optimization: OptimizationConfig = Field(default_factory=OptimizationConfig)
    benchmarking: BenchmarkingConfig = Field(default_factory=BenchmarkingConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    mlops: MLOpsConfig = Field(default_factory=MLOpsConfig)
    cost_tracking: CostTrackingConfig = Field(default_factory=CostTrackingConfig)
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> "Settings":
        """Load settings from YAML file."""
        path = Path(yaml_path)
        if not path.exists():
            return cls()
        
        with open(path, "r") as f:
            config_dict = yaml.safe_load(f)
        
        return cls(**cls._flatten_dict(config_dict))
    
    @staticmethod
    def _flatten_dict(d: Dict[str, Any], parent_key: str = "", sep: str = "_") -> Dict[str, Any]:
        """Flatten nested dictionary."""
        items: List[tuple] = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(Settings._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get global settings instance."""
    return settings


def load_config_file(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)
