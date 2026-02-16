# app_standalone.py
"""
Standalone application entry point for Windows EXE.

This is the main entry point for PyInstaller. It orchestrates:
1. First-run detection
2. Data collection phase
3. Model training phase
4. Production/prediction phase

Usage:
    python app_standalone.py              # Normal execution
    python app_standalone.py --reset      # Reset to first-run state
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Ensure src module can be imported (works both in dev and packaged exe)
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.first_run import setup_logging
from src.lifecycle import ApplicationLifecycle
from src.persistence import ExecutionDataDB

# Import the actual application functions
from src.collector import collect_traces
from src.trainer import train_model
from src.prefetcher import run_prefetcher


def create_collection_wrapper(app_name: str) -> callable:
    """
    Create a wrapper around collect_traces that works with ExecutionDataDB.
    
    Args:
        app_name: Application name for logging
    
    Returns:
        Callable that accepts execution_db parameter
    """
    def collection_handler(execution_db):
        """
        Execute data collection.
        
        Args:
            execution_db: ExecutionDataDB instance for storing collected data
        """
        print(f"\n[*] Collecting data for {app_name}...")
        
        # Call original collector (will write to files as before)
        # For now, this calls the unmodified collect_traces()
        # In production, you might enhance this to write to execution_db
        try:
            collect_traces()
            print(f"[✓] Data collection completed")
        except Exception as e:
            print(f"[!] Data collection error: {e}")
            raise
    
    return collection_handler


def create_training_wrapper(app_name: str) -> callable:
    """
    Create a wrapper around train_model.
    
    Args:
        app_name: Application name for logging
    
    Returns:
        Callable with no parameters
    """
    def training_handler():
        """Execute model training."""
        print(f"\n[*] Training model for {app_name}...")
        print("This may take 30-120 seconds...\n")
        
        try:
            train_model()
            print(f"\n[✓] Model training completed")
        except Exception as e:
            print(f"[!] Training error: {e}")
            raise
    
    return training_handler


def create_production_wrapper(app_name: str) -> callable:
    """
    Create a wrapper around run_prefetcher.
    
    Args:
        app_name: Application name for logging
    
    Returns:
        Callable with no parameters
    """
    def production_handler():
        """Execute production prefetcher."""
        print(f"\n[*] Running prefetcher for {app_name}...")
        
        try:
            run_prefetcher()
            print(f"\n[✓] Prefetcher completed")
        except Exception as e:
            print(f"[!] Prefetcher error: {e}")
            raise
    
    return production_handler


def main():
    """Main application entry point."""
    
    # Setup logging
    logger = setup_logging(logging.INFO)
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="AI File Prefetcher - Standalone Application")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset application state (WARNING: clears all execution history)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--app-name",
        default="prefetcher",
        help="Application name (default: prefetcher)"
    )
    parser.add_argument(
        "--version",
        default="1.0",
        help="Application version (default: 1.0)"
    )
    
    args = parser.parse_args()
    
    # Adjust logging level
    if args.debug:
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    try:
        # Create lifecycle manager
        lifecycle = ApplicationLifecycle(args.app_name, args.version)
        
        # Check if reset requested
        if args.reset:
            logger.warning("Resetting application state...")
            lifecycle.first_run_manager.reset_state()
            print("\n[✓] Application state reset. Next run will be treated as first-run.")
            return 0
        
        # Create handler functions
        collector_handler = create_collection_wrapper(args.app_name)
        trainer_handler = create_training_wrapper(args.app_name)
        production_handler = create_production_wrapper(args.app_name)
        
        # Execute application
        success = lifecycle.run(
            collector_func=collector_handler,
            trainer_func=trainer_handler,
            predictor_func=production_handler
        )
        
        # Print status
        print(lifecycle.get_status_summary())
        lifecycle.print_progress()
        
        # Return appropriate exit code
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n[!] Application error: {e}")
        print("Check 'logs/app.log' for details.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
