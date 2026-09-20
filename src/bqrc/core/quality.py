"""Measurement quality and status flags for the BQRC platform."""

from enum import IntFlag, auto


class QualityFlag(IntFlag):
    """Quality conditions associated with a BQRC measurement."""

    NOMINAL = 0

    DEGRADED = auto()
    INVALID = auto()
    SATURATED = auto()
    OUT_OF_RANGE = auto()
    EXTRAPOLATED = auto()
    UNCALIBRATED = auto()
    FAULT_INJECTED = auto()
    MISSING = auto()