"""
Performance monitoring and profiling for Agent Harness.

Provides:
- Execution timing context manager
- Response time tracking across agent turns
- Memory-efficient result accumulation
- Cached tool result storage
"""

import time
import functools
from collections import defaultdict
from contextlib import contextmanager
from typing import Any, Callable, Optional


# ── In-memory performance registry ───────────────────────────────────────────

_timings: dict[str, list[float]] = defaultdict(list)
_call_counts: dict[str, int] = defaultdict(int)


def record(label: str, elapsed: float) -> None:
    _timings[label].append(elapsed)
    _call_counts[label] += 1


def get_stats(label: str) -> dict:
    times = _timings.get(label, [])
    if not times:
        return {"label": label, "calls": 0, "avg_ms": 0, "min_ms": 0, "max_ms": 0}
    ms = [t * 1000 for t in times]
    return {
        "label": label,
        "calls": len(times),
        "avg_ms": round(sum(ms) / len(ms), 1),
        "min_ms": round(min(ms), 1),
        "max_ms": round(max(ms), 1),
    }


def all_stats() -> list[dict]:
    return [get_stats(label) for label in _timings]


def reset() -> None:
    _timings.clear()
    _call_counts.clear()


# ── Context manager ───────────────────────────────────────────────────────────

@contextmanager
def timer(label: str):
    """
    Context manager that records wall-clock time for a labeled block.

    Usage:
        with timer("fetch_hn"):
            result = fetch_hacker_news_trends(days=7)
    """
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        record(label, elapsed)


# ── Decorator ─────────────────────────────────────────────────────────────────

def timed(label: Optional[str] = None):
    """
    Decorator that times a function and records it.

    Usage:
        @timed()
        def my_tool(param: str) -> str:
            ...

        @timed("custom_label")
        def another_tool() -> str:
            ...
    """
    def decorator(func: Callable) -> Callable:
        _label = label or func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            record(_label, elapsed)
            return result

        return wrapper
    return decorator


# ── Response time budget ──────────────────────────────────────────────────────

class ResponseBudget:
    """
    Tracks cumulative response time and warns when budget is exceeded.

    Usage:
        budget = ResponseBudget(target_seconds=5.0)
        with budget.track("tool_call"):
            ...
        if budget.over():
            print(f"Over budget by {budget.excess():.1f}s")
    """

    def __init__(self, target_seconds: float = 30.0):
        self.target = target_seconds
        self._total = 0.0
        self._segments: list[tuple[str, float]] = []

    @contextmanager
    def track(self, label: str):
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            self._total += elapsed
            self._segments.append((label, elapsed))
            record(f"budget:{label}", elapsed)

    def spent(self) -> float:
        return round(self._total, 3)

    def remaining(self) -> float:
        return max(0.0, self.target - self._total)

    def over(self) -> bool:
        return self._total > self.target

    def excess(self) -> float:
        return max(0.0, self._total - self.target)

    def summary(self) -> dict:
        return {
            "target_s": self.target,
            "spent_s": self.spent(),
            "remaining_s": self.remaining(),
            "over_budget": self.over(),
            "segments": [
                {"label": lbl, "ms": round(t * 1000, 1)}
                for lbl, t in self._segments
            ],
        }


# ── Memory-efficient result buffer ────────────────────────────────────────────

class StreamBuffer:
    """
    Accumulates streaming text without building a single giant string per chunk.
    Only materializes the full string on demand.
    """

    __slots__ = ("_parts",)

    def __init__(self) -> None:
        self._parts: list[str] = []

    def append(self, text: str) -> None:
        self._parts.append(text)

    def text(self) -> str:
        return "".join(self._parts)

    def __len__(self) -> int:
        return sum(len(p) for p in self._parts)

    def clear(self) -> None:
        self._parts.clear()
