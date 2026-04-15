#!/usr/bin/env python
"""Simple test runner for all projects."""

import sys
import os

# Add each project to path and run basic tests
projects = {
    "prj000111": {
        "module": "api_docs_generator",
        "class": "APIDocGenerator",
        "test": lambda: test_api_docs()
    },
    "prj000112": {
        "module": "ruff_precommit",
        "class": "RuffConfig",
        "test": lambda: test_ruff_precommit()
    },
    "prj000113": {
        "module": "benchmark_runner",
        "class": "BenchmarkRunner",
        "test": lambda: test_benchmark()
    },
    "prj000114": {
        "module": "jwt_manager",
        "class": "JWTEncoder",
        "test": lambda: test_jwt()
    },
    "prj000115": {
        "module": "global_state",
        "class": "GlobalState",
        "test": lambda: test_global_state()
    }
}

def test_api_docs():
    """Test API docs generator."""
    from api_docs_generator import APIDocGenerator
    gen = APIDocGenerator()
    
    def get_user(user_id: int) -> dict:
        """Get user."""
        return {"id": user_id}
    
    gen.register_endpoint(get_user, method="GET", path="/users/{id}")
    spec = gen.generate_openapi_spec()
    
    assert spec["openapi"] == "3.0.0"
    assert "/users/{id}" in spec["paths"]
    print("✓ prj000111: API Docs tests passed")

def test_ruff_precommit():
    """Test Ruff pre-commit."""
    from ruff_precommit import RuffConfig, RuffVersionManager
    config = RuffConfig()
    is_valid, errors = config.validate()
    
    assert is_valid is True
    
    mgr = RuffVersionManager("0.1.0")
    assert mgr.compare_versions("1.0.0", "0.5.0") > 0
    print("✓ prj000112: Ruff Pre-Commit tests passed")

def test_benchmark():
    """Test benchmark runner."""
    from benchmark_runner import BenchmarkResult, ResultsAnalyzer
    from datetime import datetime
    
    result = BenchmarkResult(
        name="bench",
        iterations=1,
        mean_ns=1000.0,
        std_dev_ns=50.0,
        min_ns=950.0,
        max_ns=1050.0,
        timestamp=datetime.now().isoformat()
    )
    
    assert result.throughput() > 0
    
    analyzer = ResultsAnalyzer([result])
    stats = analyzer.calculate_statistics()
    assert stats["count"] == 1
    print("✓ prj000113: Benchmark tests passed")

def test_jwt():
    """Test JWT manager."""
    from jwt_manager import JWTEncoder, RefreshTokenManager
    from datetime import datetime
    
    encoder = JWTEncoder("secret-key")
    now = int(datetime.utcnow().timestamp())
    
    claims = {"sub": "user", "exp": now + 3600, "iat": now}
    token = encoder.encode(claims)
    
    is_valid, decoded, error = encoder.decode(token)
    assert is_valid is True
    assert decoded["sub"] == "user"
    
    manager = RefreshTokenManager(encoder)
    access, refresh = manager.generate_token_pair("user123")
    assert isinstance(access, str)
    assert isinstance(refresh, str)
    print("✓ prj000114: JWT tests passed")

def test_global_state():
    """Test global state."""
    from global_state import GlobalState
    
    state = GlobalState()
    state.set("key", "value")
    assert state.get("key") == "value"
    
    state.set("user.name", "Alice")
    assert state.get("user.name") == "Alice"
    
    changes = []
    state.subscribe(lambda c: changes.append(c))
    state.set("test", "data")
    assert len(changes) == 1
    print("✓ prj000115: Global State tests passed")

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    all_passed = True
    
    for project_id, info in projects.items():
        project_dir = os.path.join(base_dir, project_id)
        if os.path.exists(project_dir):
            sys.path.insert(0, project_dir)
            try:
                info["test"]()
            except Exception as e:
                print(f"✗ {project_id}: {e}")
                all_passed = False
            finally:
                sys.path.pop(0)
    
    if all_passed:
        print("\n✓ All projects pass basic tests!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed")
        sys.exit(1)
