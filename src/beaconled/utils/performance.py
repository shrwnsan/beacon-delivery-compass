"""Performance monitoring utilities for beacon-delivery-compass.

This module provides decorators and utilities for monitoring and optimizing
performance across the application.
"""

import functools
import logging
import time
from collections.abc import Callable
from typing import Any

# Configure performance logger
perf_logger = logging.getLogger("beaconled.performance")


def monitor_performance(
    func_name: str | None = None,
    threshold_ms: int | None = None,
    log_level: int = logging.DEBUG,
) -> Callable:
    """Decorator to monitor function performance.

    Args:
        func_name: Optional custom name for the function in logs
        threshold_ms: Optional threshold in milliseconds for warning logs
        log_level: Logging level for normal performance logs

    Returns:
        Decorated function with performance monitoring

    Example:
        @monitor_performance(threshold_ms=100)
        def slow_function():
            # Function implementation
            pass
    """

    def decorator(func: Callable) -> Callable:
        name = func_name or f"{func.__module__}.{func.__name__}"

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                execution_time = (end_time - start_time) * 1000  # Convert to milliseconds

                # Log performance metrics
                perf_logger.log(
                    log_level,
                    "Performance: %s executed in %.2fms",
                    name,
                    execution_time,
                )

                # Log warning if execution exceeds threshold
                if threshold_ms and execution_time > threshold_ms:
                    perf_logger.warning(
                        "Performance warning: %s exceeded threshold (%.2fms > %dms)",
                        name,
                        execution_time,
                        threshold_ms,
                    )

        return wrapper

    return decorator


class PerformanceTracker:
    """Context manager for tracking performance of code blocks.

    Example:
        with PerformanceTracker("database_query"):
            # Database operation
            pass
    """

    def __init__(self, operation_name: str, threshold_ms: int | None = None):
        """Initialize performance tracker.

        Args:
            operation_name: Name of the operation being tracked
            threshold_ms: Optional threshold for warning logs
        """
        self.operation_name = operation_name
        self.threshold_ms = threshold_ms
        self.start_time: float | None = None
        self.execution_time: float | None = None

    def __enter__(self) -> "PerformanceTracker":
        """Start performance tracking."""
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """End performance tracking and log results."""
        if self.start_time is not None:
            end_time = time.perf_counter()
            self.execution_time = (end_time - self.start_time) * 1000  # Convert to milliseconds

            perf_logger.debug(
                "Performance: %s executed in %.2fms",
                self.operation_name,
                self.execution_time,
            )

            # Log warning if execution exceeds threshold
            if self.threshold_ms and self.execution_time > self.threshold_ms:
                perf_logger.warning(
                    "Performance warning: %s exceeded threshold (%.2fms > %dms)",
                    self.operation_name,
                    self.execution_time,
                    self.threshold_ms,
                )


class PerformanceMetrics:
    """Collection and analysis of performance metrics."""

    def __init__(self, max_samples: int = 1000):
        """Initialize metrics collector.

        Args:
            max_samples: Maximum number of samples to keep per metric
        """
        self.max_samples = max_samples
        self.metrics: dict[str, list[float]] = {}

    def record_metric(self, name: str, value: float) -> None:
        """Record a performance metric.

        Args:
            name: Name of the metric
            value: Metric value (typically execution time in milliseconds)
        """
        if name not in self.metrics:
            self.metrics[name] = []

        self.metrics[name].append(value)

        # Keep only the most recent samples
        if len(self.metrics[name]) > self.max_samples:
            self.metrics[name] = self.metrics[name][-self.max_samples :]

    def get_statistics(self, name: str) -> dict[str, float]:
        """Get statistics for a metric.

        Args:
            name: Name of the metric

        Returns:
            Dictionary with min, max, avg, and count statistics

        Raises:
            KeyError: If metric name is not found
        """
        if name not in self.metrics or not self.metrics[name]:
            msg = f"Metric '{name}' not found or has no data"
            raise KeyError(msg) from None

        values = self.metrics[name]
        return {
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "count": len(values),
            "p95": sorted(values)[int(len(values) * 0.95)] if len(values) > 1 else values[0],
        }

    def get_all_statistics(self) -> dict[str, dict[str, float]]:
        """Get statistics for all recorded metrics."""
        return {name: self.get_statistics(name) for name in self.metrics}

    def reset(self) -> None:
        """Reset all metrics."""
        self.metrics.clear()


# Global performance metrics instance
_global_metrics = PerformanceMetrics()


def get_global_metrics() -> PerformanceMetrics:
    """Get the global performance metrics instance."""
    return _global_metrics


def record_global_metric(name: str, value: float) -> None:
    """Record a metric in the global performance metrics."""
    _global_metrics.record_metric(name, value)
