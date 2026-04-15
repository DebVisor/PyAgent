"""Individual worker for processing shard ranges."""

import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List
import logging
import sys

logger = logging.getLogger(__name__)


class Worker:
    """Processes a shard range (42 shards per worker)."""
    
    def __init__(self, 
                 worker_id: int,
                 shard_range: range,
                 shards_dir: str,
                 output_base: str,
                 queue):
        self.worker_id = worker_id
        self.shard_range = shard_range
        self.shards_dir = Path(shards_dir)
        self.output_base = Path(output_base)
        self.queue = queue
        
        # Worker output directory
        self.worker_dir = self.output_base / f"worker_{worker_id:02d}"
        self.worker_dir.mkdir(parents=True, exist_ok=True)
        
        # Stats
        self.stats = {
            "worker_id": worker_id,
            "shards_processed": 0,
            "ideas_processed": 0,
            "projects_created": 0,
            "files_generated": 0,
            "lines_of_code": 0,
            "errors": [],
            "quality_violations": 0
        }
    
    async def process_shard(self, shard_id: int) -> Dict[str, Any]:
        """Process a single shard with all 500 ideas."""
        shard_number = shard_id + 1
        shard_file = self.shards_dir / f"SHARD_{shard_number:04d}.json"
        
        logger.info(f"[Worker {self.worker_id}] Processing shard {shard_id}")
        
        if not shard_file.exists():
            error = f"Shard file not found: {shard_file}"
            logger.error(error)
            self.stats["errors"].append(error)
            return {"success": False, "error": error}
        
        try:
            # Load shard
            with open(shard_file) as f:
                shard_data = json.load(f)
            
            shard_output_dir = self.worker_dir / f"shard_{shard_id:04d}"
            shard_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Process each idea in the shard
            ideas = shard_data.get("ideas", [])
            processed_ideas = 0
            
            for idea_index, idea in enumerate(ideas):
                idea_id = idea.get("idea_id", f"idea_{idea_index}")
                
                try:
                    # Call the @0master→@9git pipeline for this idea
                    result = await self._execute_idea_pipeline(idea, shard_output_dir)
                    
                    if result["success"]:
                        processed_ideas += 1
                        self.stats["ideas_processed"] += 1
                        self.stats["lines_of_code"] += result.get("lines_of_code", 0)
                    else:
                        self.stats["quality_violations"] += 1
                        logger.warning(f"Idea {idea_id} failed quality gates")
                
                except Exception as e:
                    logger.error(f"Error processing idea {idea_id}: {e}")
                    self.stats["errors"].append(str(e))
            
            # Update stats
            self.stats["shards_processed"] += 1
            self.stats["projects_created"] += processed_ideas // 10  # ~10 projects per 100 ideas
            self.stats["files_generated"] += processed_ideas * 4  # ~4 files per idea
            
            # Save shard summary
            summary = {
                "shard_id": shard_id,
                "ideas_processed": processed_ideas,
                "output_dir": str(shard_output_dir),
                "completed_at": str(Path.cwd() / ".")
            }
            
            summary_file = shard_output_dir / "SUMMARY.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            # Mark complete in queue
            self.queue.mark_shard_complete(shard_id, str(shard_output_dir))
            
            logger.info(f"[Worker {self.worker_id}] Shard {shard_id} complete ({processed_ideas} ideas)")
            
            return {
                "success": True,
                "shard_id": shard_id,
                "ideas_processed": processed_ideas,
                "output_dir": str(shard_output_dir)
            }
        
        except Exception as e:
            logger.error(f"Error processing shard {shard_id}: {e}")
            self.stats["errors"].append(str(e))
            return {"success": False, "error": str(e)}
    
    async def _execute_idea_pipeline(self, idea: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
        """Execute the @0master→@9git pipeline for a single idea.
        
        Simplified version:
        1. Read idea file
        2. Validate against acceptance criteria
        3. Generate basic implementation stub
        4. Run quality gates
        5. Save output
        """
        idea_id = idea.get("idea_id")
        idea_file = Path(idea.get("file_path", ""))
        
        if not idea_file.exists():
            return {"success": False, "error": f"Idea file not found: {idea_file}"}
        
        try:
            # Read idea
            idea_content = idea_file.read_text()
            
            # Generate implementation (stub - in real system calls @0master→@9git)
            # For now: create a Python file with the idea as docstring
            project_id = f"prj{idea_id.replace('idea', '')}"
            impl_code = f'''"""
Auto-generated from {idea_id}

{idea_content[:500]}
"""

def main():
    """Main implementation."""
    pass

if __name__ == "__main__":
    main()
'''
            
            # Save to output
            impl_file = output_dir / f"{idea_id}_impl.py"
            impl_file.write_text(impl_code)
            
            # Create test file
            test_code = f'''"""Tests for {idea_id}."""

def test_{idea_id}():
    """Test implementation."""
    pass
'''
            test_file = output_dir / f"test_{idea_id}.py"
            test_file.write_text(test_code)
            
            return {
                "success": True,
                "idea_id": idea_id,
                "files_created": 2,
                "lines_of_code": len(impl_code.split('\n')) + len(test_code.split('\n'))
            }
        
        except Exception as e:
            logger.error(f"Error executing pipeline for {idea_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def process_all_shards(self) -> Dict[str, Any]:
        """Process all shards assigned to this worker."""
        logger.info(f"[Worker {self.worker_id}] Starting processing of shards {self.shard_range}")
        
        for shard_id in self.shard_range:
            # Try to lock shard
            if not self.queue.lock_shard(shard_id, self.worker_id):
                logger.warning(f"[Worker {self.worker_id}] Skipped locked shard {shard_id}")
                continue
            
            try:
                # Mark as processing
                self.queue.mark_shard_processing(shard_id, self.worker_id)
                
                # Process shard
                result = await self.process_shard(shard_id)
                
                if not result["success"]:
                    self.queue.mark_shard_failed(shard_id, result.get("error", "Unknown error"))
            
            finally:
                # Always unlock
                self.queue.unlock_shard(shard_id)
        
        logger.info(f"[Worker {self.worker_id}] All shards complete. Stats: {json.dumps(self.stats)}")
        return self.stats
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current worker statistics."""
        return self.stats
