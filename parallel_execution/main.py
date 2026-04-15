#!/usr/bin/env python3
"""
Main entry point for parallel execution system.

Usage:
    python main.py [--workers N] [--shards N] [--telegram]

Example:
    python main.py --workers 10 --shards 422 --telegram
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from parallel_execution.orchestrator import Orchestrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Parallel execution of 200K+ ideas across PyAgent 9-stage pipeline"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Number of worker processes (default: 10)"
    )
    parser.add_argument(
        "--shards",
        type=int,
        default=422,
        help="Total number of shards (default: 422)"
    )
    parser.add_argument(
        "--shards-dir",
        default="/home/dev/PyAgent/docs/project/execution_shards",
        help="Path to shards directory"
    )
    parser.add_argument(
        "--output-dir",
        default="/home/dev/PyAgent/implementations/generated_code",
        help="Path to output directory"
    )
    parser.add_argument(
        "--telegram",
        action="store_true",
        help="Enable Telegram progress reports"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run (don't actually execute)"
    )
    
    args = parser.parse_args()
    
    # Validate
    shards_dir = Path(args.shards_dir)
    if not shards_dir.exists():
        logger.error(f"Shards directory not found: {shards_dir}")
        return 1
    
    if args.workers < 1 or args.workers > 100:
        logger.error(f"Workers must be 1-100, got {args.workers}")
        return 1
    
    if args.shards < 1:
        logger.error(f"Shards must be > 0, got {args.shards}")
        return 1
    
    logger.info(f"Configuration:")
    logger.info(f"  Workers: {args.workers}")
    logger.info(f"  Shards: {args.shards}")
    logger.info(f"  Shards/Worker: {args.shards // args.workers}")
    logger.info(f"  Shards Dir: {shards_dir}")
    logger.info(f"  Output Dir: {args.output_dir}")
    logger.info(f"  Telegram: {args.telegram}")
    
    if args.dry_run:
        logger.info("DRY RUN MODE - no actual execution")
        return 0
    
    # Create orchestrator
    orchestrator = Orchestrator(
        num_workers=args.workers,
        total_shards=args.shards,
        shards_dir=str(shards_dir),
        output_base=args.output_dir
    )
    
    # Run
    try:
        result = asyncio.run(orchestrator.run())
        return 0
    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
