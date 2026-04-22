"""Shared utility functions for ticker data containers."""

from __future__ import annotations

from typing import Any


def parse_float(value: Any) -> float | None:
    """Parse value to float, returning None on failure."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def parse_int(value: Any) -> int | None:
    """Parse value to int, returning None on failure."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None
