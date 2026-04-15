"""Tests for prj000133: Terraform Compliance Checks."""
import pytest, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from devops.terraform_check import TerraformChecker, ComplianceResult, ComplianceConfig

class TestTerraformChecker:
    def test_checker_init(self):
        checker = TerraformChecker()
        assert checker is not None

    def test_check_valid_config(self):
        checker = TerraformChecker()
        config = {"resource": {"aws_instance": {"test": {}}}}
        result = checker.check_configuration(config)
        assert isinstance(result, ComplianceResult)

    def test_syntax_validation(self):
        checker = TerraformChecker()
        assert checker.validate_syntax({"resource": {}}) is True
        assert checker.validate_syntax("invalid") is False

    def test_config_creation(self):
        config = ComplianceConfig(strict_mode=True)
        assert config.strict_mode is True

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
