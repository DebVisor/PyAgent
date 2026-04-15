"""
Tests for secret validation script.
"""

import tempfile
from pathlib import Path
from typing import Generator

import pytest

# Import the validation functions
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from validate_secrets import validate_files, check_file_content, check_file_extension


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestFileExtension:
    """Test dangerous file extension detection."""
    
    def test_detects_pem_extension(self, temp_dir: Path) -> None:
        """Should detect .pem files."""
        test_file = temp_dir / "key.pem"
        test_file.write_text("safe content")
        
        is_dangerous, reason = check_file_extension(test_file)
        assert is_dangerous
        assert ".pem" in reason
    
    def test_detects_key_extension(self, temp_dir: Path) -> None:
        """Should detect .key files."""
        test_file = temp_dir / "id.key"
        test_file.write_text("safe content")
        
        is_dangerous, reason = check_file_extension(test_file)
        assert is_dangerous
        assert ".key" in reason
    
    def test_detects_priv_extension(self, temp_dir: Path) -> None:
        """Should detect .priv files."""
        test_file = temp_dir / "secret.priv"
        test_file.write_text("safe content")
        
        is_dangerous, reason = check_file_extension(test_file)
        assert is_dangerous
        assert ".priv" in reason
    
    def test_allows_safe_extensions(self, temp_dir: Path) -> None:
        """Should allow normal file extensions."""
        test_file = temp_dir / "config.py"
        test_file.write_text("safe content")
        
        is_dangerous, reason = check_file_extension(test_file)
        assert not is_dangerous


class TestFileContent:
    """Test secret pattern detection."""
    
    def test_detects_rsa_private_key(self, temp_dir: Path) -> None:
        """Should detect RSA private key headers."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA...")
        
        has_secret, reason = check_file_content(test_file)
        assert has_secret
        assert "rsa_private" in reason
    
    def test_detects_openssh_private_key(self, temp_dir: Path) -> None:
        """Should detect OpenSSH private key headers."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("-----BEGIN OPENSSH PRIVATE KEY-----\nkey_data...")
        
        has_secret, reason = check_file_content(test_file)
        assert has_secret
        assert "openssh" in reason
    
    def test_detects_generic_private_key(self, temp_dir: Path) -> None:
        """Should detect generic private key headers."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("-----BEGIN PRIVATE KEY-----\nkey_material...")
        
        has_secret, reason = check_file_content(test_file)
        assert has_secret
        assert "private" in reason.lower()
    
    def test_detects_pgp_private_key(self, temp_dir: Path) -> None:
        """Should detect PGP private key headers."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("-----BEGIN PGP PRIVATE KEY BLOCK-----\nVersion...")
        
        has_secret, reason = check_file_content(test_file)
        assert has_secret
        assert "pgp" in reason
    
    def test_allows_safe_content(self, temp_dir: Path) -> None:
        """Should allow files without secret content."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("This is just normal content without secrets")
        
        has_secret, reason = check_file_content(test_file)
        assert not has_secret


class TestValidateFiles:
    """Test the main validation function."""
    
    def test_passes_safe_files(self, temp_dir: Path) -> None:
        """Should pass validation for safe files."""
        safe_file1 = temp_dir / "file1.py"
        safe_file2 = temp_dir / "file2.txt"
        safe_file1.write_text("# safe python code")
        safe_file2.write_text("safe text content")
        
        is_valid, violations = validate_files([str(safe_file1), str(safe_file2)])
        assert is_valid
        assert len(violations) == 0
    
    def test_fails_on_dangerous_extension(self, temp_dir: Path) -> None:
        """Should fail validation for .key files."""
        key_file = temp_dir / "secret.key"
        key_file.write_text("safe content")
        
        is_valid, violations = validate_files([str(key_file)])
        assert not is_valid
        assert len(violations) == 1
        assert "secret.key" in violations[0]
    
    def test_fails_on_private_key_content(self, temp_dir: Path) -> None:
        """Should fail validation for files with private key content."""
        py_file = temp_dir / "config.py"
        py_file.write_text("-----BEGIN RSA PRIVATE KEY-----\nkey_material...")
        
        is_valid, violations = validate_files([str(py_file)])
        assert not is_valid
        assert len(violations) == 1
        assert "config.py" in violations[0]
    
    def test_handles_multiple_violations(self, temp_dir: Path) -> None:
        """Should report all violations."""
        key_file = temp_dir / "id.key"
        priv_file = temp_dir / "secret.priv"
        key_file.write_text("safe")
        priv_file.write_text("safe")
        
        is_valid, violations = validate_files([str(key_file), str(priv_file)])
        assert not is_valid
        assert len(violations) == 2
    
    def test_handles_empty_list(self) -> None:
        """Should handle empty file list."""
        is_valid, violations = validate_files([])
        assert is_valid
        assert len(violations) == 0


class TestIntegration:
    """Integration tests."""
    
    def test_complete_validation_workflow(self, temp_dir: Path) -> None:
        """Test complete validation workflow."""
        # Create safe and unsafe files
        safe_file = temp_dir / "main.py"
        key_file = temp_dir / "id.rsa"
        secret_file = temp_dir / "config.txt"
        
        safe_file.write_text("print('hello')")
        key_file.write_text("test content")  # .rsa should be .key, but let's use .pem
        secret_file.write_text("-----BEGIN PRIVATE KEY-----\ndata...")
        
        # Create properly named dangerous file
        dangerous_key = temp_dir / "key.pem"
        dangerous_key.write_text("test")
        
        is_valid, violations = validate_files([
            str(safe_file),
            str(dangerous_key),
            str(secret_file),
        ])
        
        assert not is_valid
        assert len(violations) == 2  # key.pem and config.txt (has private key content)
