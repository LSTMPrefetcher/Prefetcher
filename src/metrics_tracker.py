from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class PrefetchRecord:
    item: str
    timestamp: float
    size_bytes: int
    used: bool = False
    evicted: bool = False
    useful: bool = False


class MetricsTracker:
    def __init__(self, workload_name: str):
        self.workload_name = workload_name

        self.total_prefetches = 0
        self.useful_prefetches = 0
        self.timely_prefetches = 0
        self.total_cache_misses = 0
        self.covered_misses = 0

        self.tp = 0
        self.fp = 0
        self.fn = 0

        self.total_prefetch_bytes = 0
        self.useful_bytes = 0

        self.pollution = 0
        self.total_evictions = 0
        self.evictions_caused_by_prefetch = 0

        self.total_inference_time_ms = 0.0
        self.total_inference_cpu_pct = 0.0
        self.inference_calls = 0
        self.model_size_mb = 0.0

        self.total_accesses = 0
        self.cache_hits = 0

        self.prefetch_records: Dict[int, PrefetchRecord] = {}
        self.next_prefetch_id = 1
        self.active_prefetch_for_item: Dict[str, int] = {}
        self.pollution_candidates: Dict[str, bool] = {}

    def set_model_size(self, model_size_mb: float):
        self.model_size_mb = float(max(model_size_mb, 0.0))

    def record_inference(self, inference_time_ms: float, cpu_percent: float):
        self.total_inference_time_ms += max(float(inference_time_ms), 0.0)
        self.total_inference_cpu_pct += max(float(cpu_percent), 0.0)
        self.inference_calls += 1

    def record_prefetch(self, item: str, timestamp: float, size_bytes: int) -> int:
        self.total_prefetches += 1
        self.total_prefetch_bytes += max(int(size_bytes), 0)

        prefetch_id = self.next_prefetch_id
        self.next_prefetch_id += 1

        self.prefetch_records[prefetch_id] = PrefetchRecord(
            item=item,
            timestamp=float(timestamp),
            size_bytes=max(int(size_bytes), 0),
        )
        self.active_prefetch_for_item[item] = prefetch_id
        return prefetch_id

    def record_access(self, item: str, timestamp: float, cache_hit: bool, consumed_prefetch_id: Optional[int] = None):
        self.total_accesses += 1
        if cache_hit:
            self.cache_hits += 1
        else:
            self.total_cache_misses += 1
            if self.pollution_candidates.get(item):
                self.pollution += 1
                self.pollution_candidates.pop(item, None)

        if consumed_prefetch_id is not None and consumed_prefetch_id in self.prefetch_records:
            record = self.prefetch_records[consumed_prefetch_id]
            if not record.useful:
                record.used = True
                record.useful = True
                self.useful_prefetches += 1
                self.tp += 1
                self.useful_bytes += record.size_bytes
                self.covered_misses += 1

                if record.timestamp < float(timestamp):
                    self.timely_prefetches += 1

                if self.active_prefetch_for_item.get(item) == consumed_prefetch_id:
                    self.active_prefetch_for_item.pop(item, None)
        else:
            self.fn += 1

    def record_eviction(self, evicted_item: str, caused_by_prefetch: bool, evicted_prefetch_id: Optional[int] = None):
        self.total_evictions += 1

        if caused_by_prefetch:
            self.evictions_caused_by_prefetch += 1
            self.pollution_candidates[evicted_item] = True

        if evicted_prefetch_id is not None and evicted_prefetch_id in self.prefetch_records:
            record = self.prefetch_records[evicted_prefetch_id]
            if not record.useful:
                record.evicted = True

            if self.active_prefetch_for_item.get(evicted_item) == evicted_prefetch_id:
                self.active_prefetch_for_item.pop(evicted_item, None)

    @staticmethod
    def _safe_div(numerator: float, denominator: float) -> float:
        return float(numerator) / float(denominator) if denominator else 0.0

    def to_dict(self) -> Dict[str, Any]:
        self.fp = max(self.total_prefetches - self.tp, 0)

        accuracy = self._safe_div(self.useful_prefetches, self.total_prefetches)
        coverage = self._safe_div(self.useful_prefetches, self.total_cache_misses)

        precision = self._safe_div(self.tp, self.tp + self.fp)
        recall = self._safe_div(self.tp, self.tp + self.fn)
        f1 = self._safe_div(2 * precision * recall, precision + recall)

        timeliness = self._safe_div(self.timely_prefetches, self.useful_prefetches)
        overprediction_rate = self._safe_div(self.fp, self.total_prefetches)

        bandwidth_overhead_bytes = max(self.total_prefetch_bytes - self.useful_bytes, 0)
        bandwidth_overhead_mb = bandwidth_overhead_bytes / (1024 * 1024)

        pollution_rate = self._safe_div(self.pollution, self.total_evictions)

        inference_time_per_prediction_ms = self._safe_div(self.total_inference_time_ms, self.inference_calls)
        inference_cpu_usage_percent = self._safe_div(self.total_inference_cpu_pct, self.inference_calls)

        return {
            "workload": self.workload_name,
            "counts": {
                "total_prefetches": self.total_prefetches,
                "useful_prefetches": self.useful_prefetches,
                "timely_prefetches": self.timely_prefetches,
                "total_cache_misses": self.total_cache_misses,
                "covered_misses": self.covered_misses,
                "tp": self.tp,
                "fp": self.fp,
                "fn": self.fn,
                "pollution": self.pollution,
                "total_evictions": self.total_evictions,
                "evictions_caused_by_prefetch": self.evictions_caused_by_prefetch,
                "total_accesses": self.total_accesses,
                "cache_hits": self.cache_hits,
                "inference_calls": self.inference_calls,
            },
            "bytes": {
                "total_prefetch_bytes": self.total_prefetch_bytes,
                "useful_bytes": self.useful_bytes,
                "bandwidth_overhead_bytes": bandwidth_overhead_bytes,
                "bandwidth_overhead_mb": bandwidth_overhead_mb,
            },
            "metrics": {
                "accuracy": accuracy,
                "coverage": coverage,
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "timeliness": timeliness,
                "overprediction_rate": overprediction_rate,
                "pollution_rate": pollution_rate,
                "inference_time_per_prediction_ms": inference_time_per_prediction_ms,
                "inference_cpu_usage_percent": inference_cpu_usage_percent,
                "model_size_mb": self.model_size_mb,
            },
        }

    @classmethod
    def aggregate(cls, name: str, summaries: list) -> Dict[str, Any]:
        agg = cls(name)

        for summary in summaries:
            counts = summary.get("counts", {})
            bytes_data = summary.get("bytes", {})
            metrics = summary.get("metrics", {})

            agg.total_prefetches += int(counts.get("total_prefetches", 0))
            agg.useful_prefetches += int(counts.get("useful_prefetches", 0))
            agg.timely_prefetches += int(counts.get("timely_prefetches", 0))
            agg.total_cache_misses += int(counts.get("total_cache_misses", 0))
            agg.covered_misses += int(counts.get("covered_misses", 0))
            agg.tp += int(counts.get("tp", 0))
            agg.fn += int(counts.get("fn", 0))
            agg.pollution += int(counts.get("pollution", 0))
            agg.total_evictions += int(counts.get("total_evictions", 0))
            agg.evictions_caused_by_prefetch += int(counts.get("evictions_caused_by_prefetch", 0))
            agg.total_accesses += int(counts.get("total_accesses", 0))
            agg.cache_hits += int(counts.get("cache_hits", 0))

            agg.total_prefetch_bytes += int(bytes_data.get("total_prefetch_bytes", 0))
            agg.useful_bytes += int(bytes_data.get("useful_bytes", 0))

            calls = int(counts.get("inference_calls", 0))
            agg.inference_calls += calls
            agg.total_inference_time_ms += float(metrics.get("inference_time_per_prediction_ms", 0.0)) * calls
            agg.total_inference_cpu_pct += float(metrics.get("inference_cpu_usage_percent", 0.0)) * calls
            agg.model_size_mb += float(metrics.get("model_size_mb", 0.0))

        if summaries:
            agg.model_size_mb /= len(summaries)

        return agg.to_dict()