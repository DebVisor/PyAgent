#!/usr/bin/env python3
"""
Simplified Mega Executor v2 - No external dependencies
200,672 ideas | 422 shards | 14 workers
"""

import os
import sys
import time
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import argparse
import logging

sys.path.insert(0, '/home/dev/PyAgent')

from advanced_project_generator import AdvancedProjectGenerator, AdvancedCodeGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger("SimpleMegaExecutor")


class SimpleMegaExecutor:
    """Simplified executor without database dependencies"""
    
    def __init__(self, execution_id="mega-002", workers=14, output_base=None):
        self.execution_id = execution_id
        self.num_workers = workers
        self.output_base = Path(output_base or "/home/dev/PyAgent/generated_projects_v2")
        
        self.project_gen = AdvancedProjectGenerator()
        self.code_gen = AdvancedCodeGenerator(self.project_gen)
        
        self.total_ideas = 200672
        self.total_shards = 422
        self.ideas_per_shard = 475
        
        self.execution_start = datetime.now()
        self.results = {"workers": {}, "total": {}}
    
    def initialize(self) -> bool:
        """Initialize"""
        try:
            logger.info("=" * 80)
            logger.info("🚀 SIMPLIFIED MEGA EXECUTOR v2")
            logger.info("=" * 80)
            logger.info(f"📊 Configuration:")
            logger.info(f"   • Workers: {self.num_workers}")
            logger.info(f"   • Total Ideas: {self.total_ideas:,}")
            logger.info(f"   • Total Shards: {self.total_shards}")
            logger.info(f"   • Output: {self.output_base}")
            logger.info("")
            
            self.output_base.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Init failed: {e}")
            return False
    
    def execute_shard(self, worker_id: int, shard_id: int) -> dict:
        """Execute one shard"""
        shard_start_idx = shard_id * self.ideas_per_shard
        shard_end_idx = min(shard_start_idx + self.ideas_per_shard, self.total_ideas)
        
        results = {
            "shard_id": shard_id,
            "worker_id": worker_id,
            "ideas": 0,
            "files": 0,
            "loc": 0
        }
        
        try:
            for idea_id in range(shard_start_idx, shard_end_idx):
                try:
                    structure = self.project_gen.generate_project_structure(
                        idea_id, worker_id, shard_id
                    )
                    project_dir = self.project_gen.create_directory_structure(
                        worker_id, shard_id, idea_id
                    )
                    
                    category = structure["category"]
                    primary_template = structure["primary_template"]
                    secondary_templates = structure["secondary_templates"]
                    
                    # Generate primary
                    primary_code = self.code_gen.generate_code(idea_id, category, primary_template)
                    primary_ext = self.project_gen.templates[primary_template]["ext"]
                    (project_dir / f"idea_{idea_id:06d}{primary_ext}").write_text(primary_code)
                    
                    results["files"] += 1
                    results["loc"] += len(primary_code.split('\n'))
                    
                    # Tests
                    if self.project_gen.templates[primary_template]["has_tests"]:
                        test_code = self.code_gen.generate_test_code(idea_id, category, primary_template)
                        (project_dir / f"test_idea_{idea_id:06d}{primary_ext}").write_text(test_code)
                        results["files"] += 1
                        results["loc"] += len(test_code.split('\n'))
                    
                    # Secondary implementations
                    for secondary in secondary_templates:
                        if secondary == primary_template:
                            continue
                        
                        sec_code = self.code_gen.generate_code(idea_id, category, secondary)
                        sec_ext = self.project_gen.templates[secondary]["ext"]
                        (project_dir / f"impl_{idea_id:06d}{sec_ext}").write_text(sec_code)
                        results["files"] += 1
                        results["loc"] += len(sec_code.split('\n'))
                        
                        if self.project_gen.templates[secondary]["has_tests"]:
                            sec_test = self.code_gen.generate_test_code(idea_id, category, secondary)
                            (project_dir / f"test_impl_{idea_id:06d}{sec_ext}").write_text(sec_test)
                            results["files"] += 1
                            results["loc"] += len(sec_test.split('\n'))
                    
                    # Config
                    config = self.code_gen.generate_config(idea_id, category)
                    (project_dir / "config.yaml").write_text(config)
                    results["files"] += 1
                    results["loc"] += len(config.split('\n'))
                    
                    # Dockerfile
                    dockerfile = self.code_gen.generate_dockerfile(idea_id, category)
                    (project_dir / "Dockerfile").write_text(dockerfile)
                    results["files"] += 1
                    results["loc"] += len(dockerfile.split('\n'))
                    
                    # README
                    readme = self.code_gen.generate_readme(idea_id, category)
                    (project_dir / "README.md").write_text(readme)
                    results["files"] += 1
                    results["loc"] += len(readme.split('\n'))
                    
                    # Metadata
                    metadata = self.project_gen.generate_project_metadata(structure)
                    (project_dir / "project.json").write_text(metadata)
                    results["files"] += 1
                    
                    # CI/CD
                    (project_dir / ".github_workflows_ci.yaml").write_text(f"# CI/CD for idea {idea_id}\n")
                    results["files"] += 1
                    results["loc"] += 1
                    
                    results["ideas"] += 1
                    
                except Exception as e:
                    logger.warning(f"Idea {idea_id} error: {e}")
            
            logger.info(f"👷 W{worker_id:02d} S{shard_id:03d}: "
                       f"{results['ideas']} ideas, {results['files']} files, {results['loc']:,} LOC")
            return results
        
        except Exception as e:
            logger.error(f"❌ Shard {shard_id} failed: {e}")
            return results
    
    def execute_worker(self, worker_id: int) -> dict:
        """Execute one worker"""
        shards_per_worker = self.total_shards // self.num_workers
        start_shard = worker_id * shards_per_worker
        end_shard = min(start_shard + shards_per_worker, self.total_shards) if worker_id < self.num_workers - 1 else self.total_shards
        
        total_ideas = 0
        total_files = 0
        total_loc = 0
        
        logger.info(f"👷 Worker {worker_id:02d} START (shards {start_shard}-{end_shard-1})")
        
        for shard_id in range(start_shard, end_shard):
            results = self.execute_shard(worker_id, shard_id)
            total_ideas += results["ideas"]
            total_files += results["files"]
            total_loc += results["loc"]
        
        logger.info(f"✅ Worker {worker_id:02d} COMPLETE: {total_ideas:,} ideas, {total_files:,} files, {total_loc:,} LOC")
        
        return {
            "worker_id": worker_id,
            "ideas": total_ideas,
            "files": total_files,
            "loc": total_loc
        }
    
    def run(self) -> bool:
        """Run execution"""
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"🚀 STARTING {self.num_workers} WORKERS")
        logger.info("=" * 80)
        
        try:
            start = time.time()
            
            with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
                futures = {
                    executor.submit(self.execute_worker, i): i
                    for i in range(self.num_workers)
                }
                
                total_ideas = 0
                total_files = 0
                total_loc = 0
                
                for future in as_completed(futures):
                    result = future.result()
                    total_ideas += result["ideas"]
                    total_files += result["files"]
                    total_loc += result["loc"]
                    self.results["workers"][result["worker_id"]] = result
            
            duration = time.time() - start
            
            self.results["total"] = {
                "ideas": total_ideas,
                "files": total_files,
                "loc": total_loc,
                "duration": duration
            }
            
            logger.info("")
            logger.info("=" * 80)
            logger.info("🏁 EXECUTION COMPLETE")
            logger.info("=" * 80)
            logger.info(f"✅ Ideas: {total_ideas:,}")
            logger.info(f"✅ Files: {total_files:,}")
            logger.info(f"✅ LOC: {total_loc:,}")
            logger.info(f"✅ Duration: {duration:.1f}s")
            logger.info(f"✅ Rate: {total_ideas/duration:.1f} ideas/sec")
            logger.info("")
            
            # Save results
            results_file = self.output_base.parent / f"execution_{self.execution_id}_results.json"
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            logger.info(f"📁 Results: {results_file}")
            logger.info("")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Execution failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    parser = argparse.ArgumentParser(description="Simplified Mega Executor v2")
    parser.add_argument("--execution-id", default="mega-002")
    parser.add_argument("--workers", type=int, default=14)
    parser.add_argument("--output", default=None)
    
    args = parser.parse_args()
    
    executor = SimpleMegaExecutor(
        execution_id=args.execution_id,
        workers=args.workers,
        output_base=args.output
    )
    
    if not executor.initialize():
        sys.exit(1)
    
    if not executor.run():
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
