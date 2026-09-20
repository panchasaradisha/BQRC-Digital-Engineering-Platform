"""Tests for BQRC measurement quality flags."""

from bqrc.core.quality import QualityFlag


def test_nominal_has_no_active_warning_bits() -> None:
    """Nominal quality should represent no active warning condition."""
    assert QualityFlag.NOMINAL == 0


def test_quality_flags_can_be_combined() -> None:
    """Multiple measurement conditions should coexist."""
    quality = QualityFlag.DEGRADED | QualityFlag.EXTRAPOLATED

    assert quality & QualityFlag.DEGRADED
    assert quality & QualityFlag.EXTRAPOLATED


def test_unset_quality_flag_is_not_reported() -> None:
    """A condition not present in the flag set should remain inactive."""
    quality = QualityFlag.DEGRADED | QualityFlag.EXTRAPOLATED

    assert not quality & QualityFlag.SATURATED


def test_fault_and_saturation_can_coexist() -> None:
    """Fault-injected measurements may simultaneously be saturated."""
    quality = QualityFlag.FAULT_INJECTED | QualityFlag.SATURATED

    assert quality & QualityFlag.FAULT_INJECTED
    assert quality & QualityFlag.SATURATED