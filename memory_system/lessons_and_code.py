"""Lessons learned and code implementation ledger."""

import logging
import json
from typing import Any, Optional, List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class LessonLearned:
    """Track lessons, patterns, and recurrences."""
    
    def __init__(self, conn):
        """Initialize lessons system."""
        self.conn = conn
    
    def add_lesson(self, pattern: str, root_cause: str, prevention: str = None) -> Optional[int]:
        """Record a lesson learned."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO lessons (pattern, root_cause, prevention, first_seen, promotion_status)
                VALUES (%s, %s, %s, NOW(), 'OPEN')
                RETURNING lesson_id
            """, (pattern, root_cause, prevention))
            
            lesson_id = cur.fetchone()[0]
            self.conn.commit()
            logger.info(f"Lesson recorded: {lesson_id} - {pattern}")
            return lesson_id
        
        except Exception as e:
            logger.error(f"Error adding lesson: {e}")
            self.conn.rollback()
            return None
        finally:
            if cur:
                cur.close()
    
    def record_occurrence(self, lesson_id: int, context: str = None) -> bool:
        """Record an occurrence of a known lesson."""
        try:
            cur = self.conn.cursor()
            
            # Record occurrence
            cur.execute("""
                INSERT INTO lesson_occurrences (lesson_id, context)
                VALUES (%s, %s)
            """, (lesson_id, context))
            
            # Increment recurrence count
            cur.execute("""
                UPDATE lessons
                SET recurrence_count = recurrence_count + 1, updated_at = NOW()
                WHERE lesson_id = %s
            """, (lesson_id,))
            
            self.conn.commit()
            logger.debug(f"Occurrence recorded for lesson {lesson_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error recording occurrence: {e}")
            self.conn.rollback()
            return False
        finally:
            if cur:
                cur.close()
    
    def get_lesson(self, lesson_id: int) -> Optional[Dict[str, Any]]:
        """Get lesson details."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT lesson_id, pattern, root_cause, prevention, first_seen,
                       recurrence_count, promotion_status
                FROM lessons
                WHERE lesson_id = %s
            """, (lesson_id,))
            
            result = cur.fetchone()
            if result:
                return {
                    "lesson_id": result[0],
                    "pattern": result[1],
                    "root_cause": result[2],
                    "prevention": result[3],
                    "first_seen": result[4],
                    "recurrence_count": result[5],
                    "promotion_status": result[6]
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting lesson: {e}")
            return None
        finally:
            if cur:
                cur.close()
    
    def search_lessons(self, pattern_substring: str) -> List[Dict[str, Any]]:
        """Search lessons by pattern."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT lesson_id, pattern, root_cause, recurrence_count
                FROM lessons
                WHERE pattern ILIKE %s
                ORDER BY recurrence_count DESC
            """, (f"%{pattern_substring}%",))
            
            return [
                {
                    "lesson_id": row[0],
                    "pattern": row[1],
                    "root_cause": row[2],
                    "recurrence_count": row[3]
                }
                for row in cur.fetchall()
            ]
        
        except Exception as e:
            logger.error(f"Error searching lessons: {e}")
            return []
        finally:
            if cur:
                cur.close()
    
    def promote_lesson_to_prevention(self, lesson_id: int) -> bool:
        """Mark lesson as promoted to prevention practice."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                UPDATE lessons
                SET promotion_status = 'PROMOTED', updated_at = NOW()
                WHERE lesson_id = %s
            """, (lesson_id,))
            
            self.conn.commit()
            return cur.rowcount > 0
        
        except Exception as e:
            logger.error(f"Error promoting lesson: {e}")
            self.conn.rollback()
            return False
        finally:
            if cur:
                cur.close()
    
    def get_top_recurring_lessons(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequently occurring lessons."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT lesson_id, pattern, root_cause, recurrence_count, first_seen
                FROM lessons
                ORDER BY recurrence_count DESC
                LIMIT %s
            """, (limit,))
            
            return [
                {
                    "lesson_id": row[0],
                    "pattern": row[1],
                    "root_cause": row[2],
                    "recurrence_count": row[3],
                    "first_seen": row[4]
                }
                for row in cur.fetchall()
            ]
        
        except Exception as e:
            logger.error(f"Error getting top lessons: {e}")
            return []
        finally:
            if cur:
                cur.close()


class CodeImplementationLedger:
    """Track code implementations, LOC, coverage, quality metrics."""
    
    def __init__(self, conn):
        """Initialize code ledger."""
        self.conn = conn
    
    def log_implementation(self, project_id: str, file_path: str, lines_of_code: int,
                         coverage_percent: float, quality_score: float,
                         module_name: str = None, idea_id: str = None) -> Optional[int]:
        """Log a code implementation."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO code_implementations
                (project_id, file_path, module_name, lines_of_code, coverage_percent, quality_score, idea_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING impl_id
            """, (project_id, file_path, module_name, lines_of_code, coverage_percent, quality_score, idea_id))
            
            impl_id = cur.fetchone()[0]
            self.conn.commit()
            logger.info(f"Implementation logged: {file_path} ({lines_of_code} LOC)")
            return impl_id
        
        except Exception as e:
            logger.error(f"Error logging implementation: {e}")
            self.conn.rollback()
            return None
        finally:
            if cur:
                cur.close()
    
    def get_implementation(self, impl_id: int) -> Optional[Dict[str, Any]]:
        """Get implementation details."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT impl_id, project_id, file_path, module_name, lines_of_code,
                       coverage_percent, quality_score, test_count, passed_tests, created_at
                FROM code_implementations
                WHERE impl_id = %s
            """, (impl_id,))
            
            result = cur.fetchone()
            if result:
                return {
                    "impl_id": result[0],
                    "project_id": result[1],
                    "file_path": result[2],
                    "module_name": result[3],
                    "lines_of_code": result[4],
                    "coverage_percent": result[5],
                    "quality_score": result[6],
                    "test_count": result[7],
                    "passed_tests": result[8],
                    "created_at": result[9]
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting implementation: {e}")
            return None
        finally:
            if cur:
                cur.close()
    
    def get_project_stats(self, project_id: str) -> Dict[str, Any]:
        """Get aggregated stats for a project."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT
                    COUNT(*) as file_count,
                    SUM(lines_of_code) as total_loc,
                    AVG(coverage_percent) as avg_coverage,
                    AVG(quality_score) as avg_quality,
                    SUM(test_count) as total_tests,
                    SUM(passed_tests) as total_passed
                FROM code_implementations
                WHERE project_id = %s
            """, (project_id,))
            
            result = cur.fetchone()
            if result:
                return {
                    "file_count": result[0],
                    "total_loc": result[1],
                    "avg_coverage": float(result[2]) if result[2] else 0,
                    "avg_quality": float(result[3]) if result[3] else 0,
                    "total_tests": result[4],
                    "total_passed": result[5]
                }
            
            return {}
        
        except Exception as e:
            logger.error(f"Error getting project stats: {e}")
            return {}
        finally:
            if cur:
                cur.close()
    
    def list_implementations(self, project_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """List all implementations in a project."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT impl_id, file_path, module_name, lines_of_code, coverage_percent,
                       quality_score, created_at
                FROM code_implementations
                WHERE project_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (project_id, limit))
            
            return [
                {
                    "impl_id": row[0],
                    "file_path": row[1],
                    "module_name": row[2],
                    "lines_of_code": row[3],
                    "coverage_percent": row[4],
                    "quality_score": row[5],
                    "created_at": row[6]
                }
                for row in cur.fetchall()
            ]
        
        except Exception as e:
            logger.error(f"Error listing implementations: {e}")
            return []
        finally:
            if cur:
                cur.close()
    
    def update_test_results(self, impl_id: int, test_count: int, passed_tests: int) -> bool:
        """Update test results for implementation."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                UPDATE code_implementations
                SET test_count = %s, passed_tests = %s, updated_at = NOW()
                WHERE impl_id = %s
            """, (test_count, passed_tests, impl_id))
            
            self.conn.commit()
            return cur.rowcount > 0
        
        except Exception as e:
            logger.error(f"Error updating test results: {e}")
            self.conn.rollback()
            return False
        finally:
            if cur:
                cur.close()
