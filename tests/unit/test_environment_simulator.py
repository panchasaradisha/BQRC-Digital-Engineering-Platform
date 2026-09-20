"""Tests for the unified BQRC space-environment simulator."""

from __future__ import annotations

from datetime import UTC, datetime
from math import cos, radians, sin, sqrt
from pathlib import Path

import pytest

from bqrc.environment import (
    SpaceEnvironmentSimulator,
    datetime_to_decimal_year,
)
from bqrc.environment.earth import (
    EARTH_GRAVITATIONAL_PARAMETER_M3_S2,
)
from bqrc.environment.orbit import OrbitalState
from bqrc.frames import ReferenceFrame, Vector3

IGRF14_DATASET = Path(
    "data/reference/geomagnetic/igrf14/raw/igrf14coeffs.txt"
)


def create_orbital_state() -> OrbitalState:
    """Create a controlled inclined-orbit state."""

    radius_m = 6_771_000.0
    inclination = radians(51.6)

    speed = sqrt(
        EARTH_GRAVITATIONAL_PARAMETER_M3_S2
        / radius_m
    )

    return OrbitalState(
        timestamp=datetime(
            2027,
            7,
            18,
            10,
            0,
            tzinfo=UTC,
        ),
        position=Vector3(
            x=radius_m,
            y=0.0,
            z=0.0,
            unit="m",
            frame=ReferenceFrame.ECI,
        ),
        velocity=Vector3(
            x=0.0,
            y=speed * cos(inclination),
            z=speed * sin(inclination),
            unit="m/s",
            frame=ReferenceFrame.ECI,
        ),
    )


def test_decimal_year_conversion() -> None:
    """Decimal-year conversion should preserve the calendar epoch."""

    timestamp = datetime(
        2027,
        1,
        1,
        tzinfo=UTC,
    )

    assert datetime_to_decimal_year(
        timestamp
    ) == pytest.approx(2027.0)


def test_decimal_year_requires_timezone() -> None:
    """Naive timestamps must not enter the environment simulator."""

    timestamp = datetime(
        2027,
        1,
        1,
    )

    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        datetime_to_decimal_year(timestamp)


def test_environment_simulator_evaluates_orbit_state() -> None:
    """Unified simulator should evaluate location and magnetic field."""

    simulator = SpaceEnvironmentSimulator.from_igrf14_dataset(
        IGRF14_DATASET
    )

    state = simulator.evaluate(
        create_orbital_state()
    )

    assert state.timestamp == datetime(
        2027,
        7,
        18,
        10,
        0,
        tzinfo=UTC,
    )

    assert state.geodetic_position.latitude_deg == pytest.approx(
        0.0,
        abs=1e-6,
    )

    assert state.geodetic_position.altitude_m == pytest.approx(
        392_863.0,
        abs=5.0,
    )

    assert state.magnetic_field.total_intensity_nt == pytest.approx(
        24_031.4,
        abs=1.0,
    )

    assert 2027.0 < state.igrf_epoch < 2028.0


def test_environment_simulator_includes_microgravity_state() -> None:
    """Unified environment state should include microgravity truth."""

    simulator = SpaceEnvironmentSimulator.from_igrf14_dataset(
        IGRF14_DATASET
    )

    state = simulator.evaluate(
        create_orbital_state()
    )

    assert state.microgravity.magnitude_m_s2 == pytest.approx(
        0.0,
        abs=1e-15,
    )

    assert state.microgravity.magnitude_micro_g == pytest.approx(
        0.0,
        abs=1e-12,
    )

    assert state.microgravity.residual_acceleration.frame == (
        ReferenceFrame.ECI
    )

    assert (
        state.microgravity.residual_acceleration.unit
        == "m/s^2"
    )
def test_environment_simulator_includes_thermal_state() -> None:
    """Unified environment state should include thermal truth."""

    simulator = SpaceEnvironmentSimulator.from_igrf14_dataset(
        IGRF14_DATASET
    )

    state = simulator.evaluate(
        create_orbital_state()
    )

    assert state.thermal.solar.solar_irradiance_w_m2 > 0.0

    assert (
        0.0
        <= state.thermal.eclipse.sunlight_fraction
        <= 1.0
    )

    assert state.thermal.earth_flux.infrared_flux_w_m2 > 0.0

    assert state.thermal.earth_flux.albedo_flux_w_m2 >= 0.0

    assert state.thermal.direct_solar_flux_w_m2 >= 0.0

    assert (
        state.thermal.solar.earth_to_sun_unit.frame
        == ReferenceFrame.ECI
    )