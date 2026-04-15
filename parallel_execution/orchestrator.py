"""Orchestrator: Coordinates 10 workers across 422 shards."""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from .distributed_queue import DistributedQueue
from .worker import Worker
from .metrics_tracker import MetricsTracker
from .telegram_reporter import TelegramReporter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


class Orchestrator:
    """Main orchestrator for distributed parallel execution."""
    
    def __init__(self,
                 num_workers: int = 10,
                 total_shards: int = 422,
                 shards_dir: str = "/home/dev/PyAgent/docs/project/execution_shards",
                 output_base: str = "/home/dev/PyAgent/implementations/generated_code"):
        
        self.num_workers = num_workers
        self.total_shards = total_shards
        self.shards_dir = Path(shards_dir)
        self.output_base = Path(output_base)
        
        # Initialize subsystems
        self.queue = DistributedQueue()
        self.metrics = MetricsTracker()
        self.reporter = TelegramReporter()
        
        # Worker pool
        self.workers: List[Worker] = []
        self._initialize_workers()
        
        # State
        self.running = False
        self.start_time = None
        self.report_interval = 1800  # 30 minutes
    
    def _initialize_workers(self) -> None:
        """Create worker instances with shard ranges."""
        shards_per_worker = self.total_shards // self.num_workers
        
        for worker_id in range(self.num_workers):
            start_shard = worker_id * shards_per_worker
            
            # Last worker gets any remainder
            if worker_id == self.num_workers - 1:
                end_shard = self.total_shards
            else:
                end_shard = (worker_id + 1) * shards_per_worker
            
            shard_range = range(start_shard, end_shard)
            
            worker = Worker(
                worker_id=worker_id,
                shard_range=shard_range,
                shards_dir=str(self.shards_dir),
                output_base=str(self.output_base),
                queue=self.queue
            )
            
            self.workers.append(worker)
            logger.info(f"Created Worker {worker_id}: shards {start_shard}-{end_shard-1}")
    
    async def run(self) -> Dict[str, Any]:
        """Run all workers concurrently."""
        self.running = True
        self.start_time = datetime.now()
        
        logger.info("="*80)
        logger.info(f"STARTING PARALLEL EXECUTION: {self.num_workers} workers, {self.total_shards} shards")
        logger.info("="*80)
        
        try:
            # Create tasks for all workers
            tasks = [worker.process_all_shards() for worker in self.workers]
            
            # Start progress monitor
            monitor_task = asyncio.create_task(self._monitor_progress())
            
            # Run all workers concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Stop monitor
            monitor_task.cancel()
            
            # Aggregate results
            return await self._finalize(results)
        
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            raise
        
        finally:
            self.running = False
    
    async def _monitor_progress(self) -> None:
        """Monitor progress and send updates every 30 minutes."""
        while self.running:
            try:
                await asyncio.sleep(self.report_interval)
                
                # Collect metrics
                metrics = self._collect_metrics()
                
                # Send report
                self.reporter.send_progress_report(metrics)
                
                # Check for bottlenecks
                bottlenecks = self.metrics.detect_bottlenecks()
                if bottlenecks:
                    logger.warning(f"Bottlenecks detected: {bottlenecks}")
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in progress monitor: {e}")
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """Collect current metrics from all workers."""
        all_stats = [w.get_stats() for w in self.workers]
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "shards_completed": sum(s.get("shards_processed", 0) for s in all_stats),
            "ideas_processed": sum(s.get("ideas_processed", 0) for s in all_stats),
            "projects_created": sum(s.get("projects_created", 0) for s in all_stats),
            "files_generated": sum(s.get("files_generated", 0) for s in all_stats),
            "lines_of_code": sum(s.get("lines_of_code", 0) for s in all_stats),
            "quality_violations": sum(s.get("quality_violations", 0) for s in all_stats),
            "worker_stats": all_stats
        }
        
        # Add velocity
        velocity = self.metrics.get_velocity()
        metrics.update(velocity)
        
        # Add ETA
        eta = self.metrics.calculate_eta()
        metrics.update(eta)
        
        # Add quality
        quality = self.metrics.get_quality_metrics(all_stats)
        metrics.update(quality)
        
        # Save checkpoint
        self.metrics.checkpoint(metrics)
        
        return metrics
    
    async def _finalize(self, results: List[Any]) -> Dict[str, Any]:
        """Finalize execution and generate final report."""
        logger.info("="*80)
        logger.info("EXECUTION COMPLETE")
        logger.info("="*80)
        
        # Collect final metrics
        final_metrics = self._collect_metrics()
        
        # Aggregate worker results
        final_metrics["worker_results"] = results
        
        # Calculate totals
        elapsed = (datetime.now() - self.start_time).total_seconds()
        final_metrics["elapsed_seconds"] = elapsed
        final_metrics["elapsed_hours"] = round(elapsed / 3600, 2)
        
        # Per-hour stats
        final_metrics["ideas_per_hour"] = round(
            final_metrics.get("ideas_processed", 0) / max(elapsed / 3600, 1),
            0
        )
        final_metrics["shards_per_hour"] = round(
            final_metrics.get("shards_completed", 0) / max(elapsed / 3600, 1),
            2
        )
        
        # Save final report
        report_path = self.output_base / "FINAL_REPORT.json"
        with open(report_path, 'w') as f:
            json.dump(final_metrics, f, indent=2)
        
        logger.info(f"Final report saved to {report_path}")
        
        # Print summary
        self._print_summary(final_metrics)
        
        # Send final report to Telegram
        self.reporter.send_progress_report(final_metrics)
        
        return final_metrics
    
    def _print_summary(self, metrics: Dict[str, Any]) -> None:
        """Print execution summary."""
        print("\n" + "="*80)
        print("EXECUTION SUMMARY")
        print("="*80)
        print(f"Total Shards: {metrics.get('shards_completed', 0)}/422")
        print(f"Total Ideas: {metrics.get('ideas_processed', 0):,}")
        print(f"Projects Created: {metrics.get('projects_created', 0):,}")
        print(f"Files Generated: {metrics.get('files_generated', 0):,}")
        print(f"Lines of Code: {metrics.get('lines_of_code', 0):,}")
        print()
        print(f"Elapsed Time: {metrics.get('elapsed_hours', 0)} hours")
        print(f"Ideas/Hour: {metrics.get('ideas_per_hour', 0):,.0f}")
        print(f"Shards/Hour: {metrics.get('shards_per_hour', 0):.2f}")
        print()
        print(f"Quality Pass Rate: {metrics.get('pass_rate', 0):.1f}%")
        print(f"Quality Violations: {metrics.get('quality_violations', 0)}")
        print()
        print(f"Output Directory: {self.output_base}")
        print("="*80 + "\n")
