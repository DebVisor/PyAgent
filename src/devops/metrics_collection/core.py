"""Core metrics collection implementation."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class MetricPoint:
    """Single metric data point."""
    timestamp: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"MetricPoint(value={self.value}, time={self.timestamp})"


@dataclass
class Metric:
    """Represents a single metric."""
    name: str
    metric_type: MetricType
    description: str = ""
    unit: str = ""
    points: List[MetricPoint] = field(default_factory=list)

    def add_point(self, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Add a data point to metric."""
        point = MetricPoint(
            timestamp=datetime.utcnow().isoformat(),
            value=value,
            labels=labels or {}
        )
        self.points.append(point)

    def __repr__(self) -> str:
        return f"Metric(name={self.name}, type={self.metric_type.value}, points={len(self.points)})"


class MetricsCollector:
    """Metrics collection and aggregation."""

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics: Dict[str, Metric] = {}
        self.logger = logger

    def record_metric(self, name: str, value: float, metric_type: MetricType = MetricType.GAUGE,
                     labels: Optional[Dict[str, str]] = None) -> None:
        """Record a metric value.
        
        Args:
            name: Metric name
            value: Metric value
            metric_type: Type of metric
            labels: Optional labels
        """
        self.logger.debug(f"Recording metric: {name}={value}")
        
        if name not in self.metrics:
            self.metrics[name] = Metric(name=name, metric_type=metric_type)
        
        self.metrics[name].add_point(value, labels)

    def get_metric(self, name: str) -> Optional[Metric]:
        """Get a metric by name.
        
        Args:
            name: Metric name
            
        Returns:
            Metric object or None
        """
        return self.metrics.get(name)

    def get_all_metrics(self) -> Dict[str, Metric]:
        """Get all collected metrics.
        
        Returns:
            Dictionary of all metrics
        """
        return self.metrics.copy()

    def aggregate_metric(self, name: str, aggregation: str = "avg") -> Optional[float]:
        """Aggregate metric data points.
        
        Args:
            name: Metric name
            aggregation: Aggregation function (avg, sum, min, max)
            
        Returns:
            Aggregated value or None
        """
        metric = self.get_metric(name)
        if not metric or not metric.points:
            return None
        
        values = [p.value for p in metric.points]
        
        if aggregation == "avg":
            return sum(values) / len(values)
        elif aggregation == "sum":
            return sum(values)
        elif aggregation == "min":
            return min(values)
        elif aggregation == "max":
            return max(values)
        
        return None

    def clear_metrics(self) -> None:
        """Clear all metrics."""
        self.metrics.clear()
        self.logger.info("Metrics cleared")

    def export_metrics(self) -> Dict[str, Any]:
        """Export metrics in a serializable format.
        
        Returns:
            Dictionary of metric data
        """
        return {
            name: {
                "type": metric.metric_type.value,
                "description": metric.description,
                "unit": metric.unit,
                "points": [
                    {
                        "timestamp": p.timestamp,
                        "value": p.value,
                        "labels": p.labels
                    }
                    for p in metric.points
                ]
            }
            for name, metric in self.metrics.items()
        }
