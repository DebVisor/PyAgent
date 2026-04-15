"""
Example: Using the Unified Memory System for Parallel Execution Tracking.

This demonstrates:
1. Creating and managing mega execution plans
2. Tracking 200K+ ideas across workers
3. Managing code implementations
4. Learning from lessons and preventing recurrence
5. Kanban workflow tracking
"""

import json
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


def example_execution_plan_tracking():
    """Track mega execution plan with 200K+ ideas."""
    from unified_memory import UnifiedMemorySystem
    
    print("\n" + "="*80)
    print("EXAMPLE 1: MEGA EXECUTION PLAN TRACKING (200K IDEAS)")
    print("="*80)
    
    with UnifiedMemorySystem() as memory:
        # 1. Create kanban board for execution phases
        memory.kanban_create_board(
            "mega-execution",
            "200K Ideas Execution Pipeline",
            ["BACKLOG", "ENQUEUED", "IN_PROGRESS", "TESTING", "COMPLETED", "FAILED"]
        )
        
        # 2. Create graph for idea dependencies
        logger.info("Creating execution graph...")
        
        # Root node
        memory.graph_add_node(
            "execution-root",
            "PHASE",
            {
                "name": "200K Ideas Batch",
                "total_ideas": 200000,
                "status": "ACTIVE"
            }
        )
        
        # Shard nodes (420 shards, 476 ideas per shard)
        for shard_id in range(0, 420, 20):  # Sample: every 20th shard
            shard_node_id = f"shard-{shard_id}"
            memory.graph_add_node(
                shard_node_id,
                "SHARD",
                {
                    "shard_id": shard_id,
                    "ideas_count": 476,
                    "worker_id": shard_id % 10
                }
            )
            
            # Link to root
            memory.graph_add_edge(
                "execution-root",
                shard_node_id,
                "CONTAINS"
            )
        
        # 3. Log kanban cards for sample ideas
        logger.info("Creating kanban cards for ideas...")
        for idea_num in range(1, 11):  # Sample 10 ideas
            card_id = f"idea-{idea_num:06d}"
            memory.kanban_create_card(
                card_id,
                f"Implement feature #{idea_num}",
                "BACKLOG",
                "mega-execution",
                priority=idea_num % 3
            )
            
            if idea_num % 5 == 0:
                memory.kanban_move_card(card_id, "IN_PROGRESS")
        
        # 4. Check board summary
        summary = memory.kanban_board_summary("mega-execution")
        logger.info(f"Board summary: {summary}")
        
        # 5. Use B-Tree for fast idea lookup by ID
        logger.info("Indexing ideas with B-Tree...")
        for idea_num in range(1, 101, 10):
            memory.btree_insert(
                f"idea:{idea_num:06d}",
                {
                    "idea_id": idea_num,
                    "created_at": datetime.now().isoformat(),
                    "shard": idea_num // 476
                }
            )
        
        # 6. Query range of ideas
        ideas = memory.btree_range("idea:000001", "idea:000100")
        logger.info(f"Ideas in range: {len(ideas)}")
        
        return True


def example_code_implementation_tracking():
    """Track code implementations with metrics."""
    from unified_memory import UnifiedMemorySystem
    
    print("\n" + "="*80)
    print("EXAMPLE 2: CODE IMPLEMENTATION TRACKING")
    print("="*80)
    
    with UnifiedMemorySystem() as memory:
        project_id = "mega-execution-v1"
        
        # Create kanban board for code phases
        memory.kanban_create_board(
            f"{project_id}-code",
            f"{project_id} Code Implementations",
            ["DESIGN", "IN_DEVELOPMENT", "TESTING", "REVIEW", "MERGED"]
        )
        
        # Log implementations with metrics
        implementations = [
            {
                "file": "core/executor.py",
                "module": "executor",
                "loc": 2500,
                "coverage": 92.5,
                "quality": 8.7,
                "tests": 45,
                "passed": 45
            },
            {
                "file": "memory/unified_memory.py",
                "module": "memory",
                "loc": 8900,
                "coverage": 88.2,
                "quality": 8.9,
                "tests": 60,
                "passed": 59
            },
            {
                "file": "worker/coordinator.py",
                "module": "coordinator",
                "loc": 3200,
                "coverage": 85.0,
                "quality": 8.3,
                "tests": 35,
                "passed": 34
            }
        ]
        
        logger.info("Logging code implementations...")
        for impl in implementations:
            impl_id = memory.code_log(
                project_id,
                impl["file"],
                impl["loc"],
                impl["coverage"],
                impl["quality"],
                impl["module"],
                idea_id=None
            )
            
            logger.info(f"  Logged: {impl['file']} (ID: {impl_id})")
            
            # Create corresponding kanban card
            card_id = f"code-{impl['module']}"
            memory.kanban_create_card(
                card_id,
                f"Implement {impl['module']}",
                "MERGED",
                f"{project_id}-code"
            )
        
        # Get project statistics
        stats = memory.code_project_stats(project_id)
        logger.info(f"Project stats: {json.dumps(stats, indent=2)}")
        
        return True


def example_lessons_and_prevention():
    """Track lessons learned and prevent recurrence."""
    from unified_memory import UnifiedMemorySystem
    
    print("\n" + "="*80)
    print("EXAMPLE 3: LESSONS LEARNED & PREVENTION")
    print("="*80)
    
    with UnifiedMemorySystem() as memory:
        # Record common lessons
        lessons_data = [
            {
                "pattern": "Database connection timeout",
                "root_cause": "Connection pool exhausted under high parallelism",
                "prevention": "Implement connection pool scaling, add circuit breaker"
            },
            {
                "pattern": "Memory leak in worker process",
                "root_cause": "Unreleased transaction resources",
                "prevention": "Use context managers for all DB operations"
            },
            {
                "pattern": "Race condition in state updates",
                "root_cause": "Missing pessimistic locking on shared state",
                "prevention": "Add row-level locks for concurrent updates"
            }
        ]
        
        logger.info("Recording lessons learned...")
        lesson_ids = []
        for lesson in lessons_data:
            lesson_id = memory.lesson_record(
                lesson["pattern"],
                lesson["root_cause"],
                lesson["prevention"]
            )
            lesson_ids.append(lesson_id)
            logger.info(f"  Recorded: {lesson['pattern']} (ID: {lesson_id})")
        
        # Simulate lesson occurrences
        logger.info("\nRecording lesson occurrences...")
        for lesson_id in lesson_ids[:2]:
            for i in range(3):
                memory.lesson_record_occurrence(
                    lesson_id,
                    f"Occurred in worker-{i % 10} during batch-{i}"
                )
        
        # Get top recurring lessons
        top_lessons = memory.lesson_top_recurring(limit=5)
        logger.info(f"\nTop recurring lessons:\n{json.dumps(top_lessons, indent=2, default=str)}")
        
        return True


def example_execution_ledger():
    """Track execution logs and worker metrics."""
    from unified_memory import UnifiedMemorySystem
    
    print("\n" + "="*80)
    print("EXAMPLE 4: EXECUTION LEDGER & METRICS")
    print("="*80)
    
    with UnifiedMemorySystem() as memory:
        # Create linked list for execution timeline
        logger.info("Creating execution timeline...")
        
        stages = [
            "INIT",
            "SHARD_DISTRIBUTION",
            "WORKER_SPAWN",
            "EXECUTION_START",
            "BATCH_1_COMPLETE",
            "BATCH_2_COMPLETE",
            "AGGREGATION",
            "FINALIZATION"
        ]
        
        for stage in stages:
            memory.ll_append(
                "execution-timeline",
                {
                    "stage": stage,
                    "timestamp": datetime.now().isoformat(),
                    "status": "COMPLETED"
                }
            )
            logger.info(f"  Timeline: {stage}")
        
        # Use KV store for fast lookups of worker status
        logger.info("\nCaching worker status...")
        for worker_id in range(10):
            memory.kv_set(
                f"worker:{worker_id}:status",
                {
                    "worker_id": worker_id,
                    "status": "ACTIVE",
                    "shards_completed": worker_id * 42,
                    "ideas_completed": worker_id * 42 * 476
                },
                ttl_seconds=3600  # 1 hour TTL
            )
        
        # Query worker status
        logger.info("\nQuerying worker status...")
        for worker_id in [0, 5, 9]:
            status = memory.kv_get(f"worker:{worker_id}:status")
            logger.info(f"  Worker-{worker_id}: {status}")
        
        # Traverse execution timeline
        logger.info("\nExecution timeline:")
        timeline = memory.ll_traverse("execution-timeline")
        for entry in timeline:
            logger.info(f"  {entry['stage']} @ {entry['timestamp']}")
        
        return True


def example_transaction_demo():
    """Demonstrate atomic transaction operations."""
    from unified_memory import UnifiedMemorySystem
    
    print("\n" + "="*80)
    print("EXAMPLE 5: ATOMIC TRANSACTIONS")
    print("="*80)
    
    with UnifiedMemorySystem() as memory:
        logger.info("Creating transactional execution...")
        
        # Complex operation: Create idea, log implementation, update kanban
        try:
            with memory.transaction() as tx:
                # Add idea node to graph
                memory.graph_add_node(
                    "idea-999999",
                    "IDEA",
                    {
                        "title": "Transactional Feature",
                        "priority": 1,
                        "status": "IN_PROGRESS"
                    }
                )
                
                # Log code implementation
                impl_id = memory.code_log(
                    "mega-execution-v1",
                    "transactional/feature.py",
                    1500,
                    90.0,
                    8.8,
                    "transactional_feature"
                )
                
                # Create kanban card
                memory.kanban_create_card(
                    "idea-999999-card",
                    "Transactional Feature Implementation",
                    "IN_PROGRESS",
                    "mega-execution"
                )
                
                logger.info("Transaction completed successfully")
                logger.info(f"  Implementation ID: {impl_id}")
        
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            return False
        
        return True


def main():
    """Run all examples."""
    print("\n" + "#"*80)
    print("# UNIFIED MEMORY SYSTEM - COMPREHENSIVE EXAMPLES")
    print("#"*80)
    
    examples = [
        ("Execution Plan Tracking", example_execution_plan_tracking),
        ("Code Implementation", example_code_implementation_tracking),
        ("Lessons & Prevention", example_lessons_and_prevention),
        ("Execution Ledger", example_execution_ledger),
        ("Transactions", example_transaction_demo),
    ]
    
    results = {}
    for name, example_func in examples:
        try:
            result = example_func()
            results[name] = "✅ PASSED" if result else "❌ FAILED"
        except Exception as e:
            logger.error(f"Example failed: {e}")
            results[name] = f"❌ ERROR: {e}"
    
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    for name, result in results.items():
        print(f"{name:.<50} {result}")
    
    print("\n✅ All examples completed!")


if __name__ == "__main__":
    main()
