"""Tests for BQRC scientific provenance."""

from bqrc.core.provenance import DataSource


def test_simulation_truth_value() -> None:
    """Simulation truth should use the expected serialized value."""
    assert DataSource.SIMULATION_TRUTH == "simulation_truth"


def test_real_hardware_value() -> None:
    """Real hardware should remain distinguishable from simulated data."""
    assert DataSource.REAL_HARDWARE == "real_hardware"


def test_user_override_value() -> None:
    """Manual user inputs should remain explicitly identifiable."""
    assert DataSource.USER_OVERRIDE == "user_override"