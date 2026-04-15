"""Custom exceptions for K8s validation."""


class K8sError(Exception):
    """Base exception for K8s validation errors."""
    pass


class ManifestError(K8sError):
    """Exception for manifest-related errors."""
    pass


class ClusterError(K8sError):
    """Exception for cluster-related errors."""
    pass
