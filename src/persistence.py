# src/persistence.py
"""
SQLite-based data persistence layer for the standalone application.
Handles first-run detection, execution tracking, and data collection storage.
"""

import sqlite3
import json
import os
import uuid
from datetime import datetime
from typing import Optional, Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class AppStateDB:
    """Manager for application state database."""

    def __init__(self, db_path: str = None):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to app_state.db. If None, uses data/app_state.db
        """
        if db_path is None:
            db_path = os.path.join("data", "app_state.db")
        
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema if not exists."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Application state table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_state (
                    id INTEGER PRIMARY KEY,
                    app_name TEXT UNIQUE,
                    execution_count INTEGER DEFAULT 0,
                    last_execution TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    lifecycle_phase TEXT DEFAULT 'COLLECTION',
                    model_trained INTEGER DEFAULT 0,
                    version TEXT,
                    metadata TEXT
                )
            """)
            
            # Execution log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS execution_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    execution_id TEXT UNIQUE,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    phase TEXT,
                    app_name TEXT,
                    files_accessed INTEGER,
                    files_prefetched INTEGER,
                    accuracy REAL,
                    data_file_path TEXT,
                    metadata TEXT
                )
            """)
            
            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")

    def init_app_state(self, app_name: str, version: str = "1.0") -> Dict:
        """
        Initialize app state for first run.
        
        Args:
            app_name: Application identifier
            version: Application version
            
        Returns:
            Dictionary with app state
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO app_state 
                    (app_name, execution_count, lifecycle_phase, model_trained, version)
                    VALUES (?, ?, ?, ?, ?)
                """, (app_name, 0, "COLLECTION", 0, version))
                conn.commit()
                logger.info(f"Initialized app state for {app_name}")
                return self.get_app_state(app_name)
        except sqlite3.Error as e:
            logger.error(f"Database error during init_app_state: {e}")
            raise

    def get_app_state(self, app_name: str) -> Optional[Dict]:
        """
        Get current application state.
        
        Args:
            app_name: Application identifier
            
        Returns:
            Dictionary with app state or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, app_name, execution_count, lifecycle_phase, 
                           model_trained, last_execution, version, metadata
                    FROM app_state
                    WHERE app_name = ?
                """, (app_name,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        "id": row["id"],
                        "app_name": row["app_name"],
                        "execution_count": row["execution_count"],
                        "lifecycle_phase": row["lifecycle_phase"],
                        "model_trained": bool(row["model_trained"]),
                        "last_execution": row["last_execution"],
                        "version": row["version"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
                    }
                return None
        except sqlite3.Error as e:
            logger.error(f"Database error during get_app_state: {e}")
            return None

    def increment_execution_count(self, app_name: str):
        """Increment execution counter."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE app_state
                    SET execution_count = execution_count + 1,
                        last_execution = CURRENT_TIMESTAMP
                    WHERE app_name = ?
                """, (app_name,))
                conn.commit()
                logger.debug(f"Incremented execution count for {app_name}")
        except sqlite3.Error as e:
            logger.error(f"Database error during increment_execution_count: {e}")
            raise

    def set_lifecycle_phase(self, app_name: str, phase: str):
        """
        Update lifecycle phase.
        
        Args:
            app_name: Application identifier
            phase: One of 'COLLECTION', 'TRAINING', 'PRODUCTION'
        """
        valid_phases = ["COLLECTION", "TRAINING", "PRODUCTION"]
        if phase not in valid_phases:
            raise ValueError(f"Invalid phase: {phase}. Must be one of {valid_phases}")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE app_state
                    SET lifecycle_phase = ?
                    WHERE app_name = ?
                """, (phase, app_name))
                conn.commit()
                logger.info(f"Set lifecycle phase to {phase} for {app_name}")
        except sqlite3.Error as e:
            logger.error(f"Database error during set_lifecycle_phase: {e}")
            raise

    def set_model_trained(self, app_name: str, trained: bool = True):
        """Mark model as trained."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE app_state
                    SET model_trained = ?, lifecycle_phase = ?
                    WHERE app_name = ?
                """, (int(trained), "PRODUCTION" if trained else "COLLECTION", app_name))
                conn.commit()
                logger.info(f"Set model_trained={trained} for {app_name}")
        except sqlite3.Error as e:
            logger.error(f"Database error during set_model_trained: {e}")
            raise

    def log_execution(self, app_name: str, phase: str, metadata: Dict = None) -> str:
        """
        Log an execution event.
        
        Returns:
            Execution ID for reference
        """
        execution_id = f"{app_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO execution_log
                    (execution_id, phase, app_name, metadata)
                    VALUES (?, ?, ?, ?)
                """, (execution_id, phase, app_name, json.dumps(metadata or {})))
                conn.commit()
                logger.debug(f"Logged execution: {execution_id}")
                return execution_id
        except sqlite3.Error as e:
            logger.error(f"Database error during log_execution: {e}")
            raise

    def get_recent_executions(self, app_name: str, limit: int = 10) -> List[Dict]:
        """Get recent execution logs."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM execution_log
                    WHERE app_name = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (app_name, limit))
                rows = cursor.fetchall()
                
                return [
                    {
                        "execution_id": row["execution_id"],
                        "timestamp": row["timestamp"],
                        "phase": row["phase"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
                    }
                    for row in rows
                ]
        except sqlite3.Error as e:
            logger.error(f"Database error during get_recent_executions: {e}")
            return []


class ExecutionDataDB:
    """Manager for per-execution collected data."""

    def __init__(self, execution_id: str, db_dir: str = None):
        """
        Initialize execution-specific data database.
        
        Args:
            execution_id: Unique execution identifier
            db_dir: Directory to store execution data. If None, uses data/collection/
        """
        if db_dir is None:
            db_dir = os.path.join("data", "collection")
        
        os.makedirs(db_dir, exist_ok=True)
        self.execution_id = execution_id
        self.db_path = os.path.join(db_dir, f"execution_{execution_id}.sqlite")
        self._init_db()

    def _init_db(self):
        """Initialize execution data schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_access_trace (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    file_path TEXT,
                    operation TEXT,
                    process_name TEXT,
                    file_size INTEGER,
                    additional_data TEXT
                )
            """)
            
            conn.commit()
            logger.info(f"Execution data DB initialized: {self.db_path}")

    def add_file_access(self, timestamp: float, file_path: str, operation: str,
                       process_name: str = None, file_size: int = None,
                       additional_data: Dict = None):
        """
        Record a file access event.
        
        Args:
            timestamp: Time of access (float/epoch)
            file_path: Path to file accessed
            operation: Type of operation (open, read, write, close, etc)
            process_name: Name of process accessing file
            file_size: Size of file in bytes
            additional_data: Additional metadata as dict
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO file_access_trace
                    (timestamp, file_path, operation, process_name, file_size, additional_data)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (timestamp, file_path, operation, process_name, file_size,
                      json.dumps(additional_data or {})))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Database error during add_file_access: {e}")
            raise

    def get_all_accesses(self) -> List[Dict]:
        """Retrieve all file accesses from this execution."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM file_access_trace ORDER BY timestamp")
                rows = cursor.fetchall()
                
                return [
                    {
                        "timestamp": row["timestamp"],
                        "file_path": row["file_path"],
                        "operation": row["operation"],
                        "process_name": row["process_name"],
                        "file_size": row["file_size"],
                        "additional_data": json.loads(row["additional_data"]) if row["additional_data"] else {}
                    }
                    for row in rows
                ]
        except sqlite3.Error as e:
            logger.error(f"Database error during get_all_accesses: {e}")
            return []

    def get_access_count(self) -> int:
        """Get total number of accesses recorded."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM file_access_trace")
                return cursor.fetchone()[0]
        except sqlite3.Error as e:
            logger.error(f"Database error during get_access_count: {e}")
            return 0
