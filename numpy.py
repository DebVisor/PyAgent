#!/usr/bin/env python3
"""Lightweight numpy shim for test environments without numpy installed.
This provides minimal helpers used by the test-collection path (dot, linalg.norm, asarray).
Not a replacement for real numpy; intended only to let static imports succeed in CI/test sandbox.
"""
from __future__ import annotations

import math
from typing import Iterable, Sequence, List, Any


def asarray(x: Iterable) -> list:
    return list(x)


def array(x: Iterable) -> list:
    return asarray(x)


def dot(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(float(x) * float(y) for x, y in zip(a, b))


class linalg:
    @staticmethod
    def norm(a: Sequence[float]) -> float:
        return math.sqrt(sum(float(x) * float(x) for x in a))


__all__ = ["asarray", "array", "dot", "linalg"]

# Minimal aliases to satisfy simple type checks and annotations that expect numpy.ndarray
ndarray = list
# ensure both names are present
array = asarray
asarray = asarray

__version__ = "0.0"
# Minimal dtype aliases used in type annotations
float32 = float
float64 = float
int32 = int
int64 = int
float16 = float
int8 = int
int16 = int
uint8 = int
uint16 = int
uint32 = int
uint64 = int
# Minimal dtype factory placeholder
def dtype(t: Any) -> Any:
    return t
