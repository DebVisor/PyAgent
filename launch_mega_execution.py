#!/usr/bin/env python3
"""
Mega Execution Launcher
Orchestrates parallel execution of 200K ideas with monitoring
"""

import subprocess
import sys
import time
import os
from pathlib import Path
import argparse


def check_prerequisites():
    """Check all prerequisites"""
    print("\n" + "=" * 80)
    print("🔍 CHECKING PREREQUISITES")
    print("=" * 80)
    
    checks = []
    
    # Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    checks.append(("Python 3.8+", python_version >= "3.8", f"v{python_version}"))
    
    # PostgreSQL
    try:
        result = subprocess.run(["psql", "--version"], capture_output=True, text=True)
        pg_version = result.stdout.strip()
        checks.append(("PostgreSQL", result.returncode == 0, pg_version))
    except:
        checks.append(("PostgreSQL", False, "Not found"))
    
    # psycopg2
    try:
        import psycopg2
        checks.append(("psycopg2", True, "Installed"))
    except:
        checks.append(("psycopg2", False, "Not installed"))
    
    # PyAgent
    pyagent_path = Path("/home/dev/PyAgent")
    checks.append(("PyAgent", pyagent_path.exists(), str(pyagent_path)))
    
    # Memory system
    memory_system_path = pyagent_path / "memory_system"
    checks.append(("Memory System", memory_system_path.exists(), str(memory_system_path)))
    
    for name, status, info in checks:
        symbol = "✅" if status else "❌"
        print(f"{symbol} {name}: {info}")
    
    all_ok = all(check[1] for check in checks)
    
    if all_ok:
        print("\n✅ All prerequisites met!")
    else:
        print("\n❌ Some prerequisites missing!")
        return False
    
    return True


def setup_database():
    """Setup PostgreSQL database"""
    print("\n" + "=" * 80)
    print("🗄️  SETTING UP DATABASE")
    print("=" * 80)
    
    try:
        # Check if database exists
        result = subprocess.run(
            ["psql", "-lqt"],
            capture_output=True,
            text=True
        )
        
        if "mega_execution" not in result.stdout:
            print("📦 Creating database 'mega_execution'...")
            subprocess.run(
                ["createdb", "mega_execution"],
                check=True
            )
            print("✅ Database created")
        else:
            print("✅ Database 'mega_execution' exists")
        
        return True
    
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False


def start_executor(execution_id: str, workers: int, output_dir: str):
    """Start the parallel executor"""
    print("\n" + "=" * 80)
    print("🚀 STARTING PARALLEL EXECUTOR")
    print("=" * 80)
    
    cmd = [
        "python3",
        "/home/dev/PyAgent/parallel_mega_executor.py",
        "--execution-id", execution_id,
        "--workers", str(workers),
        "--output", output_dir
    ]
    
    print(f"\n📝 Command:\n   {' '.join(cmd)}\n")
    
    try:
        process = subprocess.Popen(cmd)
        return process
    except Exception as e:
        print(f"❌ Failed to start executor: {e}")
        return None


def start_monitor(execution_id: str):
    """Start the live monitor"""
    print("\n" + "=" * 80)
    print("📊 STARTING LIVE MONITOR")
    print("=" * 80)
    
    cmd = [
        "python3",
        "/home/dev/PyAgent/memory_system/live_monitor.py",
        "--execution-id", execution_id,
        "--until-complete"
    ]
    
    print(f"\n📝 Command:\n   {' '.join(cmd)}\n")
    
    try:
        process = subprocess.Popen(cmd)
        return process
    except Exception as e:
        print(f"❌ Failed to start monitor: {e}")
        return None


def main():
    """Main launcher"""
    parser = argparse.ArgumentParser(description="Mega Execution Launcher")
    parser.add_argument("--execution-id", default="mega-001", help="Execution ID")
    parser.add_argument("--workers", type=int, default=10, help="Number of workers")
    parser.add_argument("--output", default="/home/dev/PyAgent/generated_projects",
                       help="Output directory")
    parser.add_argument("--skip-checks", action="store_true", help="Skip prerequisites check")
    parser.add_argument("--skip-monitor", action="store_true", help="Skip launching monitor")
    parser.add_argument("--sequential", action="store_true",
                       help="Run executor and monitor sequentially (not parallel)")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 80)
    print("🎯 MEGA EXECUTION LAUNCHER - 200K IDEAS")
    print("=" * 80)
    
    # Check prerequisites
    if not args.skip_checks:
        if not check_prerequisites():
            sys.exit(1)
    
    # Setup database
    if not setup_database():
        sys.exit(1)
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output directory: {output_dir}")
    
    # Start processes
    print("\n" + "=" * 80)
    print("🎬 LAUNCHING EXECUTION")
    print("=" * 80)
    
    executor_process = start_executor(args.execution_id, args.workers, str(output_dir))
    if not executor_process:
        sys.exit(1)
    
    if args.sequential:
        # Wait for executor to complete
        print("\n⏳ Waiting for executor to complete...")
        executor_process.wait()
        
        # Then start monitor
        if not args.skip_monitor:
            monitor_process = start_monitor(args.execution_id)
            if monitor_process:
                monitor_process.wait()
    else:
        # Wait a bit before starting monitor
        time.sleep(2)
        
        if not args.skip_monitor:
            monitor_process = start_monitor(args.execution_id)
        else:
            monitor_process = None
        
        # Wait for executor
        print("\n⏳ Waiting for executor to complete...")
        executor_process.wait()
        
        # Wait for monitor if started
        if monitor_process:
            print("⏳ Waiting for monitor to complete...")
            monitor_process.wait()
    
    print("\n" + "=" * 80)
    print("✅ MEGA EXECUTION COMPLETE")
    print("=" * 80)
    print(f"\nResults:")
    print(f"  Execution ID: {args.execution_id}")
    print(f"  Output: {output_dir}")
    print(f"\nYou can query results with:")
    print(f"  python /home/dev/PyAgent/memory_system/live_monitor.py")
    print(f"    --execution-id {args.execution_id} --once")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
