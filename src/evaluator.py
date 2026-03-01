import json
import os
import re
import shlex
import subprocess
import time
from collections import OrderedDict
from pathlib import Path

import torch
import yaml

try:
    import psutil
except Exception:
    psutil = None

from src.metrics_tracker import MetricsTracker
from src.model import FilePrefetchLSTM
from src.utils import get_paths


def clear_cache():
    """Best-effort cache clear; no-op on unsupported platforms."""
    if os.name != "posix":
        print("[!] Cache clear skipped (requires Linux/Unix drop_caches support).")
        return
    print("[!] Clearing System Cache...")
    os.system("sync; echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null")


def measure_launch_time(app_command: str, timeout_seconds: int = 5) -> float:
    start_time = time.perf_counter()
    try:
        cmd_parts = shlex.split(app_command)
        subprocess.run(
            cmd_parts,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        pass
    except Exception:
        return 0.0
    return max(time.perf_counter() - start_time, 0.0)


def parse_trace_events(trace_path: str):
    """
    Parse strace lines into (timestamp_seconds, filepath).
    Supports both timestamped and non-timestamped strace output.
    """
    events = []
    open_regex = re.compile(r'openat\(.*?"(.*?)"')
    ts_regex = re.compile(r"(\d{2}):(\d{2}):(\d{2})\.(\d+)")

    with open(trace_path, "r", errors="ignore") as f:
        fallback_t = 0.0
        for line in f:
            file_match = open_regex.search(line)
            if not file_match:
                continue

            filepath = file_match.group(1)
            if not filepath.startswith("/"):
                continue
            if filepath.startswith("/dev") or filepath.startswith("/proc"):
                continue

            ts_match = ts_regex.search(line)
            if ts_match:
                h, m, s, micros = ts_match.groups()
                timestamp = (
                    int(h) * 3600
                    + int(m) * 60
                    + int(s)
                    + float(f"0.{micros}")
                )
            else:
                fallback_t += 0.001
                timestamp = fallback_t

            events.append((timestamp, filepath))

    return events


def get_file_size(filepath: str, fallback_size_bytes: int, cache: dict) -> int:
    if filepath in cache:
        return cache[filepath]

    size = fallback_size_bytes
    try:
        if os.path.exists(filepath):
            size = max(os.path.getsize(filepath), 1)
    except Exception:
        size = fallback_size_bytes

    cache[filepath] = size
    return size


def load_model_and_vocab(vocab_path: str, model_path: str, cfg: dict):
    with open(vocab_path, "r") as f:
        vocab = json.load(f)

    idx_to_file = {v: k for k, v in vocab.items()}
    model = FilePrefetchLSTM(
        len(vocab) + 1,
        cfg["model"]["embedding_dim"],
        cfg["model"]["hidden_dim"],
    )
    model.load_state_dict(torch.load(model_path, map_location="cpu"))
    model.eval()

    return model, vocab, idx_to_file


def update_cache_with_eviction(cache: OrderedDict, item: str, entry: dict, cache_size: int, tracker: MetricsTracker, caused_by_prefetch: bool):
    if item in cache:
        cache.pop(item, None)
        cache[item] = entry
        return

    if cache_size > 0 and len(cache) >= cache_size:
        evicted_item, evicted_entry = cache.popitem(last=False)
        tracker.record_eviction(
            evicted_item,
            caused_by_prefetch=caused_by_prefetch,
            evicted_prefetch_id=evicted_entry.get("prefetch_id"),
        )

    cache[item] = entry


def evaluate_workload(workload_name: str, trace_path: str, vocab_path: str, model_path: str, cfg: dict):
    events = parse_trace_events(trace_path)
    if not events:
        raise RuntimeError(f"No valid trace events found in {trace_path}")

    model, vocab, idx_to_file = load_model_and_vocab(vocab_path, model_path, cfg)
    tracker = MetricsTracker(workload_name)

    model_size_mb = 0.0
    try:
        model_size_mb = os.path.getsize(model_path) / (1024 * 1024)
    except Exception:
        model_size_mb = 0.0
    tracker.set_model_size(model_size_mb)

    eval_cfg = cfg.get("evaluation", {})
    seq_length = int(cfg["model"].get("seq_length", 30))
    cache_size = int(eval_cfg.get("cache_size", 128))
    fallback_size_bytes = int(eval_cfg.get("default_item_size_bytes", 4096))

    lru_cache = OrderedDict()
    size_cache = {}
    context_ids = []

    process = psutil.Process(os.getpid()) if psutil else None

    for timestamp, filepath in events:
        file_size = get_file_size(filepath, fallback_size_bytes, size_cache)

        consumed_prefetch_id = None
        if filepath in lru_cache:
            cache_entry = lru_cache.pop(filepath)
            consumed_prefetch_id = cache_entry.get("prefetch_id")
            cache_entry["prefetch_id"] = None
            lru_cache[filepath] = cache_entry
            cache_hit = True
        else:
            cache_hit = False
            update_cache_with_eviction(
                lru_cache,
                filepath,
                {"prefetch_id": None, "size": file_size},
                cache_size,
                tracker,
                caused_by_prefetch=False,
            )

        tracker.record_access(
            filepath,
            timestamp,
            cache_hit=cache_hit,
            consumed_prefetch_id=consumed_prefetch_id,
        )

        file_id = vocab.get(filepath)
        if file_id is not None:
            context_ids.append(file_id)

        if len(context_ids) < seq_length:
            continue

        input_ids = context_ids[-seq_length:]
        input_tensor = torch.tensor([input_ids], dtype=torch.long)

        cpu_before = process.cpu_percent(interval=None) if process else 0.0
        infer_start = time.perf_counter()

        with torch.no_grad():
            output = model(input_tensor)
            predicted_id = torch.argmax(output, dim=1).item()

        infer_ms = (time.perf_counter() - infer_start) * 1000.0
        cpu_after = process.cpu_percent(interval=None) if process else 0.0
        cpu_used = max(cpu_after - cpu_before, 0.0)

        tracker.record_inference(infer_ms, cpu_used)

        predicted_file = idx_to_file.get(predicted_id)
        if not predicted_file:
            continue

        predicted_size = get_file_size(predicted_file, fallback_size_bytes, size_cache)
        prefetch_id = tracker.record_prefetch(
            predicted_file,
            timestamp + 1e-9,
            predicted_size,
        )

        update_cache_with_eviction(
            lru_cache,
            predicted_file,
            {"prefetch_id": prefetch_id, "size": predicted_size},
            cache_size,
            tracker,
            caused_by_prefetch=True,
        )

    return tracker.to_dict()


def resolve_workloads(cfg: dict, paths: dict):
    eval_cfg = cfg.get("evaluation", {})
    workloads_cfg = eval_cfg.get("workloads", [])

    if not workloads_cfg:
        return [
            {
                "name": cfg["system"].get("app_name", "default"),
                "trace_path": paths["raw_log"],
                "vocab_path": paths["vocab"],
                "model_path": paths["model"],
            }
        ]

    workloads = []
    for index, workload in enumerate(workloads_cfg, start=1):
        if isinstance(workload, str):
            workloads.append(
                {
                    "name": f"workload_{index}",
                    "trace_path": workload,
                    "vocab_path": paths["vocab"],
                    "model_path": paths["model"],
                }
            )
            continue

        workloads.append(
            {
                "name": workload.get("name", f"workload_{index}"),
                "trace_path": workload.get("trace_path", paths["raw_log"]),
                "vocab_path": workload.get("vocab_path", paths["vocab"]),
                "model_path": workload.get("model_path", paths["model"]),
            }
        )

    return workloads


def compute_speedup(cfg: dict):
    eval_cfg = cfg.get("evaluation", {})
    if not eval_cfg.get("measure_speedup", True):
        return {"cold_time_sec": 0.0, "prefetched_time_sec": 0.0, "speedup_percent": 0.0, "enabled": False}

    app_name = cfg.get("system", {}).get("target_app", "")
    if not app_name:
        return {"cold_time_sec": 0.0, "prefetched_time_sec": 0.0, "speedup_percent": 0.0, "enabled": False}

    clear_cache()
    cold_time = measure_launch_time(app_name)

    clear_cache()
    prefetched_time = measure_launch_time(app_name)

    speedup_percent = 0.0
    if cold_time > 0:
        speedup_percent = ((cold_time - prefetched_time) / cold_time) * 100.0

    return {
        "cold_time_sec": cold_time,
        "prefetched_time_sec": prefetched_time,
        "speedup_percent": speedup_percent,
        "enabled": True,
    }


def print_final_summary(result: dict):
    aggregate = result["aggregate"]
    metrics = aggregate["metrics"]
    bytes_data = aggregate["bytes"]
    speedup = result.get("speedup", {})

    print("\n" + "=" * 70)
    print("FINAL EVALUATION REPORT")
    print("=" * 70)
    print(f"Speedup (%)              : {speedup.get('speedup_percent', 0.0):.2f}")
    print(f"Accuracy (%)             : {metrics['accuracy'] * 100:.2f}")
    print(f"Coverage (%)             : {metrics['coverage'] * 100:.2f}")
    print(f"Precision                : {metrics['precision']:.4f}")
    print(f"Recall                   : {metrics['recall']:.4f}")
    print(f"F1-score                 : {metrics['f1_score']:.4f}")
    print(f"Timeliness (%)           : {metrics['timeliness'] * 100:.2f}")
    print(f"Overprediction Rate (%)  : {metrics['overprediction_rate'] * 100:.2f}")
    print(f"Bandwidth Overhead (MB)  : {bytes_data['bandwidth_overhead_mb']:.4f}")
    print(f"Inference Latency (ms)   : {metrics['inference_time_per_prediction_ms']:.4f}")
    print(f"Model Size (MB)          : {metrics['model_size_mb']:.4f}")
    print("=" * 70)


def evaluate():
    cfg, paths = get_paths()
    print("--- EVALUATION STARTED ---")

    workloads = resolve_workloads(cfg, paths)
    workload_summaries = []

    for workload in workloads:
        trace_path = workload["trace_path"]
        if not os.path.exists(trace_path):
            print(f"[!] Skipping {workload['name']} (trace missing): {trace_path}")
            continue

        if not os.path.exists(workload["vocab_path"]):
            print(f"[!] Skipping {workload['name']} (vocab missing): {workload['vocab_path']}")
            continue

        if not os.path.exists(workload["model_path"]):
            print(f"[!] Skipping {workload['name']} (model missing): {workload['model_path']}")
            continue

        print(f"[*] Evaluating workload: {workload['name']}")
        summary = evaluate_workload(
            workload_name=workload["name"],
            trace_path=trace_path,
            vocab_path=workload["vocab_path"],
            model_path=workload["model_path"],
            cfg=cfg,
        )
        workload_summaries.append(summary)

    if not workload_summaries:
        print("[!] No workloads could be evaluated. Check trace/model/vocab paths.")
        return

    aggregate = MetricsTracker.aggregate("all_workloads", workload_summaries)
    speedup = compute_speedup(cfg)

    output = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "workloads": workload_summaries,
        "aggregate": aggregate,
        "speedup": speedup,
    }

    output_path = cfg.get("evaluation", {}).get(
        "metrics_output_path",
        os.path.join("data", "processed", "evaluation_metrics.json"),
    )
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"[*] Metrics JSON saved to: {output_file}")
    print_final_summary(output)


if __name__ == "__main__":
    evaluate()
