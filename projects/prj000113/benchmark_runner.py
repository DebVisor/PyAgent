"""Rust Criterion Benchmarking Framework Integration

This module provides Python interfaces for managing Rust Criterion benchmarks.
"""

import json
import os
import subprocess
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime


@dataclass
class BenchmarkResult:
    """Represents a single benchmark result."""
    name: str
    iterations: int
    mean_ns: float
    std_dev_ns: float
    min_ns: float
    max_ns: float
    timestamp: str
    
    def throughput(self, items_per_iter: int = 1) -> float:
        """Calculate throughput in items per second."""
        if self.mean_ns == 0:
            return 0.0
        return (1e9 / self.mean_ns) * items_per_iter
    
    def outlier_percentage(self) -> float:
        """Estimate percentage of outliers based on std dev."""
        if self.mean_ns == 0:
            return 0.0
        return (self.std_dev_ns / self.mean_ns) * 100


class BenchmarkRunner:
    """Executes Criterion benchmarks."""
    
    def __init__(self, project_dir: str = "."):
        self.project_dir = project_dir
        self.results: List[BenchmarkResult] = []
    
    def run_benchmarks(self, benchmark_name: str = None) -> Tuple[bool, str]:
        """Run Criterion benchmarks."""
        cmd = ["cargo", "bench"]
        
        if benchmark_name:
            cmd.append("--bench")
            cmd.append(benchmark_name)
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                self._parse_results(result.stdout)
                return True, "Benchmarks completed successfully"
            else:
                return False, result.stderr
        
        except FileNotFoundError:
            return False, "cargo not found"
        except subprocess.TimeoutExpired:
            return False, "Benchmark timeout"
    
    def _parse_results(self, output: str) -> None:
        """Parse benchmark output."""
        # Simple parsing of Criterion output
        for line in output.split('\n'):
            if 'time:' in line and '[' in line:
                try:
                    # Extract benchmark name and timing
                    parts = line.split('time:')
                    if len(parts) == 2:
                        name = parts[0].strip().split()[-1]
                        timing = parts[1].strip().split()[0]
                        
                        # Parse timing (e.g., "123.45 us")
                        time_value, time_unit = timing.split()
                        time_ns = self._convert_to_ns(float(time_value), time_unit)
                        
                        result = BenchmarkResult(
                            name=name,
                            iterations=1,
                            mean_ns=time_ns,
                            std_dev_ns=time_ns * 0.1,  # Estimate
                            min_ns=time_ns * 0.95,
                            max_ns=time_ns * 1.05,
                            timestamp=datetime.now().isoformat()
                        )
                        self.results.append(result)
                except (ValueError, IndexError):
                    pass
    
    @staticmethod
    def _convert_to_ns(value: float, unit: str) -> float:
        """Convert timing to nanoseconds."""
        conversions = {
            'ns': 1.0,
            'us': 1e3,
            'µs': 1e3,
            'ms': 1e6,
            's': 1e9
        }
        return value * conversions.get(unit, 1.0)
    
    def get_results(self) -> List[BenchmarkResult]:
        """Get parsed benchmark results."""
        return self.results


class ResultsAnalyzer:
    """Analyzes benchmark results."""
    
    def __init__(self, results: List[BenchmarkResult]):
        self.results = results
        self.comparisons: Dict[str, Dict] = {}
    
    def compare_with_baseline(
        self,
        baseline_results: List[BenchmarkResult],
        threshold_percent: float = 5.0
    ) -> Dict[str, Dict]:
        """Compare current results with baseline."""
        self.comparisons = {}
        
        baseline_map = {r.name: r for r in baseline_results}
        
        for result in self.results:
            if result.name in baseline_map:
                baseline = baseline_map[result.name]
                percent_change = (
                    (result.mean_ns - baseline.mean_ns) / baseline.mean_ns
                ) * 100
                
                is_regression = abs(percent_change) > threshold_percent
                
                self.comparisons[result.name] = {
                    "baseline_ns": baseline.mean_ns,
                    "current_ns": result.mean_ns,
                    "percent_change": percent_change,
                    "is_regression": is_regression,
                    "regression_type": (
                        "slowdown" if percent_change > 0 else "speedup"
                    ) if is_regression else "OK"
                }
        
        return self.comparisons
    
    def get_slowest_benchmarks(self, count: int = 5) -> List[BenchmarkResult]:
        """Get slowest benchmarks."""
        return sorted(
            self.results,
            key=lambda x: x.mean_ns,
            reverse=True
        )[:count]
    
    def get_fastest_benchmarks(self, count: int = 5) -> List[BenchmarkResult]:
        """Get fastest benchmarks."""
        return sorted(
            self.results,
            key=lambda x: x.mean_ns
        )[:count]
    
    def calculate_statistics(self) -> Dict:
        """Calculate overall statistics."""
        if not self.results:
            return {
                "count": 0,
                "total_time_ns": 0,
                "mean_ns": 0,
                "min_ns": 0,
                "max_ns": 0
            }
        
        means = [r.mean_ns for r in self.results]
        return {
            "count": len(self.results),
            "total_time_ns": sum(means),
            "mean_ns": sum(means) / len(means),
            "min_ns": min(means),
            "max_ns": max(means)
        }


class ReportGenerator:
    """Generates benchmark reports."""
    
    def __init__(self, analyzer: ResultsAnalyzer):
        self.analyzer = analyzer
    
    def generate_json_report(self) -> str:
        """Generate JSON report."""
        stats = self.analyzer.calculate_statistics()
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "statistics": stats,
            "benchmarks": [
                {
                    "name": r.name,
                    "mean_ns": r.mean_ns,
                    "std_dev_ns": r.std_dev_ns,
                    "min_ns": r.min_ns,
                    "max_ns": r.max_ns,
                    "throughput": r.throughput()
                }
                for r in self.analyzer.results
            ]
        }
        
        return json.dumps(report, indent=2)
    
    def generate_text_report(self) -> str:
        """Generate text report."""
        lines = [
            "═" * 60,
            "BENCHMARK REPORT",
            "═" * 60,
            ""
        ]
        
        stats = self.analyzer.calculate_statistics()
        lines.append("OVERALL STATISTICS")
        lines.append(f"  Count: {stats['count']}")
        lines.append(f"  Mean: {stats['mean_ns']:.2f} ns")
        lines.append(f"  Min: {stats['min_ns']:.2f} ns")
        lines.append(f"  Max: {stats['max_ns']:.2f} ns")
        lines.append("")
        
        lines.append("SLOWEST BENCHMARKS")
        for result in self.analyzer.get_slowest_benchmarks(5):
            lines.append(f"  {result.name}: {result.mean_ns:.2f} ns")
        lines.append("")
        
        if self.analyzer.comparisons:
            lines.append("REGRESSIONS")
            for name, comp in self.analyzer.comparisons.items():
                if comp["is_regression"]:
                    lines.append(
                        f"  {name}: {comp['percent_change']:+.2f}% "
                        f"({comp['regression_type']})"
                    )
        
        return "\n".join(lines)
