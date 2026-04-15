"""
Progress Tracker - Real-time PostgreSQL monitoring for Mega Execution
Tracks worker status, shard completion, code metrics, and timeline events
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class ProgressTracker:
    """Track real-time progress of mega execution in PostgreSQL"""
    
    def __init__(self, db_url: str = None):
        """
        Initialize progress tracker
        
        Args:
            db_url: PostgreSQL connection string
        """
        self.db_url = db_url or "postgresql://localhost/mega_execution"
        self.conn = None
    
    def initialize(self) -> bool:
        """Initialize PostgreSQL schema for progress tracking"""
        try:
            self.conn = psycopg2.connect(self.db_url)
            cursor = self.conn.cursor()
            
            # Create progress schema
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS execution_progress (
                    id SERIAL PRIMARY KEY,
                    execution_id VARCHAR(50),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_ideas BIGINT,
                    total_workers INT,
                    total_shards INT,
                    ideas_per_shard INT,
                    status VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(execution_id)
                );
                
                CREATE TABLE IF NOT EXISTS worker_status (
                    id SERIAL PRIMARY KEY,
                    execution_id VARCHAR(50),
                    worker_id INT,
                    status VARCHAR(50),
                    shards_assigned INT,
                    shards_completed INT,
                    ideas_count BIGINT,
                    ideas_processed BIGINT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(execution_id, worker_id)
                );
                
                CREATE TABLE IF NOT EXISTS shard_completion (
                    id SERIAL PRIMARY KEY,
                    execution_id VARCHAR(50),
                    worker_id INT,
                    shard_id INT,
                    ideas_processed INT,
                    code_files_created INT,
                    total_loc BIGINT,
                    avg_coverage FLOAT,
                    avg_quality FLOAT,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(execution_id, shard_id)
                );
                
                CREATE TABLE IF NOT EXISTS code_metrics (
                    id SERIAL PRIMARY KEY,
                    execution_id VARCHAR(50),
                    worker_id INT,
                    idea_id VARCHAR(50),
                    file_name VARCHAR(255),
                    loc INT,
                    coverage FLOAT,
                    quality_score FLOAT,
                    module_name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_execution_id (execution_id),
                    INDEX idx_worker_id (worker_id)
                );
                
                CREATE TABLE IF NOT EXISTS timeline_events (
                    id SERIAL PRIMARY KEY,
                    execution_id VARCHAR(50),
                    stage VARCHAR(100),
                    worker_id INT,
                    event_data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_execution_id (execution_id),
                    INDEX idx_created_at (created_at)
                );
                
                CREATE TABLE IF NOT EXISTS kanban_progress (
                    id SERIAL PRIMARY KEY,
                    execution_id VARCHAR(50),
                    board_id VARCHAR(50),
                    column_name VARCHAR(50),
                    card_count INT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(execution_id, board_id, column_name)
                );
                
                CREATE TABLE IF NOT EXISTS execution_summary (
                    id SERIAL PRIMARY KEY,
                    execution_id VARCHAR(50),
                    total_ideas BIGINT,
                    total_shards INT,
                    shards_completed INT,
                    workers_completed INT,
                    total_workers INT,
                    total_code_files BIGINT,
                    total_loc BIGINT,
                    avg_coverage FLOAT,
                    avg_quality FLOAT,
                    success_rate FLOAT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    duration_seconds INT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(execution_id)
                );
            """)
            
            self.conn.commit()
            logger.info("✅ Progress tracker schema initialized")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to initialize progress tracker: {e}")
            return False
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor"""
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()
    
    # ========================================================================
    # EXECUTION PROGRESS
    # ========================================================================
    
    def create_execution(self, execution_id: str, total_ideas: int = 200000,
                        total_workers: int = 10, total_shards: int = 420,
                        ideas_per_shard: int = 476) -> bool:
        """Create new execution record"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO execution_progress
                    (execution_id, total_ideas, total_workers, total_shards, ideas_per_shard, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT(execution_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    timestamp = CURRENT_TIMESTAMP
                """, (execution_id, total_ideas, total_workers, total_shards, ideas_per_shard, "RUNNING"))
            
            logger.info(f"✅ Execution {execution_id} created")
            return True
        except Exception as e:
            logger.error(f"Failed to create execution: {e}")
            return False
    
    def get_execution(self, execution_id: str) -> Optional[Dict]:
        """Get execution details"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM execution_progress WHERE execution_id = %s",
                    (execution_id,)
                )
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Failed to get execution: {e}")
            return None
    
    # ========================================================================
    # WORKER STATUS
    # ========================================================================
    
    def update_worker_status(self, execution_id: str, worker_id: int,
                            status: str, shards_assigned: int = None,
                            shards_completed: int = 0, ideas_count: int = None,
                            ideas_processed: int = 0, start_time: datetime = None,
                            end_time: datetime = None) -> bool:
        """Update worker status"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO worker_status
                    (execution_id, worker_id, status, shards_assigned, shards_completed,
                     ideas_count, ideas_processed, start_time, end_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT(execution_id, worker_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    shards_completed = EXCLUDED.shards_completed,
                    ideas_processed = EXCLUDED.ideas_processed,
                    end_time = EXCLUDED.end_time,
                    updated_at = CURRENT_TIMESTAMP
                """, (execution_id, worker_id, status, shards_assigned,
                      shards_completed, ideas_count, ideas_processed,
                      start_time, end_time))
            
            return True
        except Exception as e:
            logger.error(f"Failed to update worker status: {e}")
            return False
    
    def get_worker_status(self, execution_id: str, worker_id: int = None) -> List[Dict]:
        """Get worker status"""
        try:
            with self.get_cursor() as cursor:
                if worker_id is not None:
                    cursor.execute(
                        "SELECT * FROM worker_status WHERE execution_id = %s AND worker_id = %s",
                        (execution_id, worker_id)
                    )
                    return [cursor.fetchone()]
                else:
                    cursor.execute(
                        "SELECT * FROM worker_status WHERE execution_id = %s ORDER BY worker_id",
                        (execution_id,)
                    )
                    return cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to get worker status: {e}")
            return []
    
    def get_worker_summary(self, execution_id: str) -> Dict:
        """Get summary of all workers"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT
                        COUNT(*) as total_workers,
                        SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) as completed,
                        SUM(CASE WHEN status = 'RUNNING' THEN 1 ELSE 0 END) as running,
                        SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed,
                        SUM(shards_completed) as total_shards_completed,
                        SUM(ideas_processed) as total_ideas_processed
                    FROM worker_status
                    WHERE execution_id = %s
                """, (execution_id,))
                
                result = cursor.fetchone()
                return dict(result) if result else {}
        except Exception as e:
            logger.error(f"Failed to get worker summary: {e}")
            return {}
    
    # ========================================================================
    # SHARD COMPLETION
    # ========================================================================
    
    def record_shard_completion(self, execution_id: str, worker_id: int,
                               shard_id: int, ideas_processed: int,
                               code_files_created: int = 0,
                               total_loc: int = 0, avg_coverage: float = 0.0,
                               avg_quality: float = 0.0) -> bool:
        """Record shard completion"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO shard_completion
                    (execution_id, worker_id, shard_id, ideas_processed,
                     code_files_created, total_loc, avg_coverage, avg_quality)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT(execution_id, shard_id) DO UPDATE SET
                    ideas_processed = EXCLUDED.ideas_processed,
                    code_files_created = EXCLUDED.code_files_created,
                    total_loc = EXCLUDED.total_loc,
                    avg_coverage = EXCLUDED.avg_coverage,
                    avg_quality = EXCLUDED.avg_quality
                """, (execution_id, worker_id, shard_id, ideas_processed,
                      code_files_created, total_loc, avg_coverage, avg_quality))
            
            return True
        except Exception as e:
            logger.error(f"Failed to record shard completion: {e}")
            return False
    
    def get_shard_progress(self, execution_id: str) -> List[Dict]:
        """Get all shard completion status"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM shard_completion
                    WHERE execution_id = %s
                    ORDER BY shard_id
                """, (execution_id,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to get shard progress: {e}")
            return []
    
    def get_shard_summary(self, execution_id: str) -> Dict:
        """Get shard completion summary"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT
                        COUNT(*) as total_shards,
                        SUM(ideas_processed) as total_ideas,
                        SUM(code_files_created) as total_files,
                        SUM(total_loc) as total_loc,
                        AVG(avg_coverage) as avg_coverage,
                        AVG(avg_quality) as avg_quality,
                        MIN(completed_at) as first_shard_time,
                        MAX(completed_at) as last_shard_time
                    FROM shard_completion
                    WHERE execution_id = %s
                """, (execution_id,))
                
                result = cursor.fetchone()
                return dict(result) if result else {}
        except Exception as e:
            logger.error(f"Failed to get shard summary: {e}")
            return {}
    
    # ========================================================================
    # CODE METRICS
    # ========================================================================
    
    def log_code_implementation(self, execution_id: str, worker_id: int,
                               idea_id: str, file_name: str, loc: int,
                               coverage: float, quality_score: float,
                               module_name: str = None) -> bool:
        """Log code implementation metrics"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO code_metrics
                    (execution_id, worker_id, idea_id, file_name, loc,
                     coverage, quality_score, module_name)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (execution_id, worker_id, idea_id, file_name, loc,
                      coverage, quality_score, module_name))
            
            return True
        except Exception as e:
            logger.error(f"Failed to log code implementation: {e}")
            return False
    
    def get_code_metrics_summary(self, execution_id: str) -> Dict:
        """Get aggregated code metrics"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT
                        COUNT(*) as total_files,
                        SUM(loc) as total_loc,
                        AVG(coverage) as avg_coverage,
                        AVG(quality_score) as avg_quality,
                        MIN(coverage) as min_coverage,
                        MAX(coverage) as max_coverage,
                        STDDEV(quality_score) as quality_stddev
                    FROM code_metrics
                    WHERE execution_id = %s
                """, (execution_id,))
                
                result = cursor.fetchone()
                return dict(result) if result else {}
        except Exception as e:
            logger.error(f"Failed to get code metrics summary: {e}")
            return {}
    
    # ========================================================================
    # TIMELINE EVENTS
    # ========================================================================
    
    def log_timeline_event(self, execution_id: str, stage: str,
                          worker_id: int = None, event_data: Dict = None) -> bool:
        """Log timeline event"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO timeline_events
                    (execution_id, stage, worker_id, event_data)
                    VALUES (%s, %s, %s, %s)
                """, (execution_id, stage, worker_id, json.dumps(event_data or {})))
            
            return True
        except Exception as e:
            logger.error(f"Failed to log timeline event: {e}")
            return False
    
    def get_timeline(self, execution_id: str) -> List[Dict]:
        """Get timeline events"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM timeline_events
                    WHERE execution_id = %s
                    ORDER BY created_at
                """, (execution_id,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to get timeline: {e}")
            return []
    
    # ========================================================================
    # KANBAN PROGRESS
    # ========================================================================
    
    def update_kanban_progress(self, execution_id: str, board_id: str,
                              column_name: str, card_count: int) -> bool:
        """Update kanban column progress"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO kanban_progress
                    (execution_id, board_id, column_name, card_count)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT(execution_id, board_id, column_name) DO UPDATE SET
                    card_count = EXCLUDED.card_count,
                    updated_at = CURRENT_TIMESTAMP
                """, (execution_id, board_id, column_name, card_count))
            
            return True
        except Exception as e:
            logger.error(f"Failed to update kanban progress: {e}")
            return False
    
    def get_kanban_progress(self, execution_id: str, board_id: str = None) -> List[Dict]:
        """Get kanban progress"""
        try:
            with self.get_cursor() as cursor:
                if board_id:
                    cursor.execute("""
                        SELECT * FROM kanban_progress
                        WHERE execution_id = %s AND board_id = %s
                        ORDER BY column_name
                    """, (execution_id, board_id))
                else:
                    cursor.execute("""
                        SELECT * FROM kanban_progress
                        WHERE execution_id = %s
                        ORDER BY board_id, column_name
                    """, (execution_id,))
                
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to get kanban progress: {e}")
            return []
    
    # ========================================================================
    # EXECUTION SUMMARY
    # ========================================================================
    
    def create_summary(self, execution_id: str, total_ideas: int = 200000,
                      total_shards: int = 420, start_time: datetime = None) -> bool:
        """Create execution summary record"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO execution_summary
                    (execution_id, total_ideas, total_shards, start_time)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT(execution_id) DO UPDATE SET
                    updated_at = CURRENT_TIMESTAMP
                """, (execution_id, total_ideas, total_shards, start_time))
            
            return True
        except Exception as e:
            logger.error(f"Failed to create summary: {e}")
            return False
    
    def update_summary(self, execution_id: str, shards_completed: int = None,
                      workers_completed: int = None, total_workers: int = None,
                      total_code_files: int = None, total_loc: int = None,
                      avg_coverage: float = None, avg_quality: float = None,
                      success_rate: float = None, end_time: datetime = None) -> bool:
        """Update execution summary"""
        try:
            with self.get_cursor() as cursor:
                updates = []
                params = []
                
                if shards_completed is not None:
                    updates.append("shards_completed = %s")
                    params.append(shards_completed)
                
                if workers_completed is not None:
                    updates.append("workers_completed = %s")
                    params.append(workers_completed)
                
                if total_workers is not None:
                    updates.append("total_workers = %s")
                    params.append(total_workers)
                
                if total_code_files is not None:
                    updates.append("total_code_files = %s")
                    params.append(total_code_files)
                
                if total_loc is not None:
                    updates.append("total_loc = %s")
                    params.append(total_loc)
                
                if avg_coverage is not None:
                    updates.append("avg_coverage = %s")
                    params.append(avg_coverage)
                
                if avg_quality is not None:
                    updates.append("avg_quality = %s")
                    params.append(avg_quality)
                
                if success_rate is not None:
                    updates.append("success_rate = %s")
                    params.append(success_rate)
                
                if end_time is not None:
                    updates.append("end_time = %s")
                    params.append(end_time)
                
                if end_time and start_time:
                    cursor.execute(
                        "SELECT start_time FROM execution_summary WHERE execution_id = %s",
                        (execution_id,)
                    )
                    result = cursor.fetchone()
                    if result and result['start_time']:
                        duration = int((end_time - result['start_time']).total_seconds())
                        updates.append("duration_seconds = %s")
                        params.append(duration)
                
                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(execution_id)
                
                query = f"UPDATE execution_summary SET {', '.join(updates)} WHERE execution_id = %s"
                cursor.execute(query, params)
            
            return True
        except Exception as e:
            logger.error(f"Failed to update summary: {e}")
            return False
    
    def get_summary(self, execution_id: str) -> Optional[Dict]:
        """Get execution summary"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM execution_summary WHERE execution_id = %s",
                    (execution_id,)
                )
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Failed to get summary: {e}")
            return None
    
    # ========================================================================
    # DASHBOARD GENERATION
    # ========================================================================
    
    def get_full_dashboard(self, execution_id: str) -> Dict:
        """Get complete dashboard data"""
        return {
            "execution": self.get_execution(execution_id),
            "workers": self.get_worker_summary(execution_id),
            "shards": self.get_shard_summary(execution_id),
            "code_metrics": self.get_code_metrics_summary(execution_id),
            "kanban": self.get_kanban_progress(execution_id),
            "summary": self.get_summary(execution_id)
        }
    
    def print_dashboard(self, execution_id: str):
        """Print formatted dashboard"""
        data = self.get_full_dashboard(execution_id)
        
        print("\n" + "=" * 80)
        print("🚀 MEGA EXECUTION - LIVE PROGRESS DASHBOARD")
        print("=" * 80)
        
        # Execution status
        if data["execution"]:
            exec_data = data["execution"]
            print(f"\n📊 EXECUTION: {exec_data['execution_id']}")
            print(f"   Status: {exec_data['status']}")
            print(f"   Total Ideas: {exec_data['total_ideas']:,}")
            print(f"   Total Workers: {exec_data['total_workers']}")
            print(f"   Total Shards: {exec_data['total_shards']}")
        
        # Worker summary
        if data["workers"]:
            workers = data["workers"]
            print(f"\n👷 WORKERS:")
            print(f"   Total: {workers.get('total_workers', 0)}")
            print(f"   Completed: {workers.get('completed', 0)}")
            print(f"   Running: {workers.get('running', 0)}")
            print(f"   Failed: {workers.get('failed', 0)}")
            print(f"   Shards Completed: {workers.get('total_shards_completed', 0)}")
            print(f"   Ideas Processed: {workers.get('total_ideas_processed', 0):,}")
        
        # Shard summary
        if data["shards"]:
            shards = data["shards"]
            print(f"\n📦 SHARDS:")
            print(f"   Completed: {shards.get('total_shards', 0)}")
            print(f"   Ideas: {shards.get('total_ideas', 0):,}")
            print(f"   Code Files: {shards.get('total_files', 0)}")
            print(f"   Total LOC: {shards.get('total_loc', 0):,}")
            print(f"   Avg Coverage: {shards.get('avg_coverage', 0):.1f}%")
            print(f"   Avg Quality: {shards.get('avg_quality', 0):.1f}/10")
        
        # Code metrics
        if data["code_metrics"]:
            metrics = data["code_metrics"]
            print(f"\n💻 CODE METRICS:")
            print(f"   Total Files: {metrics.get('total_files', 0)}")
            print(f"   Total LOC: {metrics.get('total_loc', 0):,}")
            print(f"   Avg Coverage: {metrics.get('avg_coverage', 0):.1f}%")
            print(f"   Avg Quality: {metrics.get('avg_quality', 0):.1f}/10")
        
        # Summary
        if data["summary"]:
            summary = data["summary"]
            print(f"\n📈 SUMMARY:")
            print(f"   Shards Completed: {summary.get('shards_completed', 0)}/{summary.get('total_shards', 420)}")
            print(f"   Workers Completed: {summary.get('workers_completed', 0)}/{summary.get('total_workers', 10)}")
            print(f"   Total Code Files: {summary.get('total_code_files', 0)}")
            print(f"   Total LOC: {summary.get('total_loc', 0):,}")
            print(f"   Success Rate: {summary.get('success_rate', 0):.1f}%")
            if summary.get('duration_seconds'):
                print(f"   Duration: {summary['duration_seconds']} seconds")
        
        print("\n" + "=" * 80 + "\n")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("✅ Database connection closed")


if __name__ == "__main__":
    # Test progress tracker
    logging.basicConfig(level=logging.INFO)
    
    tracker = ProgressTracker()
    tracker.initialize()
    
    # Create execution
    tracker.create_execution("mega-001", total_ideas=200000, total_workers=10, total_shards=420)
    
    # Simulate progress
    import time
    from random import randint
    
    for worker_id in range(10):
        tracker.update_worker_status(
            "mega-001", worker_id, "RUNNING",
            shards_assigned=42, ideas_count=19992,
            start_time=datetime.now()
        )
    
    # Simulate shard completion
    for shard_id in range(5):
        tracker.record_shard_completion(
            "mega-001", shard_id % 10, shard_id,
            ideas_processed=476, code_files_created=48,
            total_loc=72000, avg_coverage=92.0, avg_quality=8.0
        )
        tracker.log_code_implementation(
            "mega-001", shard_id % 10, f"idea:{shard_id:06d}",
            f"idea_{shard_id:06d}.py", 1500, 92.0, 8.0, f"module_{shard_id // 10}"
        )
    
    # Print dashboard
    tracker.print_dashboard("mega-001")
    
    tracker.close()
