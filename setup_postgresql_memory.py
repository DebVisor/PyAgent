#!/usr/bin/env python3
"""
PostgreSQL Memory System Setup & Configuration

Switches PyAgent memory backend from holographic to PostgreSQL.
Sets up database, schema, and enables the unified memory system.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PostgreSQLSetup:
    """Setup and configuration for PostgreSQL memory backend"""
    
    def __init__(self):
        self.pyagent_root = Path.home() / "PyAgent"
        self.memory_system = self.pyagent_root / "memory_system"
        self.config_file = self.pyagent_root / "memory_config.json"
        
        self.config = {
            "backend": "postgresql",
            "database": {
                "host": "localhost",
                "port": 5432,
                "database": "hermes_memory",
                "user": "postgres",
                "password": os.getenv("POSTGRES_PASSWORD", "postgres")
            },
            "virtual_paths": [
                "kv",           # Key-value store
                "btree",        # B-tree index
                "linked_list",  # Linked lists
                "graph",        # DAG graphs
                "kanban",       # Kanban boards
                "lessons",      # Lessons learned
                "code_ledger"   # Code metrics
            ],
            "features": {
                "transactions": True,
                "savepoints": True,
                "acid_compliance": True,
                "replication": False,
                "sharding": False
            },
            "created_at": None,
            "initialized": False
        }
    
    def print_banner(self):
        """Print setup banner"""
        print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║          🗄️  PYAGENT POSTGRESQL MEMORY SYSTEM SETUP 🗄️                   ║
║                                                                            ║
║              Switching from Holographic to PostgreSQL Backend             ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
        """)
    
    def check_prerequisites(self) -> bool:
        """Check if PostgreSQL is installed and running"""
        print("\n📋 Checking prerequisites...\n")
        
        # Check Python
        try:
            import psycopg2
            print("  ✓ psycopg2 available (Python PostgreSQL driver)")
        except ImportError:
            print("  ❌ psycopg2 not installed")
            print("     Install with: pip install psycopg2-binary")
            return False
        
        # Check PostgreSQL
        ret = os.system("which psql > /dev/null 2>&1")
        if ret == 0:
            print("  ✓ PostgreSQL client installed")
        else:
            print("  ❌ PostgreSQL client not found")
            print("     Install PostgreSQL: https://www.postgresql.org/download/")
            return False
        
        # Check memory_system module
        if self.memory_system.exists():
            print("  ✓ Memory system module found")
        else:
            print("  ❌ Memory system module not found at", self.memory_system)
            return False
        
        return True
    
    def test_postgres_connection(self) -> bool:
        """Test PostgreSQL connection"""
        print("\n🔗 Testing PostgreSQL connection...\n")
        
        try:
            import psycopg2
            
            conn = psycopg2.connect(
                host=self.config["database"]["host"],
                port=self.config["database"]["port"],
                user=self.config["database"]["user"],
                password=self.config["database"]["password"],
                database="postgres"
            )
            
            cur = conn.cursor()
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            
            print(f"  ✓ Connected to PostgreSQL")
            print(f"    {version[:60]}...")
            
            cur.close()
            conn.close()
            return True
        
        except Exception as e:
            print(f"  ❌ Connection failed: {e}")
            print("\n  Troubleshooting:")
            print("    1. Ensure PostgreSQL server is running")
            print("    2. Check host/port settings")
            print("    3. Verify credentials")
            return False
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        print("\n💾 Saving configuration...\n")
        
        try:
            from datetime import datetime, timezone
            self.config["created_at"] = datetime.now(timezone.utc).isoformat()
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            print(f"  ✓ Config saved to {self.config_file}")
            return True
        
        except Exception as e:
            print(f"  ❌ Error saving config: {e}")
            return False
    
    def initialize_memory_system(self) -> bool:
        """Initialize the PostgreSQL memory system"""
        print("\n🗄️  Initializing memory system...\n")
        
        try:
            # Add to path
            sys.path.insert(0, str(self.pyagent_root))
            
            from memory_system import UnifiedMemorySystem
            
            # Create instance
            memory = UnifiedMemorySystem(
                host=self.config["database"]["host"],
                port=self.config["database"]["port"],
                database=self.config["database"]["database"],
                user=self.config["database"]["user"],
                password=self.config["database"]["password"]
            )
            
            # Initialize
            if memory.initialize():
                print("  ✓ Memory system initialized")
                print("  ✓ Database schema created")
                print("  ✓ All virtual paths enabled:")
                for path in self.config["virtual_paths"]:
                    print(f"    - {path}")
                
                self.config["initialized"] = True
                return True
            else:
                print("  ❌ Failed to initialize memory system")
                return False
        
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_usage_guide(self):
        """Generate usage guide"""
        guide = """
================================================================================
📖 POSTGRESQL MEMORY SYSTEM USAGE GUIDE
================================================================================

1. BASIC USAGE
─────────────

  from memory_system import UnifiedMemorySystem
  
  # Initialize
  memory = UnifiedMemorySystem()
  memory.initialize()
  
  # Access virtual paths
  memory.kv.set("key", "value")
  memory.btree.insert(1, "item")
  memory.linked_list.append("node")
  memory.graph.add_edge("A", "B")
  memory.kanban.add_task("BACKLOG", "task1")
  memory.lessons.record("pattern", "lesson")
  memory.code_ledger.log_impl("feature", 100)


2. TRANSACTIONS
───────────────

  with memory.transaction() as tx:
      memory.kv.set("key1", "val1")
      memory.kv.set("key2", "val2")
      # Auto-commit on exit
  
  # Or with explicit control
  tx = memory.new_transaction()
  tx.begin_sync()
  try:
      memory.kv.set("key", "value")
      tx.commit_sync()
  except Exception as e:
      tx.rollback_sync()


3. VIRTUAL PATHS
────────────────

  KV Store - Fast O(1) lookups with TTL
  ├── memory.kv.set(key, value, ttl_seconds=3600)
  ├── memory.kv.get(key)
  ├── memory.kv.delete(key)
  └── memory.kv.scan(prefix="user:")
  
  B-Tree Index - Sorted range queries
  ├── memory.btree.insert(key, value)
  ├── memory.btree.range(min_key, max_key)
  ├── memory.btree.scan()
  └── memory.btree.delete(key)
  
  Linked List - Ordered sequences
  ├── memory.linked_list.append(value)
  ├── memory.linked_list.pop()
  ├── memory.linked_list.iterate()
  └── memory.linked_list.length()
  
  Graph (DAG) - Dependencies
  ├── memory.graph.add_node(id)
  ├── memory.graph.add_edge(from_id, to_id)
  ├── memory.graph.get_dependencies(id)
  └── memory.graph.topological_sort()
  
  Kanban Board - Workflow
  ├── memory.kanban.add_task(status, task_id)
  ├── memory.kanban.move_task(task_id, to_status)
  ├── memory.kanban.get_tasks(status)
  └── memory.kanban.get_board()
  
  Lessons Learned - Pattern tracking
  ├── memory.lessons.record(pattern, lesson, severity)
  ├── memory.lessons.find_similar(pattern)
  ├── memory.lessons.increase_recurrence(lesson_id)
  └── memory.lessons.get_high_recurrence()
  
  Code Ledger - Implementation metrics
  ├── memory.code_ledger.log_impl(feature, loc)
  ├── memory.code_ledger.get_metrics(feature)
  ├── memory.code_ledger.total_loc()
  └── memory.code_ledger.get_implementations()


4. CONFIGURATION
────────────────

  Config file: ~/PyAgent/memory_config.json
  
  Customize:
  {
    "database": {
      "host": "localhost",
      "port": 5432,
      "database": "hermes_memory",
      "user": "postgres",
      "password": "your_password"
    },
    "features": {
      "transactions": true,
      "savepoints": true,
      "acid_compliance": true
    }
  }


5. MONITORING & MAINTENANCE
────────────────────────────

  Check database:
  $ psql -U postgres -d hermes_memory -c "\\dt"
  
  View stats:
  $ psql -U postgres -d hermes_memory -c "SELECT * FROM kv_store LIMIT 5;"
  
  Backup:
  $ pg_dump -U postgres hermes_memory > backup.sql
  
  Restore:
  $ psql -U postgres -d hermes_memory < backup.sql


6. TROUBLESHOOTING
───────────────────

  Connection refused?
  $ psql -U postgres  # Test basic connection
  
  Permission denied?
  $ ALTER USER postgres WITH PASSWORD 'new_password';
  
  Database doesn't exist?
  $ createdb -U postgres hermes_memory
  
  Schema issues?
  Run: memory.initialize()  # Reinitialize schema


7. PERFORMANCE TIPS
────────────────────

  - Use KV store for frequent hot reads (O(1))
  - Use B-Tree for range queries
  - Use transactions for atomic multi-operation updates
  - Index key patterns for faster lookups
  - Regular VACUUM to maintain performance


8. BACKUP & RECOVERY
─────────────────────

  Backup:
  $ pg_dump -U postgres -d hermes_memory > hermes_backup.sql
  
  Restore:
  $ psql -U postgres -d hermes_memory < hermes_backup.sql
  
  Scheduled backup:
  $ crontab -e
  0 2 * * * pg_dump -U postgres hermes_memory > ~/backups/hermes_$(date +%Y%m%d).sql

================================================================================
"""
        
        guide_file = self.pyagent_root / "POSTGRESQL_MEMORY_GUIDE.md"
        with open(guide_file, 'w') as f:
            f.write(guide)
        
        print(f"\n📚 Usage guide saved to: {guide_file}")
        print("\nView with: cat ~/PyAgent/POSTGRESQL_MEMORY_GUIDE.md")
    
    def print_summary(self, success: bool):
        """Print setup summary"""
        print("\n" + "=" * 80)
        
        if success:
            print("✅ POSTGRESQL MEMORY SYSTEM SETUP COMPLETE")
            print("=" * 80)
            print(f"\nBackend: PostgreSQL")
            print(f"Database: {self.config['database']['database']}")
            print(f"Host: {self.config['database']['host']}:{self.config['database']['port']}")
            print(f"Config: {self.config_file}")
            print("\nVirtual Paths Enabled:")
            for path in self.config["virtual_paths"]:
                print(f"  ✓ {path}")
            print("\nNext steps:")
            print("  1. Review config: cat ~/PyAgent/memory_config.json")
            print("  2. Read usage guide: cat ~/PyAgent/POSTGRESQL_MEMORY_GUIDE.md")
            print("  3. Test connection: psql -U postgres -d hermes_memory")
            print("  4. Use in code: from memory_system import UnifiedMemorySystem")
        else:
            print("❌ POSTGRESQL MEMORY SYSTEM SETUP FAILED")
            print("=" * 80)
            print("\nReview errors above and fix issues, then run setup again.")
        
        print("\n" + "=" * 80)
    
    def run(self):
        """Run full setup"""
        self.print_banner()
        
        if not self.check_prerequisites():
            self.print_summary(False)
            return False
        
        if not self.test_postgres_connection():
            self.print_summary(False)
            return False
        
        if not self.initialize_memory_system():
            self.print_summary(False)
            return False
        
        if not self.save_config():
            self.print_summary(False)
            return False
        
        self.generate_usage_guide()
        self.print_summary(True)
        return True


if __name__ == "__main__":
    setup = PostgreSQLSetup()
    success = setup.run()
    sys.exit(0 if success else 1)
