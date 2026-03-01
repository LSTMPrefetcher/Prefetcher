"""Standalone application entry point for Windows EXE and source CLI usage."""

import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

# Ensure src module can be imported (works both in dev and packaged exe)
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.collector import collect_traces
from src.first_run import FirstRunManager, setup_logging
from src.lifecycle import ApplicationLifecycle
from src.trainer import train_model
from src.prefetcher import run_prefetcher


def check_admin_privileges():
    """
    Check if running with administrator privileges.
    Returns True if running as admin, False otherwise.
    """
    try:
        import ctypes
        is_admin = ctypes.windll.shell.IsUserAnAdmin()
        return is_admin
    except Exception:
        # If we can't check, assume we're not admin (safer assumption)
        return False


def request_admin_privileges():
    """
    Request admin privileges and relaunch if not already admin.
    
    Note: This is a backup in case the PyInstaller manifest doesn't work.
    The manifest should handle this automatically.
    """
    import ctypes

    print("\n" + "="*70)
    print("  ADMINISTRATOR PRIVILEGES REQUIRED")
    print("="*70)
    print("\nThis application requires administrator privileges to:")
    print("  • Monitor file system operations")
    print("  • Load files into memory cache")
    print("  • Optimize system performance")
    print("\nPlease:")
    print("  1. Right-click AiFilePrefetcher.exe")
    print("  2. Select 'Run as administrator'")
    print("  3. Click 'Yes' on the User Account Control dialog")
    print("\n" + "="*70 + "\n")
    
    # Try to automatically relaunch with elevated privileges
    try:
        # Re-run the script with admin privileges
        ctypes.windll.shell.ShellExecuteEx(
            lpVerb='runas',
            lpFile=sys.executable,
            lpParameters=f'"{sys.argv[0]}" {" ".join(sys.argv[1:])}',
            nShow=5  # SW_SHOW
        )
    except Exception as e:
        print(f"Note: Could not automatically elevate privileges ({e})")
        print("Please manually run as administrator (right-click → Run as administrator)")
    
    sys.exit(1)


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


def is_frozen_executable() -> bool:
    return bool(getattr(sys, "frozen", False))


def print_quick_manual():
    print("\n" + "=" * 70)
    print("AI FILE PREFETCHER - QUICK USER MANUAL")
    print("=" * 70)
    print("1) Run once per session:      AiFilePrefetcher.exe run")
    print("2) Check lifecycle status:    AiFilePrefetcher.exe status")
    print("3) Reset training lifecycle:  AiFilePrefetcher.exe reset")
    print("4) Health checks:             AiFilePrefetcher.exe doctor")
    print("\nLifecycle:")
    print("  - Runs 1-10 : COLLECTION")
    print("  - Next run  : TRAINING")
    print("  - Later runs: PRODUCTION")
    if is_frozen_executable():
        print("\nDependency mode: Bundled EXE (no Python/pip install required).")
    else:
        print("\nDependency mode: Source mode. Run 'setup-deps' once if needed.")
    print("=" * 70)


def install_dependencies(cpu_torch: bool = False) -> int:
    if is_frozen_executable():
        print("[✓] EXE mode detected. Dependencies are already bundled.")
        print("[✓] No pip installation is required for end users.")
        return 0

    requirements_path = os.path.join(current_dir, "requirements.txt")
    if not os.path.exists(requirements_path):
        print(f"[!] requirements.txt not found at: {requirements_path}")
        return 1

    print("[*] Installing Python dependencies from requirements.txt...")
    cmd = [sys.executable, "-m", "pip", "install", "-r", requirements_path]
    if subprocess.run(cmd, check=False).returncode != 0:
        print("[!] Dependency installation failed.")
        return 1

    if cpu_torch:
        print("[*] Installing CPU-only PyTorch (optional optimization)...")
        torch_cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "torch",
            "--index-url",
            "https://download.pytorch.org/whl/cpu",
        ]
        if subprocess.run(torch_cmd, check=False).returncode != 0:
            print("[!] CPU-only PyTorch install failed (continuing with existing torch package).")

    print("[✓] Dependencies installed successfully.")
    return 0


def run_doctor(app_name: str, app_version: str) -> int:
    print("\n" + "=" * 70)
    print("SYSTEM HEALTH CHECK (DOCTOR)")
    print("=" * 70)

    checks = []

    for path in ["config", "data", "logs"]:
        abs_path = os.path.join(current_dir, path)
        exists = os.path.exists(abs_path)
        checks.append((f"Path exists: {path}", exists))
        if not exists:
            try:
                os.makedirs(abs_path, exist_ok=True)
                checks.append((f"Path created: {path}", True))
            except Exception:
                checks.append((f"Path created: {path}", False))

    config_file = os.path.join(current_dir, "config", "config.yaml")
    checks.append(("Config file present", os.path.exists(config_file)))

    writable_probe = os.path.join(current_dir, "logs", ".write_test")
    try:
        with open(writable_probe, "w") as f:
            f.write("ok")
        os.remove(writable_probe)
        checks.append(("Workspace writable", True))
    except Exception:
        checks.append(("Workspace writable", False))

    frm = FirstRunManager(app_name, app_version)
    state = frm.get_or_initialize_state()
    checks.append(("State DB initialized", bool(state)))

    all_passed = True
    for label, status in checks:
        icon = "[✓]" if status else "[✗]"
        print(f"{icon} {label}")
        all_passed = all_passed and status

    print("=" * 70)
    return 0 if all_passed else 1


def show_status(app_name: str, app_version: str):
    frm = FirstRunManager(app_name, app_version)
    state = frm.get_or_initialize_state()
    recent = frm.db.get_recent_executions(app_name, limit=5)

    print("\n" + "=" * 70)
    print("APPLICATION STATUS")
    print("=" * 70)
    print(f"Name            : {state['app_name']}")
    print(f"Version         : {state['version']}")
    print(f"Execution Count : {state['execution_count']}")
    print(f"Lifecycle Phase : {state['lifecycle_phase']}")
    print(f"Model Trained   : {'Yes' if state['model_trained'] else 'No'}")
    print(f"Last Execution  : {state['last_execution']}")
    print("\nRecent Runs:")
    if not recent:
        print("  - No execution history yet")
    else:
        for item in recent:
            print(f"  - {item['timestamp']} | {item['phase']} | {item['execution_id']}")
    print("=" * 70)


def execute_pipeline_once(app_name: str, app_version: str, logger) -> int:
    if not check_admin_privileges():
        logger.warning("Not running with admin privileges. Attempting to elevate...")
        request_admin_privileges()
        return 1

    lifecycle = ApplicationLifecycle(app_name, app_version)
    collector_handler = create_collection_wrapper(app_name)
    trainer_handler = create_training_wrapper(app_name)
    production_handler = create_production_wrapper(app_name)

    success = lifecycle.run(
        collector_func=collector_handler,
        trainer_func=trainer_handler,
        predictor_func=production_handler,
    )

    print(lifecycle.get_status_summary())
    lifecycle.print_progress()

    return 0 if success else 1


def interactive_menu(args, logger) -> int:
    while True:
        print("\n" + "=" * 70)
        print("AI FILE PREFETCHER - USER CLI")
        print("=" * 70)
        print("1) Run prefetcher lifecycle now")
        print("2) Show current status")
        print("3) Run doctor checks")
        print("4) Reset lifecycle state")
        print("5) Install dependencies (source mode only)")
        print("6) Show quick manual")
        print("0) Exit")

        choice = input("Select an option [0-6]: ").strip()
        if choice == "1":
            return execute_pipeline_once(args.app_name, args.version, logger)
        if choice == "2":
            show_status(args.app_name, args.version)
            continue
        if choice == "3":
            run_doctor(args.app_name, args.version)
            continue
        if choice == "4":
            lifecycle = ApplicationLifecycle(args.app_name, args.version)
            lifecycle.first_run_manager.reset_state()
            print("\n[✓] Application state reset. Next run starts collection flow.")
            continue
        if choice == "5":
            install_dependencies(cpu_torch=False)
            continue
        if choice == "6":
            print_quick_manual()
            continue
        if choice == "0":
            print("[✓] Exiting.")
            return 0
        print("[!] Invalid choice. Please enter a number from 0 to 6.")


def main():
    """Main application entry point."""

    # Setup logging
    logger = setup_logging(logging.INFO)

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="AI File Prefetcher - User-friendly standalone CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("run", help="Run one lifecycle iteration (collection/training/production)")
    subparsers.add_parser("status", help="Show lifecycle status and recent runs")
    subparsers.add_parser("doctor", help="Run health checks (paths, config, DB, write access)")
    subparsers.add_parser("reset", help="Reset lifecycle state to collection mode")
    deps_parser = subparsers.add_parser("setup-deps", help="Install Python dependencies (source mode)")
    deps_parser.add_argument("--cpu-torch", action="store_true", help="Install CPU-only PyTorch wheel")
    subparsers.add_parser("guide", help="Show quick usage manual")

    parser.add_argument("--interactive", action="store_true", help="Open interactive CLI menu")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Backward-compatible flag for reset command"
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
        help="Application version profile (default: 1.0)"
    )

    args = parser.parse_args()

    # Adjust logging level
    if args.debug:
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")

    if args.reset and args.command is None:
        args.command = "reset"

    if args.interactive and args.command is None:
        return interactive_menu(args, logger)

    if args.command is None:
        return interactive_menu(args, logger)

    try:
        if args.command == "run":
            return execute_pipeline_once(args.app_name, args.version, logger)

        if args.command == "status":
            show_status(args.app_name, args.version)
            return 0

        if args.command == "doctor":
            return run_doctor(args.app_name, args.version)

        if args.command == "reset":
            lifecycle = ApplicationLifecycle(args.app_name, args.version)
            logger.warning("Resetting application state...")
            lifecycle.first_run_manager.reset_state()
            print("\n[✓] Application state reset. Next run starts collection flow.")
            return 0

        if args.command == "setup-deps":
            return install_dependencies(cpu_torch=args.cpu_torch)

        if args.command == "guide":
            print_quick_manual()
            return 0

        print("[!] Unknown command. Use --help to see available commands.")
        return 1

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n[!] Application error: {e}")
        print("Check 'logs/app.log' for details.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
