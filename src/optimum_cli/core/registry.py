"""Model registry for managing optimized models."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import aiosqlite
from loguru import logger

from optimum_cli.core.config import settings


class ModelRegistry:
    """Manage model versions and metadata."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize model registry."""
        self.db_path = db_path or settings.registry_path / "registry.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    async def initialize(self):
        """Initialize database schema."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    version TEXT NOT NULL,
                    backend TEXT NOT NULL,
                    model_path TEXT NOT NULL,
                    base_model TEXT,
                    task TEXT,
                    size_mb REAL,
                    metadata TEXT,
                    created_at TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    UNIQUE(name, version)
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS ab_tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    model_a_id INTEGER NOT NULL,
                    model_b_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'active',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (model_a_id) REFERENCES models (id),
                    FOREIGN KEY (model_b_id) REFERENCES models (id)
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS ab_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id INTEGER NOT NULL,
                    model_id INTEGER NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (test_id) REFERENCES ab_tests (id),
                    FOREIGN KEY (model_id) REFERENCES models (id)
                )
                """
            )
            await db.commit()
            logger.success(f"Registry database initialized at {self.db_path}")

    async def register_model(
        self,
        name: str,
        version: str,
        backend: str,
        model_path: Path,
        base_model: Optional[str] = None,
        task: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> int:
        """Register a new model version."""
        # Calculate model size
        size_mb = sum(f.stat().st_size for f in model_path.rglob("*") if f.is_file()) / (1024 * 1024)
        
        # Create registry directory for this model
        registry_model_path = settings.registry_path / name / version
        registry_model_path.mkdir(parents=True, exist_ok=True)
        
        # Copy model to registry
        if model_path.is_dir():
            shutil.copytree(model_path, registry_model_path, dirs_exist_ok=True)
        else:
            shutil.copy2(model_path, registry_model_path)
        
        # Store in database
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO models (name, version, backend, model_path, base_model, task, size_mb, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    version,
                    backend,
                    str(registry_model_path),
                    base_model,
                    task,
                    size_mb,
                    json.dumps(metadata or {}),
                    datetime.now().isoformat(),
                ),
            )
            await db.commit()
            model_id = cursor.lastrowid
            logger.success(f"Registered {name}:{version} (ID: {model_id})")
            return model_id

    async def list_models(self, name: Optional[str] = None) -> List[Dict]:
        """List all registered models."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if name:
                cursor = await db.execute(
                    "SELECT * FROM models WHERE name = ? ORDER BY created_at DESC", (name,)
                )
            else:
                cursor = await db.execute("SELECT * FROM models ORDER BY created_at DESC")
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_model(self, name: str, version: str = "latest") -> Optional[Dict]:
        """Get a specific model version."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if version == "latest":
                cursor = await db.execute(
                    "SELECT * FROM models WHERE name = ? ORDER BY created_at DESC LIMIT 1",
                    (name,),
                )
            else:
                cursor = await db.execute(
                    "SELECT * FROM models WHERE name = ? AND version = ?", (name, version)
                )
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def delete_model(self, name: str, version: Optional[str] = None):
        """Delete model(s) from registry."""
        async with aiosqlite.connect(self.db_path) as db:
            if version:
                # Delete specific version
                cursor = await db.execute(
                    "SELECT model_path FROM models WHERE name = ? AND version = ?",
                    (name, version),
                )
                row = await cursor.fetchone()
                if row:
                    model_path = Path(row[0])
                    if model_path.exists():
                        shutil.rmtree(model_path, ignore_errors=True)
                    await db.execute(
                        "DELETE FROM models WHERE name = ? AND version = ?", (name, version)
                    )
                    logger.success(f"Deleted {name}:{version}")
            else:
                # Delete all versions
                cursor = await db.execute("SELECT model_path FROM models WHERE name = ?", (name,))
                rows = await cursor.fetchall()
                for row in rows:
                    model_path = Path(row[0])
                    if model_path.exists():
                        shutil.rmtree(model_path.parent, ignore_errors=True)
                await db.execute("DELETE FROM models WHERE name = ?", (name,))
                logger.success(f"Deleted all versions of {name}")
            await db.commit()

    async def create_ab_test(self, name: str, model_a_id: int, model_b_id: int) -> int:
        """Create a new A/B test."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO ab_tests (name, model_a_id, model_b_id, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (name, model_a_id, model_b_id, datetime.now().isoformat()),
            )
            await db.commit()
            test_id = cursor.lastrowid
            logger.success(f"Created A/B test '{name}' (ID: {test_id})")
            return test_id

    async def get_ab_test(self, name: str) -> Optional[Dict]:
        """Get A/B test by name."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT t.*, 
                       ma.name as model_a_name, ma.version as model_a_version,
                       mb.name as model_b_name, mb.version as model_b_version
                FROM ab_tests t
                JOIN models ma ON t.model_a_id = ma.id
                JOIN models mb ON t.model_b_id = mb.id
                WHERE t.name = ?
                """,
                (name,),
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def list_ab_tests(self) -> List[Dict]:
        """List all A/B tests."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT t.*, 
                       ma.name as model_a_name, ma.version as model_a_version,
                       mb.name as model_b_name, mb.version as model_b_version
                FROM ab_tests t
                JOIN models ma ON t.model_a_id = ma.id
                JOIN models mb ON t.model_b_id = mb.id
                ORDER BY t.created_at DESC
                """
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def record_ab_result(
        self, test_id: int, model_id: int, metric_name: str, metric_value: float
    ):
        """Record an A/B test result."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO ab_results (test_id, model_id, metric_name, metric_value, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                (test_id, model_id, metric_name, metric_value, datetime.now().isoformat()),
            )
            await db.commit()

    async def get_ab_results(self, test_id: int) -> List[Dict]:
        """Get all results for an A/B test."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT r.*, m.name as model_name, m.version as model_version
                FROM ab_results r
                JOIN models m ON r.model_id = m.id
                WHERE r.test_id = ?
                ORDER BY r.timestamp DESC
                """,
                (test_id,),
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
