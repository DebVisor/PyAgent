#!/usr/bin/env python3
"""TestAssertion shim for pytest collection."""

class TestAssertion:
    def __init__(self, name: str, passed: bool = True, details: str | None = None):
        self.name = name
        self.passed = passed
        self.details = details

    def __bool__(self):
        return bool(self.passed)


__all__ = ["TestAssertion"]
