#!/usr/bin/env python3
"""
Live Progress Monitor - Real-time dashboard for Mega Execution
Monitors PostgreSQL progress and displays live updates
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import Dict, List
import argparse

# Add PyAgent to path
sys.path.insert(0, '/home/dev/PyAgent')

from memory_system.progress_tracker import ProgressTracker

logger = logging.getLogger(__name__)


class LiveProgressMonitor:
    """Real-time progress monitor with live dashboard"""
    
    def __init__(self, execution_id: str, db_url: str = None, refresh_interval: int = 5):
        """
        Initialize monitor
        
        Args:
            execution_id: Execution ID to monitor
            db_url: PostgreSQL connection string
            refresh_interval: Refresh interval in seconds
        """
        self.execution_id = execution_id
        self.db_url = db_url or os.getenv("DATABASE_URL", "postgresql://localhost/mega_execution")
        self.refresh_interval = refresh_interval
        self.tracker = ProgressTracker(self.db_url)
        self.start_time = datetime.now()
        self.session_start = None
    
    def initialize(self) -> bool:
        """Initialize monitor"""
        try:
            if not self.tracker.initialize():
                logger.error("Failed to initialize tracker")
                return False
            
            logger.info(f"✅ Monitor initialized for execution {self.execution_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize monitor: {e}")
            return False
    
    def calculate_eta(self, shards_completed: int, total_shards: int,
                     elapsed_seconds: float) -> str:
        """Calculate estimated time to completion"""
        if shards_completed == 0:
            return "N/A"
        
        shards_per_second = shards_completed / elapsed_seconds if elapsed_seconds > 0 else 0
        if shards_per_second == 0:
            return "N/A"
        
        remaining_shards = total_shards - shards_completed
        remaining_seconds = remaining_shards / shards_per_second
        
        hours = int(remaining_seconds // 3600)
        minutes = int((remaining_seconds % 3600) // 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def get_progress_bar(self, current: int, total: int, width: int = 40) -> str:
        """Generate progress bar"""
        if total == 0:
            return "[" + " " * width + "] 0%"
        
        percentage = (current / total) * 100
        filled = int((current / total) * width)
        
        bar = "[" + "=" * filled + " " * (width - filled) + f"] {percentage:.1f}%"
        return bar
    
    def print_header(self):
        """Print dashboard header"""
        os.system('clear' if os.name != 'nt' else 'cls')
        
        print("\n" + "=" * 100)
        print("🚀 MEGA EXECUTION - LIVE PROGRESS MONITOR")
        print("=" * 100)
        print(f"Execution ID: {self.execution_id}")
        print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Elapsed Time: {self.get_elapsed_time()}")
        print("=" * 100 + "\n")
    
    def get_elapsed_time(self) -> str:
        """Get elapsed time string"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def print_execution_status(self, data: Dict):
        """Print execution status"""
        exec_data = data.get("execution")
        if not exec_data:
            return
        
        print("📊 EXECUTION STATUS")
        print("─" * 100)
        print(f"  Status: {exec_data.get('status', 'N/A')} | Total Ideas: {exec_data.get('total_ideas', 0):,} | "
              f"Workers: {exec_data.get('total_workers', 0)} | Shards: {exec_data.get('total_shards', 0)}")
        print()
    
    def print_worker_progress(self, data: Dict):
        """Print worker progress"""
        workers = data.get("workers", {})
        summary = data.get("summary", {})
        total_shards = summary.get("total_shards", 420)
        
        if not workers:
            return
        
        print("👷 WORKER PROGRESS")
        print("─" * 100)
        
        total_workers = workers.get("total_workers", 0)
        completed = workers.get("completed", 0)
        running = workers.get("running", 0)
        failed = workers.get("failed", 0)
        
        print(f"  Status: {completed}/{total_workers} completed | {running} running | {failed} failed")
        print(f"  Shards: {workers.get('total_shards_completed', 0)}/{total_shards} "
              f"{self.get_progress_bar(workers.get('total_shards_completed', 0), total_shards)}")
        print(f"  Ideas: {workers.get('total_ideas_processed', 0):,} processed")
        print()
    
    def print_code_metrics(self, data: Dict):
        """Print code metrics"""
        metrics = data.get("code_metrics", {})
        if not metrics:
            return
        
        print("💻 CODE METRICS")
        print("─" * 100)
        print(f"  Files: {metrics.get('total_files', 0):,} | "
              f"LOC: {metrics.get('total_loc', 0):,} | "
              f"Coverage: {metrics.get('avg_coverage', 0):.1f}% | "
              f"Quality: {metrics.get('avg_quality', 0):.1f}/10")
        print()
    
    def print_shard_progress(self, data: Dict):
        """Print shard progress details"""
        shards = data.get("shards", {})
        summary = data.get("summary", {})
        
        if not shards:
            return
        
        print("📦 SHARD PROGRESS")
        print("─" * 100)
        
        total_shards = shards.get("total_shards", 0)
        total_ideas = shards.get("total_ideas", 0)
        total_loc = shards.get("total_loc", 0)
        avg_coverage = shards.get("avg_coverage", 0)
        avg_quality = shards.get("avg_quality", 0)
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        eta = self.calculate_eta(total_shards, 420, elapsed) if elapsed > 0 else "N/A"
        
        print(f"  Completed: {total_shards}/420 {self.get_progress_bar(total_shards, 420)}")
        print(f"  Ideas: {total_ideas:,}/200,000 | Files: {shards.get('total_files', 0):,} | "
              f"LOC: {total_loc:,}")
        print(f"  Metrics: Coverage {avg_coverage:.1f}% | Quality {avg_quality:.1f}/10")
        print(f"  ETA: {eta}")
        print()
    
    def print_throughput(self, data: Dict):
        """Print throughput metrics"""
        summary = data.get("summary", {})
        shards = data.get("shards", {})
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        if elapsed == 0:
            return
        
        shards_completed = shards.get("total_shards", 0)
        shards_per_sec = shards_completed / elapsed if elapsed > 0 else 0
        shards_per_hour = shards_per_sec * 3600
        
        ideas_processed = shards.get("total_ideas", 0)
        ideas_per_sec = ideas_processed / elapsed if elapsed > 0 else 0
        ideas_per_hour = ideas_per_sec * 3600
        
        code_files = shards.get("total_files", 0)
        files_per_hour = (code_files / elapsed) * 3600 if elapsed > 0 else 0
        
        print("⚡ THROUGHPUT")
        print("─" * 100)
        print(f"  Shards: {shards_per_sec:.2f}/sec = {shards_per_hour:.1f}/hour")
        print(f"  Ideas: {ideas_per_sec:.2f}/sec = {ideas_per_hour:.1f}/hour")
        print(f"  Code Files: {files_per_hour:.1f}/hour")
        print()
    
    def print_summary(self, data: Dict):
        """Print summary"""
        summary = data.get("summary", {})
        
        if not summary:
            return
        
        print("📈 SUMMARY")
        print("─" * 100)
        print(f"  Shards: {summary.get('shards_completed', 0)}/{summary.get('total_shards', 420)} "
              f"({(summary.get('shards_completed', 0) / summary.get('total_shards', 420) * 100) if summary.get('total_shards') else 0:.1f}%)")
        print(f"  Workers: {summary.get('workers_completed', 0)}/{summary.get('total_workers', 10)}")
        print(f"  Code Files: {summary.get('total_code_files', 0):,} | "
              f"LOC: {summary.get('total_loc', 0):,}")
        print(f"  Success Rate: {summary.get('success_rate', 0):.1f}%")
        
        if summary.get('duration_seconds'):
            hours = summary['duration_seconds'] // 3600
            minutes = (summary['duration_seconds'] % 3600) // 60
            print(f"  Duration: {hours}h {minutes}m")
        print()
    
    def print_kanban(self, data: Dict):
        """Print kanban progress"""
        kanban = data.get("kanban", [])
        
        if not kanban:
            return
        
        print("🎯 KANBAN BOARD")
        print("─" * 100)
        
        # Group by board
        boards = {}
        for item in kanban:
            board_id = item.get('board_id', 'unknown')
            if board_id not in boards:
                boards[board_id] = {}
            
            column = item.get('column_name', 'unknown')
            count = item.get('card_count', 0)
            boards[board_id][column] = count
        
        for board_id, columns in boards.items():
            print(f"  {board_id}:")
            for col, count in columns.items():
                print(f"    {col}: {count}")
        print()
    
    def run_once(self) -> bool:
        """Run monitor once and print dashboard"""
        try:
            data = self.tracker.get_full_dashboard(self.execution_id)
            
            self.print_header()
            self.print_execution_status(data)
            self.print_worker_progress(data)
            self.print_shard_progress(data)
            self.print_code_metrics(data)
            self.print_throughput(data)
            self.print_summary(data)
            self.print_kanban(data)
            
            print("=" * 100)
            print(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 100 + "\n")
            
            return True
        except Exception as e:
            logger.error(f"Error during monitoring: {e}")
            return False
    
    def run_continuous(self, duration_seconds: int = None):
        """Run monitor continuously"""
        try:
            start_time = datetime.now()
            
            while True:
                if not self.run_once():
                    logger.warning("Error during update, retrying...")
                
                # Check if duration exceeded
                if duration_seconds:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    if elapsed >= duration_seconds:
                        logger.info(f"Duration limit reached ({duration_seconds}s)")
                        break
                
                # Wait before next refresh
                time.sleep(self.refresh_interval)
        
        except KeyboardInterrupt:
            logger.info("Monitor stopped by user")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
        finally:
            self.tracker.close()
    
    def run_until_complete(self):
        """Run monitor until execution completes"""
        try:
            last_status = None
            
            while True:
                data = self.tracker.get_full_dashboard(self.execution_id)
                summary = data.get("summary", {})
                
                self.run_once()
                
                # Check completion
                total_shards = summary.get("total_shards", 420)
                shards_completed = summary.get("shards_completed", 0)
                workers_completed = summary.get("workers_completed", 0)
                total_workers = summary.get("total_workers", 10)
                
                if shards_completed == total_shards and workers_completed == total_workers:
                    print("\n" + "=" * 100)
                    print("🎉 EXECUTION COMPLETE!")
                    print("=" * 100 + "\n")
                    break
                
                # Wait before next refresh
                time.sleep(self.refresh_interval)
        
        except KeyboardInterrupt:
            logger.info("Monitor stopped by user")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
        finally:
            self.tracker.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Live Progress Monitor for Mega Execution")
    parser.add_argument("--execution-id", default="mega-001", help="Execution ID to monitor")
    parser.add_argument("--db-url", default=None, help="PostgreSQL connection URL")
    parser.add_argument("--refresh", type=int, default=5, help="Refresh interval (seconds)")
    parser.add_argument("--duration", type=int, default=None, help="Monitor duration (seconds)")
    parser.add_argument("--until-complete", action="store_true", help="Monitor until execution completes")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )
    
    # Create monitor
    monitor = LiveProgressMonitor(
        execution_id=args.execution_id,
        db_url=args.db_url,
        refresh_interval=args.refresh
    )
    
    if not monitor.initialize():
        sys.exit(1)
    
    # Run monitor
    if args.once:
        monitor.run_once()
    elif args.until_complete:
        monitor.run_until_complete()
    else:
        monitor.run_continuous(duration_seconds=args.duration)


if __name__ == "__main__":
    main()
