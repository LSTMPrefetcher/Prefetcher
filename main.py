# main.py
import argparse
import sys
from src.collector import collect_traces
from src.preprocessor import preprocess
from src.trainer import train_model
from src.prefetcher import run_prefetcher
from src.evaluator import evaluate

def main():
    parser = argparse.ArgumentParser(description="AI File Prefetcher Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Define commands matching your roadmap phases
    subparsers.add_parser("collect", help="Phase 2: Collect strace logs from the app")
    subparsers.add_parser("process", help="Phase 3: Clean logs and build vocabulary")
    subparsers.add_parser("train", help="Phase 4: Train the LSTM model")
    subparsers.add_parser("prefetch", help="Phase 5: Run the prefetcher engine")
    subparsers.add_parser("evaluate", help="Phase 6: Compare launch times")

    args = parser.parse_args()

    if args.command == "collect":
        collect_traces()
    elif args.command == "process":
        preprocess()
    elif args.command == "train":
        train_model()
    elif args.command == "prefetch":
        run_prefetcher()
    elif args.command == "evaluate":
        evaluate()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
