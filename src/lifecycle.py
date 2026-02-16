# src/lifecycle.py
"""
Application lifecycle management for standalone mode.
Orchestrates transitions between collection, training, and production phases.
"""

import os
import sys
import logging
import time
from typing import Optional, Dict, Callable

from src.first_run import FirstRunManager
from src.persistence import AppStateDB, ExecutionDataDB

logger = logging.getLogger(__name__)


class ApplicationLifecycle:
    """
    Manages application lifecycle through different phases:
    - COLLECTION: Gathering user interaction data (executions 0-9)
    - TRAINING: Processing data and training model (execution 10)
    - PRODUCTION: Using trained model for predictions (execution 11+)
    """

    def __init__(self, app_name: str, app_version: str = "1.0"):
        """
        Initialize application lifecycle manager.
        
        Args:
            app_name: Application identifier
            app_version: Version number
        """
        self.app_name = app_name
        self.app_version = app_version
        self.first_run_manager = FirstRunManager(app_name, app_version)
        self.app_state = None
        self.execution_id = None
        self.execution_db = None

    def initialize(self):
        """Initialize and get current application state."""
        logger.info(f"Initializing application: {self.app_name} v{self.app_version}")
        self.app_state = self.first_run_manager.get_or_initialize_state()
        self.execution_id = self._create_execution_id()
        self.execution_db = ExecutionDataDB(self.execution_id)
        logger.info(f"Application initialized. State: {self.app_state}")
        return self.app_state

    def _create_execution_id(self) -> str:
        """Create unique execution identifier."""
        import uuid
        from datetime import datetime
        return f"{self.app_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

    def get_current_phase(self) -> str:
        """Get current lifecycle phase."""
        return self.first_run_manager.get_current_phase()

    def get_execution_count(self) -> int:
        """Get current execution count (0-indexed)."""
        return self.first_run_manager.get_execution_count()

    def print_startup_message(self):
        """Print user-friendly startup message based on lifecycle phase."""
        state = self.app_state
        count = state["execution_count"]
        
        if count == 0:
            print("\n" + "="*60)
            print("  FIRST RUN INITIALIZATION")
            print("="*60)
            print(f"Setting up {self.app_name}...")
            print(f"This first run will initialize the application.")
            print("="*60 + "\n")
        
        elif count < 10 and not state["model_trained"]:
            print(f"[COLLECTION MODE] Run {count}/10 - Gathering user interaction data...")
        
        elif count == 10 and not state["model_trained"]:
            print("\n" + "="*60)
            print("  TRAINING MODE")
            print("="*60)
            print(f"Sufficient data collected. Training model now...")
            print("This may take 30-120 seconds depending on your system.")
            print("="*60 + "\n")
        
        elif state["model_trained"]:
            print(f"[PRODUCTION MODE] Using trained model for predictions...")

    def execute_collection_phase(self, collector_func: Callable) -> bool:
        """
        Execute data collection phase.
        
        Args:
            collector_func: Callable that performs data collection.
                          Should accept execution_db as argument.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Starting COLLECTION phase (execution {self.get_execution_count()})")
        self.print_startup_message()
        
        try:
            # Call the collector function with execution_db
            collector_func(self.execution_db)
            
            # Log execution
            self.first_run_manager.log_execution({
                "mode": "collection",
                "execution_number": self.get_execution_count(),
                "access_count": self.execution_db.get_access_count()
            })
            
            logger.info(f"Collection phase completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during collection phase: {e}", exc_info=True)
            return False

    def execute_training_phase(self, trainer_func: Callable) -> bool:
        """
        Execute model training phase.
        
        Args:
            trainer_func: Callable that trains the model.
                         Should handle loading data and training.
        
        Returns:
            True if successful, False otherwise
        """
        # Update state to indicate training
        self.first_run_manager.db.set_lifecycle_phase(self.app_name, "TRAINING")
        
        logger.info("Starting TRAINING phase")
        self.print_startup_message()
        
        try:
            # Call trainer function
            start_time = time.time()
            trainer_func()
            elapsed = time.time() - start_time
            
            # Mark model as trained
            self.first_run_manager.mark_model_trained()
            
            # Log execution
            self.first_run_manager.log_execution({
                "mode": "training",
                "training_time_seconds": elapsed,
                "execution_number": self.get_execution_count()
            })
            
            logger.info(f"Training phase completed in {elapsed:.2f}s")
            print(f"\n✓ Model trained successfully in {elapsed:.2f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"Error during training phase: {e}", exc_info=True)
            print(f"\n✗ Training failed: {e}")
            return False

    def execute_production_phase(self, predictor_func: Callable) -> bool:
        """
        Execute production (inference) phase.
        
        Args:
            predictor_func: Callable that performs prediction/prefetching.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Starting PRODUCTION phase (execution {self.get_execution_count()})")
        self.print_startup_message()
        
        try:
            # Call predictor function
            predictor_func()
            
            # Log execution
            self.first_run_manager.log_execution({
                "mode": "production",
                "execution_number": self.get_execution_count()
            })
            
            logger.info("Production phase completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during production phase: {e}", exc_info=True)
            return False

    def run(self, collector_func: Callable, trainer_func: Callable, predictor_func: Callable) -> bool:
        """
        Main application entry point. Routes to appropriate phase and executes.
        
        Args:
            collector_func: Function to call during COLLECTION phase
            trainer_func: Function to call during TRAINING phase
            predictor_func: Function to call during PRODUCTION phase
        
        Returns:
            True if execution successful, False otherwise
        """
        self.initialize()
        count = self.get_execution_count()
        
        logger.info(f"Application execution {count} starting...")
        
        # Determine which phase to execute
        if self.first_run_manager.should_train_model():
            # Training should happen at execution 10
            success = self.execute_training_phase(trainer_func)
        
        elif self.first_run_manager.is_production_mode():
            # Production mode for execution 11+
            success = self.execute_production_phase(predictor_func)
        
        else:
            # Collection mode for executions 0-9
            success = self.execute_collection_phase(collector_func)
        
        # Log final state
        if success:
            logger.info(f"Execution {count} completed successfully")
        else:
            logger.warning(f"Execution {count} completed with errors")
        
        return success

    def get_status_summary(self) -> str:
        """Get human-readable status summary."""
        state = self.app_state
        
        summary = f"""
Application Status Summary:
  - Name: {state['app_name']}
  - Version: {state['version']}
  - Execution Count: {state['execution_count']}
  - Lifecycle Phase: {state['lifecycle_phase']}
  - Model Trained: {'Yes' if state['model_trained'] else 'No'}
  - Last Execution: {state['last_execution']}
"""
        return summary

    def print_progress(self):
        """Print progress information to user."""
        state = self.app_state
        count = state["execution_count"]
        
        if not state["model_trained"]:
            progress = min(count, 10)
            print(f"\n[Progress] {progress}/10 collection iterations completed")
            if progress < 10:
                print(f"Remaining: {10 - progress} more collections needed before training")
        else:
            print("\n[Status] Model is trained and in production mode")
