"""Metrics tracker for real-time progress and ETA calculation."""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import statistics

class MetricsTracker:
    """Tracks real-time metrics and calculates ETA."""
    
    def __init__(self, checkpoint_file: str = "/tmp/metrics_checkpoint.json"):
        self.checkpoint_file = Path(checkpoint_file)
        self.start_time = time.time()
        self.checkpoints = []
        self._load_checkpoints()
    
    def checkpoint(self, metrics: Dict[str, Any]) -> None:
        """Record a checkpoint of current metrics."""
        checkpoint = {
            "timestamp": time.time(),
            "elapsed_seconds": time.time() - self.start_time,
            "ideas_processed": metrics.get("ideas_processed", 0),
            "shards_completed": metrics.get("shards_completed", 0),
            "projects_created": metrics.get("projects_created", 0),
            "quality_violations": metrics.get("quality_violations", 0)
        }
        
        self.checkpoints.append(checkpoint)
        self._save_checkpoints()
    
    def get_velocity(self) -> Dict[str, float]:
        """Calculate velocity (ideas/hour, shards/hour, etc)."""
        if len(self.checkpoints) < 2:
            return {
                "ideas_per_hour": 0.0,
                "shards_per_hour": 0.0,
                "projects_per_hour": 0.0
            }
        
        # Use last 5 checkpoints for average
        recent = self.checkpoints[-5:]
        
        if len(recent) < 2:
            return {
                "ideas_per_hour": 0.0,
                "shards_per_hour": 0.0,
                "projects_per_hour": 0.0
            }
        
        first = recent[0]
        last = recent[-1]
        
        elapsed_hours = (last["elapsed_seconds"] - first["elapsed_seconds"]) / 3600.0
        
        if elapsed_hours == 0:
            return {
                "ideas_per_hour": 0.0,
                "shards_per_hour": 0.0,
                "projects_per_hour": 0.0
            }
        
        return {
            "ideas_per_hour": (last["ideas_processed"] - first["ideas_processed"]) / elapsed_hours,
            "shards_per_hour": (last["shards_completed"] - first["shards_completed"]) / elapsed_hours,
            "projects_per_hour": (last["projects_created"] - first["projects_created"]) / elapsed_hours
        }
    
    def calculate_eta(self, target_ideas: int = 200000) -> Dict[str, Any]:
        """Calculate ETA to target."""
        velocity = self.get_velocity()
        
        if velocity["ideas_per_hour"] == 0:
            return {
                "eta_hours": None,
                "eta_timestamp": None,
                "confidence": 0.0
            }
        
        ideas_processed = self.checkpoints[-1]["ideas_processed"] if self.checkpoints else 0
        remaining_ideas = max(0, target_ideas - ideas_processed)
        
        hours_remaining = remaining_ideas / velocity["ideas_per_hour"]
        eta_timestamp = datetime.now() + timedelta(hours=hours_remaining)
        
        # Confidence based on stability of velocity
        if len(self.checkpoints) >= 5:
            velocities = []
            for i in range(1, min(6, len(self.checkpoints))):
                prev = self.checkpoints[i-1]
                curr = self.checkpoints[i]
                elapsed = (curr["elapsed_seconds"] - prev["elapsed_seconds"]) / 3600.0
                if elapsed > 0:
                    v = (curr["ideas_processed"] - prev["ideas_processed"]) / elapsed
                    velocities.append(v)
            
            if velocities:
                std_dev = statistics.stdev(velocities) if len(velocities) > 1 else 0
                mean_v = statistics.mean(velocities)
                # Confidence = 1 / (1 + coefficient_of_variation)
                cov = (std_dev / mean_v) if mean_v > 0 else 1.0
                confidence = 1.0 / (1.0 + cov)
            else:
                confidence = 0.0
        else:
            confidence = 0.0
        
        return {
            "eta_hours": round(hours_remaining, 1),
            "eta_timestamp": eta_timestamp.isoformat(),
            "ideas_processed": ideas_processed,
            "ideas_remaining": remaining_ideas,
            "confidence": round(confidence, 2)
        }
    
    def get_quality_metrics(self, stats_list: list) -> Dict[str, Any]:
        """Calculate quality metrics from worker stats."""
        if not stats_list:
            return {"pass_rate": 100.0, "avg_violations": 0.0}
        
        total_shards = sum(s.get("shards_processed", 0) for s in stats_list)
        total_violations = sum(s.get("quality_violations", 0) for s in stats_list)
        
        pass_rate = 100.0 - (total_violations / max(total_shards * 500, 1) * 100.0)
        
        return {
            "pass_rate": round(pass_rate, 1),
            "total_violations": total_violations,
            "avg_violations_per_shard": round(total_violations / max(total_shards, 1), 2)
        }
    
    def detect_bottlenecks(self) -> list:
        """Detect performance bottlenecks."""
        bottlenecks = []
        
        if len(self.checkpoints) < 3:
            return bottlenecks
        
        # Check for stalling (no progress in recent checkpoints)
        recent = self.checkpoints[-3:]
        if recent[-1]["ideas_processed"] == recent[0]["ideas_processed"]:
            bottlenecks.append("No progress in last 3 checkpoints - possible stall")
        
        # Check for quality violations spiking
        violations_trend = [c.get("quality_violations", 0) for c in recent]
        if len(violations_trend) >= 2 and violations_trend[-1] > violations_trend[0] * 1.5:
            bottlenecks.append("Quality violations spiking - investigate failed shards")
        
        return bottlenecks
    
    def _load_checkpoints(self) -> None:
        """Load checkpoints from file."""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file) as f:
                    data = json.load(f)
                    self.checkpoints = data.get("checkpoints", [])
                    self.start_time = data.get("start_time", self.start_time)
            except:
                pass
    
    def _save_checkpoints(self) -> None:
        """Save checkpoints to file."""
        try:
            with open(self.checkpoint_file, 'w') as f:
                json.dump({
                    "start_time": self.start_time,
                    "checkpoints": self.checkpoints
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving checkpoints: {e}")
