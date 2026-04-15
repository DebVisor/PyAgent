"""Tests for prj000134: Observability Metrics Collection."""
import pytest, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from devops.metrics_collection import MetricsCollector, Metric, MetricsConfig, MetricType

class TestMetricsCollector:
    def test_collector_init(self):
        collector = MetricsCollector()
        assert collector is not None

    def test_record_metric(self):
        collector = MetricsCollector()
        collector.record_metric("cpu_usage", 85.5)
        assert "cpu_usage" in collector.metrics

    def test_get_metric(self):
        collector = MetricsCollector()
        collector.record_metric("memory", 90.0)
        metric = collector.get_metric("memory")
        assert metric is not None
        assert len(metric.points) == 1

    def test_aggregate_metric(self):
        collector = MetricsCollector()
        collector.record_metric("latency", 100.0)
        collector.record_metric("latency", 200.0)
        avg = collector.aggregate_metric("latency", "avg")
        assert avg == 150.0

    def test_config_creation(self):
        config = MetricsConfig(collection_interval=30)
        assert config.collection_interval == 30

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
