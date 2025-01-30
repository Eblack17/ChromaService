from datetime import datetime, timedelta, UTC
from typing import Dict, List, Optional, Any
import time
import threading
from collections import defaultdict, deque
import json
from pathlib import Path
from functools import wraps
from .logging import get_logger

logger = get_logger(__name__)

class MetricsCollector:
    """Collector for application metrics."""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics_dir = Path("metrics")
        self.metrics_dir.mkdir(exist_ok=True)
        
        # Initialize metrics storage
        self._metrics: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=max_history)
        )
        self._metrics_lock = threading.Lock()
        
        # Start background metrics writer
        self._should_run = True
        self._writer_thread = threading.Thread(
            target=self._write_metrics_periodically,
            daemon=True
        )
        self._writer_thread.start()
    
    def record_metric(
        self,
        metric_name: str,
        value: Any,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a metric value.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            tags: Optional tags for the metric
        """
        timestamp = datetime.now(UTC).isoformat()
        metric_data = {
            "timestamp": timestamp,
            "value": value,
            "tags": tags or {}
        }
        
        with self._metrics_lock:
            self._metrics[metric_name].append(metric_data)
    
    def get_metrics(
        self,
        metric_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """Get metrics for a specific time range.
        
        Args:
            metric_name: Name of the metric
            start_time: Start of time range (UTC)
            end_time: End of time range (UTC)
            tags: Filter by tags
            
        Returns:
            List[Dict[str, Any]]: Filtered metrics
        """
        with self._metrics_lock:
            metrics = list(self._metrics[metric_name])
        
        # Filter by time range
        if start_time:
            metrics = [
                m for m in metrics
                if datetime.fromisoformat(m["timestamp"]).replace(tzinfo=UTC) >= start_time
            ]
        if end_time:
            metrics = [
                m for m in metrics
                if datetime.fromisoformat(m["timestamp"]).replace(tzinfo=UTC) <= end_time
            ]
        
        # Filter by tags
        if tags:
            metrics = [
                m for m in metrics
                if all(
                    m["tags"].get(k) == v
                    for k, v in tags.items()
                )
            ]
        
        return metrics
    
    def _write_metrics_periodically(self, interval: int = 60) -> None:
        """Write metrics to disk periodically.
        
        Args:
            interval: Write interval in seconds
        """
        while self._should_run:
            try:
                self._write_metrics_to_disk()
            except Exception as e:
                logger.error("Failed to write metrics", exc_info=True)
            time.sleep(interval)
    
    def _write_metrics_to_disk(self) -> None:
        """Write current metrics to disk."""
        timestamp = datetime.now(UTC)
        filename = self.metrics_dir / f"metrics_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        
        with self._metrics_lock:
            metrics_data = {
                name: list(values)
                for name, values in self._metrics.items()
            }
        
        with open(filename, "w") as f:
            json.dump(metrics_data, f, indent=2)

class PerformanceMonitor:
    """Monitor for tracking performance metrics."""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
    
    def track_execution_time(
        self,
        operation_name: str,
        tags: Optional[Dict[str, str]] = None
    ):
        """Decorator to track operation execution time.
        
        Args:
            operation_name: Name of the operation
            tags: Optional tags for the metric
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    self.metrics_collector.record_metric(
                        f"{operation_name}_execution_time",
                        execution_time,
                        tags
                    )
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    self.metrics_collector.record_metric(
                        f"{operation_name}_error",
                        {
                            "error_type": type(e).__name__,
                            "execution_time": execution_time
                        },
                        tags
                    )
                    raise
            return wrapper
        return decorator
    
    def track_api_metrics(
        self,
        endpoint: str,
        tags: Optional[Dict[str, str]] = None
    ):
        """Decorator to track API metrics.
        
        Args:
            endpoint: API endpoint name
            tags: Optional tags for the metric
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    self.metrics_collector.record_metric(
                        "api_request",
                        {
                            "endpoint": endpoint,
                            "status": "success",
                            "execution_time": execution_time
                        },
                        tags
                    )
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    self.metrics_collector.record_metric(
                        "api_request",
                        {
                            "endpoint": endpoint,
                            "status": "error",
                            "error_type": type(e).__name__,
                            "execution_time": execution_time
                        },
                        tags
                    )
                    raise
            return wrapper
        return decorator

# Create global instances
metrics_collector = MetricsCollector()
performance_monitor = PerformanceMonitor() 