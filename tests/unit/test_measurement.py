"""Tests for the universal BQRC measurement contract."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from bqrc.core.measurement import Measurement
from bqrc.core.provenance import DataSource
from bqrc.core.quality import QualityFlag
from bqrc.core.uncertainty import Uncertainty, UncertaintyType


def test_nominal_simulated_measurement() -> None:
    """A basic simulated measurement should preserve its scientific context."""
    measurement = Measurement(
        quantity="magnetic_field_magnitude",
        value=42.8e-6,
        unit="T",
        timestamp=datetime(2032, 7, 18, 10, 0, tzinfo=UTC),
        source=DataSource.SIMULATED_SENSOR,
        sensor_id="NV_MAG_01",
    )

    assert measurement.quantity == "magnetic_field_magnitude"
    assert measurement.value == 42.8e-6
    assert measurement.unit == "T"
    assert measurement.source == DataSource.SIMULATED_SENSOR
    assert measurement.quality == QualityFlag.NOMINAL
    assert measurement.sensor_id == "NV_MAG_01"


def test_measurement_can_include_uncertainty() -> None:
    """Measurements should carry uncertainty when available."""
    uncertainty = Uncertainty(
        value=0.035e-6,
        uncertainty_type=UncertaintyType.STANDARD_DEVIATION,
        method="Monte Carlo simulation",
    )

    measurement = Measurement(
        quantity="magnetic_field_magnitude",
        value=42.8e-6,
        unit="T",
        timestamp=datetime(2032, 7, 18, 10, 0, tzinfo=UTC),
        source=DataSource.SIMULATED_SENSOR,
        uncertainty=uncertainty,
    )

    assert measurement.uncertainty is not None
    assert measurement.uncertainty.value == 0.035e-6


def test_measurement_can_carry_multiple_quality_flags() -> None:
    """Measurements may simultaneously carry several quality conditions."""
    measurement = Measurement(
        quantity="magnetic_field_magnitude",
        value=42.8e-6,
        unit="T",
        timestamp=datetime(2032, 7, 18, 10, 0, tzinfo=UTC),
        source=DataSource.SIMULATED_SENSOR,
        quality=QualityFlag.DEGRADED | QualityFlag.EXTRAPOLATED,
    )

    assert measurement.quality & QualityFlag.DEGRADED
    assert measurement.quality & QualityFlag.EXTRAPOLATED


def test_measurement_rejects_naive_timestamp() -> None:
    """Measurements must use unambiguous timezone-aware timestamps."""
    with pytest.raises(ValidationError):
        Measurement(
            quantity="temperature",
            value=295.0,
            unit="K",
            timestamp=datetime(2032, 7, 18, 10, 0),
            source=DataSource.SIMULATION_TRUTH,
        )


def test_measurement_metadata_is_independent() -> None:
    """Each measurement should receive its own metadata dictionary."""
    first = Measurement(
        quantity="temperature",
        value=295.0,
        unit="K",
        timestamp=datetime(2032, 7, 18, 10, 0, tzinfo=UTC),
        source=DataSource.SIMULATED_SENSOR,
    )

    second = Measurement(
        quantity="temperature",
        value=296.0,
        unit="K",
        timestamp=datetime(2032, 7, 18, 10, 1, tzinfo=UTC),
        source=DataSource.SIMULATED_SENSOR,
    )

    first.metadata["location"] = "nv_module"

    assert "location" not in second.metadata