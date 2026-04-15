"""PostgreSQL Memory System - Core schema and initialization."""

import os
import psycopg2
from psycopg2.extras import execute_values
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class PostgreSQLMemory:
    """Core PostgreSQL connection and schema manager."""
    
    def __init__(self, 
                 host: str = "localhost",
                 port: int = 5432,
                 database: str = "hermes_memory",
                 user: str = "postgres",
                 password: Optional[str] = None):
        """Initialize PostgreSQL connection."""
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password or os.getenv("POSTGRES_PASSWORD", "postgres")
        
        self.conn = None
        self.connected = False
    
    def connect(self) -> bool:
        """Establish connection to PostgreSQL."""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.connected = True
            logger.info(f"Connected to PostgreSQL: {self.host}:{self.port}/{self.database}")
            return True
        except psycopg2.OperationalError as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    def create_database(self) -> bool:
        """Create the hermes_memory database if it doesn't exist."""
        try:
            # Connect to default postgres database
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database="postgres",
                user=self.user,
                password=self.password
            )
            conn.autocommit = True
            cur = conn.cursor()
            
            # Check if database exists
            cur.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (self.database,)
            )
            
            if not cur.fetchone():
                cur.execute(f"CREATE DATABASE {self.database}")
                logger.info(f"Created database: {self.database}")
            else:
                logger.info(f"Database already exists: {self.database}")
            
            cur.close()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error creating database: {e}")
            return False
    
    def init_schema(self) -> bool:
        """Initialize all required tables and indexes."""
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            cur = self.conn.cursor()
            
            # Enable extensions
            cur.execute("CREATE EXTENSION IF NOT EXISTS hstore")
            cur.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
            
            # 1. KV STORE TABLE
            cur.execute("""
                CREATE TABLE IF NOT EXISTS kv_store (
                    key TEXT PRIMARY KEY,
                    value BYTEA NOT NULL,
                    metadata JSONB,
                    ttl_expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_kv_ttl ON kv_store(ttl_expires_at)")
            
            # 2. B-TREE INDEX TABLE
            cur.execute("""
                CREATE TABLE IF NOT EXISTS btree_nodes (
                    node_id BIGSERIAL PRIMARY KEY,
                    parent_id BIGINT REFERENCES btree_nodes(node_id) ON DELETE CASCADE,
                    key TEXT NOT NULL,
                    value JSONB NOT NULL,
                    left_child_id BIGINT,
                    right_child_id BIGINT,
                    height INT DEFAULT 0,
                    balance_factor INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_btree_key ON btree_nodes(key)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_btree_parent ON btree_nodes(parent_id)")
            
            # 3. LINKED LIST TABLE
            cur.execute("""
                CREATE TABLE IF NOT EXISTS linked_list_nodes (
                    node_id BIGSERIAL PRIMARY KEY,
                    list_id TEXT NOT NULL,
                    data JSONB NOT NULL,
                    prev_node_id BIGINT REFERENCES linked_list_nodes(node_id) ON DELETE CASCADE,
                    next_node_id BIGINT REFERENCES linked_list_nodes(node_id) ON DELETE CASCADE,
                    position INT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    CONSTRAINT unique_list_position UNIQUE(list_id, position)
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_ll_list_id ON linked_list_nodes(list_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_ll_position ON linked_list_nodes(list_id, position)")
            
            # 4. GRAPH EDGES TABLE (DAG for task dependencies)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS graph_nodes (
                    node_id TEXT PRIMARY KEY,
                    node_type TEXT NOT NULL,
                    data JSONB NOT NULL,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS graph_edges (
                    edge_id BIGSERIAL PRIMARY KEY,
                    from_node_id TEXT NOT NULL REFERENCES graph_nodes(node_id) ON DELETE CASCADE,
                    to_node_id TEXT NOT NULL REFERENCES graph_nodes(node_id) ON DELETE CASCADE,
                    edge_type TEXT NOT NULL,
                    weight FLOAT DEFAULT 1.0,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT NOW(),
                    CONSTRAINT unique_edge UNIQUE(from_node_id, to_node_id, edge_type)
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_graph_from ON graph_edges(from_node_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_graph_to ON graph_edges(to_node_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_graph_type ON graph_edges(edge_type)")
            
            # 5. KANBAN BOARD TABLE
            cur.execute("""
                CREATE TABLE IF NOT EXISTS kanban_cards (
                    card_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    priority INT DEFAULT 0,
                    assignee TEXT,
                    project_id TEXT,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    completed_at TIMESTAMP
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_kanban_status ON kanban_cards(status)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_kanban_project ON kanban_cards(project_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_kanban_priority ON kanban_cards(priority)")
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS kanban_board (
                    board_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    columns JSONB NOT NULL,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # 6. LESSONS/LEARNING TABLE
            cur.execute("""
                CREATE TABLE IF NOT EXISTS lessons (
                    lesson_id BIGSERIAL PRIMARY KEY,
                    pattern TEXT NOT NULL,
                    root_cause TEXT NOT NULL,
                    prevention TEXT,
                    first_seen TIMESTAMP,
                    recurrence_count INT DEFAULT 1,
                    promotion_status TEXT DEFAULT 'OPEN',
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_lessons_status ON lessons(promotion_status)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_lessons_pattern ON lessons(pattern)")
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS lesson_occurrences (
                    occurrence_id BIGSERIAL PRIMARY KEY,
                    lesson_id BIGINT NOT NULL REFERENCES lessons(lesson_id) ON DELETE CASCADE,
                    context TEXT,
                    resolved_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # 7. CODE IMPLEMENTATION LEDGER
            cur.execute("""
                CREATE TABLE IF NOT EXISTS code_implementations (
                    impl_id BIGSERIAL PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    idea_id TEXT,
                    file_path TEXT NOT NULL,
                    module_name TEXT,
                    language TEXT DEFAULT 'python',
                    lines_of_code INT,
                    coverage_percent FLOAT,
                    quality_score FLOAT,
                    test_count INT DEFAULT 0,
                    passed_tests INT DEFAULT 0,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_code_project ON code_implementations(project_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_code_idea ON code_implementations(idea_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_code_module ON code_implementations(module_name)")
            
            # 8. EXECUTION TRACKING
            cur.execute("""
                CREATE TABLE IF NOT EXISTS execution_log (
                    log_id BIGSERIAL PRIMARY KEY,
                    worker_id INT,
                    shard_id INT,
                    idea_id TEXT,
                    stage TEXT,
                    status TEXT,
                    duration_ms INT,
                    error_message TEXT,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_exec_worker ON execution_log(worker_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_exec_shard ON execution_log(shard_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_exec_stage ON execution_log(stage)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_exec_status ON execution_log(status)")
            
            self.conn.commit()
            logger.info("Schema initialized successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error initializing schema: {e}")
            self.conn.rollback()
            return False
        finally:
            if cur:
                cur.close()
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.connected = False
            logger.info("Disconnected from PostgreSQL")
    
    def execute_query(self, query: str, params: tuple = None) -> Any:
        """Execute a query and return results."""
        if not self.connected:
            return None
        
        try:
            cur = self.conn.cursor()
            cur.execute(query, params or ())
            result = cur.fetchall()
            cur.close()
            return result
        except Exception as e:
            logger.error(f"Query error: {e}")
            return None
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
