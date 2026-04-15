"""Custom exceptions for Terraform checking."""


class TerraformError(Exception):
    """Base exception for Terraform errors."""
    pass


class ConfigError(TerraformError):
    """Exception for configuration errors."""
    pass


class PolicyError(TerraformError):
    """Exception for policy-related errors."""
    pass
