# src/first_run.py
"""
First-run detection and initialization logic for standalone application.
"""

import os
import logging
from typing import Dict
from src.persistence import AppStateDB

logger = logging.getLogger(__name__)


class FirstRunManager:
    """Manages first-run detection and initialization."""

    def __init__(self, app_name: str, app_version: str = "1.0", db_path: str = None):
        """
        Initialize first-run manager.
        
        Args:
            app_name: Application identifier (e.g., 'prefetcher', 'gimp', 'chrome')
            app_version: Version number
            db_path: Path to app_state.db (optional)
        """
        self.app_name = app_name
        self.app_version = app_version
        self.db = AppStateDB(db_path)

    def is_first_run(self) -> bool:
        """
        Check if this is the first run of the application.
        
        Returns:
            True if first run, False otherwise
        """
        state = self.db.get_app_state(self.app_name)
        return state is None

    def get_or_initialize_state(self) -> Dict:
        """
        Get application state, initializing if needed.
        
        Returns:
            Application state dictionary with keys:
            - app_name: Application identifier
            - execution_count: Number of times app has run
            - lifecycle_phase: 'COLLECTION', 'TRAINING', or 'PRODUCTION'
            - model_trained: Boolean indicating if model is trained
            - version: Application version
        """
        state = self.db.get_app_state(self.app_name)
        
        if state is None:
            logger.info(f"First run detected for {self.app_name}. Initializing...")
            state = self.db.init_app_state(self.app_name, self.app_version)
            logger.info(f"Initialized state: {state}")
        
        return state

    def should_collect_data(self) -> bool:
        """
        Determine if data collection should occur this run.
        
        Returns:
            True if execution_count < 10 and model_trained = False
        """
        state = self.get_or_initialize_state()
        should_collect = (
            state["execution_count"] < 10 and
            not state["model_trained"]
        )
        
        logger.info(
            f"Data collection: {should_collect} "
            f"(count={state['execution_count']}, trained={state['model_trained']})"
        )
        
        return should_collect

    def should_train_model(self) -> bool:
        """
        Determine if model training should occur.
        
        Returns:
            True if execution_count == 10 and model_trained = False
        """
        state = self.get_or_initialize_state()
        should_train = (
            state["execution_count"] == 10 and
            not state["model_trained"]
        )
        
        logger.info(f"Model training: {should_train} (count={state['execution_count']})")
        
        return should_train

    def is_production_mode(self) -> bool:
        """
        Check if application is in production mode (model trained).
        
        Returns:
            True if model_trained = True
        """
        state = self.get_or_initialize_state()
        is_prod = state["model_trained"]
        logger.info(f"Production mode: {is_prod}")
        return is_prod

    def get_current_phase(self) -> str:
        """
        Get current application lifecycle phase.
        
        Returns:
            One of 'COLLECTION', 'TRAINING', 'PRODUCTION'
        """
        state = self.get_or_initialize_state()
        return state["lifecycle_phase"]

    def get_execution_count(self) -> int:
        """Get current execution count."""
        state = self.get_or_initialize_state()
        return state["execution_count"]

    def log_execution(self, metadata: Dict = None) -> str:
        """
        Log this execution and increment counter.
        
        Args:
            metadata: Additional metadata to log
            
        Returns:
            Execution ID
        """
        state = self.get_or_initialize_state()
        phase = state["lifecycle_phase"]
        
        execution_id = self.db.log_execution(self.app_name, phase, metadata)
        self.db.increment_execution_count(self.app_name)
        
        logger.info(f"Execution logged: {execution_id}")
        
        return execution_id

    def mark_model_trained(self):
        """Mark the model as trained and transition to PRODUCTION phase."""
        self.db.set_model_trained(self.app_name, trained=True)
        logger.info(f"Model marked as trained. Transitioning to PRODUCTION phase.")

    def reset_state(self):
        """
        Reset application state to first-run.
        
        WARNING: This will clear all execution history and model status.
        Used for debugging/testing purposes.
        """
        logger.warning(f"Resetting state for {self.app_name}")
        self.db.set_lifecycle_phase(self.app_name, "COLLECTION")
        self.db.set_model_trained(self.app_name, False)
        # Note: Does NOT reset execution_count to allow history tracking


def setup_logging(log_level=logging.INFO):
    """
    Configure logging for the application.
    
    Args:
        log_level: Logging level (default: INFO)
    """
    os.makedirs("logs", exist_ok=True)
    
    log_file = os.path.join("logs", "app.log")
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
