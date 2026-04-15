"""Tests for Rust Criterion benchmarking."""

import pytest
from datetime import datetime
from benchmark_runner import (
    BenchmarkResult,
    BenchmarkRunner,
    ResultsAnalyzer,
    ReportGenerator
)


class TestBenchmarkResult:
    """Test BenchmarkResult dataclass."""
    
    def test_result_creation(self):
        """Test creating a benchmark result."""
        result = BenchmarkResult(
            name="test_bench",
            iterations=100,
            mean_ns=1000.0,
            std_dev_ns=50.0,
            min_ns=950.0,
            max_ns=1050.0,
            timestamp=datetime.now().isoformat()
        )
        
        assert result.name == "test_bench"
        assert result.mean_ns == 1000.0
        assert result.iterations == 100
    
    def test_throughput_calculation(self):
        """Test throughput calculation."""
        result = BenchmarkResult(
            name="bench",
            iterations=1,
            mean_ns=1e6,  # 1 microsecond = 1000 ns
            std_dev_ns=0,
            min_ns=0,
            max_ns=0,
            timestamp=datetime.now().isoformat()
        )
        
        # 1e9 ns/s / 1e6 ns = 1000 ops/s
        assert result.throughput() == 1000.0
    
    def test_throughput_with_items_per_iter(self):
        """Test throughput with multiple items per iteration."""
        result = BenchmarkResult(
            name="bench",
            iterations=1,
            mean_ns=1e6,
            std_dev_ns=0,
            min_ns=0,
            max_ns=0,
            timestamp=datetime.now().isoformat()
        )
        
        assert result.throughput(items_per_iter=10) == 10000.0
    
    def test_outlier_percentage(self):
        """Test outlier percentage calculation."""
        result = BenchmarkResult(
            name="bench",
            iterations=1,
            mean_ns=1000.0,
            std_dev_ns=100.0,
            min_ns=0,
            max_ns=0,
            timestamp=datetime.now().isoformat()
        )
        
        assert result.outlier_percentage() == 10.0


class TestResultsAnalyzer:
    """Test benchmark result analysis."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.results = [
            BenchmarkResult(
                name="bench1",
                iterations=100,
                mean_ns=1000.0,
                std_dev_ns=50.0,
                min_ns=950.0,
                max_ns=1050.0,
                timestamp=datetime.now().isoformat()
            ),
            BenchmarkResult(
                name="bench2",
                iterations=100,
                mean_ns=5000.0,
                std_dev_ns=250.0,
                min_ns=4750.0,
                max_ns=5250.0,
                timestamp=datetime.now().isoformat()
            )
        ]
        self.analyzer = ResultsAnalyzer(self.results)
    
    def test_get_slowest_benchmarks(self):
        """Test getting slowest benchmarks."""
        slowest = self.analyzer.get_slowest_benchmarks(1)
        assert len(slowest) == 1
        assert slowest[0].name == "bench2"
    
    def test_get_fastest_benchmarks(self):
        """Test getting fastest benchmarks."""
        fastest = self.analyzer.get_fastest_benchmarks(1)
        assert len(fastest) == 1
        assert fastest[0].name == "bench1"
    
    def test_calculate_statistics(self):
        """Test statistics calculation."""
        stats = self.analyzer.calculate_statistics()
        
        assert stats["count"] == 2
        assert stats["min_ns"] == 1000.0
        assert stats["max_ns"] == 5000.0
        assert stats["mean_ns"] == 3000.0
    
    def test_compare_with_baseline_no_regression(self):
        """Test comparison with baseline (no regression)."""
        baseline = [
            BenchmarkResult(
                name="bench1",
                iterations=100,
                mean_ns=1000.0,
                std_dev_ns=50.0,
                min_ns=950.0,
                max_ns=1050.0,
                timestamp=datetime.now().isoformat()
            )
        ]
        
        comps = self.analyzer.compare_with_baseline(
            baseline,
            threshold_percent=10.0
        )
        
        assert "bench1" in comps
        assert comps["bench1"]["is_regression"] is False
    
    def test_compare_with_baseline_regression(self):
        """Test comparison with baseline (with regression)."""
        baseline = [
            BenchmarkResult(
                name="bench1",
                iterations=100,
                mean_ns=1000.0,
                std_dev_ns=50.0,
                min_ns=950.0,
                max_ns=1050.0,
                timestamp=datetime.now().isoformat()
            )
        ]
        
        # Modify result to be slower
        self.results[0].mean_ns = 1200.0
        
        comps = self.analyzer.compare_with_baseline(
            baseline,
            threshold_percent=10.0
        )
        
        assert comps["bench1"]["is_regression"] is True
        assert comps["bench1"]["regression_type"] == "slowdown"


class TestReportGenerator:
    """Test report generation."""
    
    def setup_method(self):
        """Setup test fixtures."""
        results = [
            BenchmarkResult(
                name="bench1",
                iterations=100,
                mean_ns=1000.0,
                std_dev_ns=50.0,
                min_ns=950.0,
                max_ns=1050.0,
                timestamp=datetime.now().isoformat()
            )
        ]
        self.analyzer = ResultsAnalyzer(results)
        self.generator = ReportGenerator(self.analyzer)
    
    def test_generate_json_report(self):
        """Test JSON report generation."""
        report = self.generator.generate_json_report()
        
        assert isinstance(report, str)
        assert "statistics" in report
        assert "benchmarks" in report
        assert "generated_at" in report
    
    def test_generate_text_report(self):
        """Test text report generation."""
        report = self.generator.generate_text_report()
        
        assert isinstance(report, str)
        assert "BENCHMARK REPORT" in report
        assert "OVERALL STATISTICS" in report
        assert "bench1" in report
