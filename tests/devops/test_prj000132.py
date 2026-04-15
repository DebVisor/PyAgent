"""Tests for prj000132: Kubernetes Deployment Validation."""
import pytest, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from devops.k8s_validation import K8sValidator, ValidationResult, ValidationConfig

class TestK8sValidator:
    def test_validator_init(self):
        validator = K8sValidator()
        assert validator is not None

    def test_validate_valid_manifest(self):
        validator = K8sValidator()
        manifest = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {"name": "test-pod"}
        }
        result = validator.validate_manifest(manifest)
        assert isinstance(result, ValidationResult)

    def test_validate_missing_fields(self):
        validator = K8sValidator()
        manifest = {"apiVersion": "v1"}
        result = validator.validate_manifest(manifest)
        assert not result.valid

    def test_config_creation(self):
        config = ValidationConfig(cluster_name="test", strict_mode=True)
        assert config.cluster_name == "test"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
