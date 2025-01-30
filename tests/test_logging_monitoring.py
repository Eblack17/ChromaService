import pytest
import json
import logging
import time
from datetime import datetime, timedelta, UTC
from pathlib import Path
from functools import wraps
from app.core.logging import (
    setup_logging,
    get_logger,
    log_execution_time,
    monitor_api_call,
    JSONFormatter,
    StandardFormatter
)
from app.core.monitoring import (
    MetricsCollector,
    PerformanceMonitor
)

@pytest.fixture
def caplog(caplog):
    """Fixture to capture log output."""
    return caplog

def test_json_formatter():
    """Test JSON formatter for logs."""
    formatter = JSONFormatter(app_name="test_app", environment="test")
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    formatted = formatter.format(record)
    log_data = json.loads(formatted)
    
    assert log_data["level"] == "INFO"
    assert log_data["message"] == "Test message"
    assert log_data["logger"] == "test_logger"
    assert log_data["app_name"] == "test_app"
    assert log_data["environment"] == "test"

def test_standard_formatter():
    """Test standard formatter for logs."""
    formatter = StandardFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    formatted = formatter.format(record)
    assert "test_logger" in formatted
    assert "INFO" in formatted
    assert "Test message" in formatted

def test_logger_with_context(caplog):
    """Test logger with additional context."""
    logger = get_logger("test_module", user_id="123", action="test")
    
    # Temporarily capture log output
    with caplog.at_level(logging.INFO):
        logger.info("Test message with context")
    
    # Check log record
    assert len(caplog.records) > 0
    record = caplog.records[-1]
    assert record.msg == "Test message with context"
    assert record.levelname == "INFO"
    
    # Check log text
    log_text = caplog.text
    assert "Test message with context" in log_text
    assert "test_module" in log_text
    assert "INFO" in log_text

@log_execution_time()
def sample_function():
    """Sample function for testing execution time logging."""
    time.sleep(0.1)
    return "done"

def test_execution_time_logging(caplog):
    """Test execution time logging decorator."""
    with caplog.at_level(logging.INFO):
        result = sample_function()
        
    assert result == "done"
    assert "executed in" in caplog.text
    assert "seconds" in caplog.text

@monitor_api_call()
def sample_api_call():
    """Sample API call for testing monitoring."""
    time.sleep(0.1)
    return {"status": "success"}

def test_api_call_monitoring(caplog):
    """Test API call monitoring decorator."""
    with caplog.at_level(logging.INFO):
        result = sample_api_call()
        
    assert result["status"] == "success"
    assert "API call" in caplog.text
    assert "successful" in caplog.text

def test_metrics_collector():
    """Test metrics collection and retrieval."""
    collector = MetricsCollector()
    
    # Record some metrics
    collector.record_metric(
        "test_metric",
        42,
        tags={"env": "test"}
    )
    collector.record_metric(
        "test_metric",
        43,
        tags={"env": "test"}
    )
    
    # Get metrics
    metrics = collector.get_metrics(
        "test_metric",
        tags={"env": "test"}
    )
    
    assert len(metrics) == 2
    assert metrics[0]["value"] == 42
    assert metrics[1]["value"] == 43
    assert all(m["tags"]["env"] == "test" for m in metrics)

def test_performance_monitor():
    """Test performance monitoring."""
    monitor = PerformanceMonitor()
    
    @monitor.track_execution_time("test_operation")
    def test_operation():
        time.sleep(0.1)
        return "success"
    
    result = test_operation()
    assert result == "success"
    
    # Check recorded metrics
    metrics = monitor.metrics_collector.get_metrics("test_operation_execution_time")
    assert len(metrics) > 0
    assert isinstance(metrics[0]["value"], float)
    assert metrics[0]["value"] >= 0.1

def test_metrics_file_writing():
    """Test metrics are written to disk."""
    collector = MetricsCollector()
    
    # Record a metric
    collector.record_metric("test_metric", 42)
    
    # Force metrics write
    collector._write_metrics_to_disk()
    
    # Check metrics directory
    metrics_files = list(Path("metrics").glob("metrics_*.json"))
    assert len(metrics_files) > 0
    
    # Read latest metrics file
    latest_file = max(metrics_files, key=lambda p: p.stat().st_mtime)
    with open(latest_file) as f:
        metrics_data = json.load(f)
    
    assert "test_metric" in metrics_data
    assert len(metrics_data["test_metric"]) > 0
    assert metrics_data["test_metric"][0]["value"] == 42

def test_metrics_filtering():
    """Test metrics filtering by time and tags."""
    collector = MetricsCollector()
    
    # Record metrics with different timestamps and tags
    now = datetime.now(UTC)
    collector.record_metric(
        "test_metric",
        1,
        tags={"env": "prod"}
    )
    time.sleep(0.1)
    collector.record_metric(
        "test_metric",
        2,
        tags={"env": "test"}
    )
    
    # Test time filtering
    recent_metrics = collector.get_metrics(
        "test_metric",
        start_time=now
    )
    assert len(recent_metrics) == 2
    
    # Test tag filtering
    prod_metrics = collector.get_metrics(
        "test_metric",
        tags={"env": "prod"}
    )
    assert len(prod_metrics) == 1
    assert prod_metrics[0]["value"] == 1 
