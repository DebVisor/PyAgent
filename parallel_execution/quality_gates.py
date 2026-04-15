"""Quality gates for per-shard validation."""

import ast
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Tuple, List
import logging

logger = logging.getLogger(__name__)


class QualityGates:
    """Enforces quality standards on generated code per shard."""
    
    def __init__(self, threshold_coverage: float = 0.85, threshold_lint: float = 8.0):
        self.threshold_coverage = threshold_coverage
        self.threshold_lint = threshold_lint
    
    def validate_syntax(self, code: str, filename: str = "generated.py") -> Tuple[bool, str]:
        """Validate Python syntax via ast.parse."""
        try:
            ast.parse(code)
            return True, "Syntax valid"
        except SyntaxError as e:
            return False, f"Syntax error: {e.msg} at line {e.lineno}"
    
    def check_type_hints(self, code: str) -> Tuple[bool, float]:
        """Check for type hints using mypy. Returns (passed, score 0-1)."""
        try:
            # Write temp file
            temp_path = Path("/tmp/check_types.py")
            temp_path.write_text(code)
            
            # Run mypy
            result = subprocess.run(
                ["mypy", str(temp_path), "--ignore-missing-imports"],
                capture_output=True,
                timeout=10
            )
            
            # Score based on mypy output
            if result.returncode == 0:
                return True, 1.0
            else:
                # Count type errors
                output = result.stderr.decode() + result.stdout.decode()
                error_count = output.count("error:")
                score = max(0.0, 1.0 - (error_count * 0.1))
                return error_count < 5, score
        except Exception as e:
            logger.warning(f"Type checking failed: {e}")
            return False, 0.5
    
    def validate_docstrings(self, code: str) -> Tuple[bool, float]:
        """Check docstring coverage. Score = (with_docstrings / total_functions)."""
        try:
            tree = ast.parse(code)
            total_funcs = 0
            with_docs = 0
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    total_funcs += 1
                    if ast.get_docstring(node):
                        with_docs += 1
            
            if total_funcs == 0:
                return True, 1.0
            
            score = with_docs / total_funcs
            return score >= 0.9, score
        except Exception as e:
            logger.warning(f"Docstring check failed: {e}")
            return False, 0.0
    
    def check_coverage(self, project_path: str) -> Tuple[bool, float]:
        """Run coverage.py on test directory. Returns (passed, coverage %)."""
        try:
            result = subprocess.run(
                ["coverage", "run", "-m", "pytest", project_path],
                capture_output=True,
                timeout=30,
                cwd=project_path
            )
            
            coverage_result = subprocess.run(
                ["coverage", "report", "--skip-empty"],
                capture_output=True,
                timeout=10,
                cwd=project_path
            )
            
            output = coverage_result.stdout.decode()
            # Parse "TOTAL" line for percentage
            for line in output.split('\n'):
                if 'TOTAL' in line:
                    parts = line.split()
                    if parts[-1].endswith('%'):
                        pct = float(parts[-1].rstrip('%')) / 100.0
                        return pct >= self.threshold_coverage, pct
            
            return False, 0.0
        except Exception as e:
            logger.warning(f"Coverage check failed: {e}")
            return False, 0.0
    
    def lint_code(self, code: str) -> Tuple[bool, float]:
        """Run ruff linter. Score = (lines_clean / total_lines)."""
        try:
            temp_path = Path("/tmp/lint_check.py")
            temp_path.write_text(code)
            
            result = subprocess.run(
                ["ruff", "check", str(temp_path)],
                capture_output=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, 1.0
            
            output = result.stdout.decode() + result.stderr.decode()
            error_count = output.count("error") + output.count("warning")
            
            line_count = len(code.split('\n'))
            score = max(0.0, 1.0 - (error_count / max(line_count, 1)))
            
            return score >= self.threshold_lint / 10.0, score
        except Exception as e:
            logger.warning(f"Linting failed: {e}")
            return False, 0.5
    
    def validate_tests(self, project_path: str) -> Tuple[bool, int]:
        """Run pytest on project. Returns (passed, test_count)."""
        try:
            result = subprocess.run(
                ["pytest", project_path, "-v", "--tb=short"],
                capture_output=True,
                timeout=60,
                cwd=project_path
            )
            
            output = result.stdout.decode() + result.stderr.decode()
            # Count passed tests
            passed = output.count(" PASSED")
            failed = output.count(" FAILED")
            
            return result.returncode == 0, (passed, failed)
        except Exception as e:
            logger.warning(f"Test execution failed: {e}")
            return False, (0, -1)
    
    def run_all_gates(self, code: str, project_path: str = None) -> Dict[str, Any]:
        """Run all quality gates. Returns comprehensive report."""
        report = {
            "passed": True,
            "gates": {},
            "score": 0.0
        }
        
        # Syntax validation
        syntax_ok, syntax_msg = self.validate_syntax(code)
        report["gates"]["syntax"] = {
            "passed": syntax_ok,
            "message": syntax_msg,
            "score": 1.0 if syntax_ok else 0.0
        }
        
        # Type hints
        types_ok, types_score = self.check_type_hints(code)
        report["gates"]["type_hints"] = {
            "passed": types_ok,
            "score": types_score
        }
        
        # Docstrings
        docs_ok, docs_score = self.validate_docstrings(code)
        report["gates"]["docstrings"] = {
            "passed": docs_ok,
            "score": docs_score
        }
        
        # Linting
        lint_ok, lint_score = self.lint_code(code)
        report["gates"]["linting"] = {
            "passed": lint_ok,
            "score": lint_score
        }
        
        # Coverage (if project path provided)
        if project_path:
            cov_ok, cov_score = self.check_coverage(project_path)
            report["gates"]["coverage"] = {
                "passed": cov_ok,
                "score": cov_score,
                "threshold": self.threshold_coverage
            }
            
            # Tests
            tests_ok, test_counts = self.validate_tests(project_path)
            report["gates"]["tests"] = {
                "passed": tests_ok,
                "passed_count": test_counts[0],
                "failed_count": test_counts[1]
            }
        
        # Calculate overall score
        scores = [g.get("score", 0.0) for g in report["gates"].values()]
        report["score"] = sum(scores) / len(scores) if scores else 0.0
        
        # Determine if all gates passed
        report["passed"] = all(g.get("passed", False) for g in report["gates"].values())
        
        return report
