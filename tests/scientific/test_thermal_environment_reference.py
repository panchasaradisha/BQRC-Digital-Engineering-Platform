"""Scientific regression tests for the BQRC thermal environment."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from bqrc.environment.thermal import (
    EARTH_MEAN_RADIUS_M,
    evaluate_thermal_environment,
)
from bqrc.environment.thermal.solar import (
    evaluate_solar_environment,
)
from bqrc.frames import ReferenceFrame, Vector3

TIMESTAMP = datetime(
    2027,
    7,
    18,
    10,
    0,
    tzinfo=UTC,
)

ALTITUDE_M = 400_000.0

ORBIT_RADIUS_M = (
    EARTH_MEAN_RADIUS_M + ALTITUDE_M
)


def scaled_position(
    direction: Vector3,
    scale_m: float,
) -> Vector3:
    """Create an ECI position along a supplied direction."""

    return Vector3(
        x=direction.x * scale_m,
        y=direction.y * scale_m,
        z=direction.z * scale_m,
        unit="m",
        frame=ReferenceFrame.ECI,
    )


def test_thermal_reference_illuminated_case() -> None:
    """Match the validated illuminated thermal reference case."""

    solar = evaluate_solar_environment(
        TIMESTAMP
    )

    spacecraft_position = scaled_position(
        solar.earth_to_sun_unit,
        ORBIT_RADIUS_M,
    )

    state = evaluate_thermal_environment(
        timestamp=TIMESTAMP,
        spacecraft_position=spacecraft_position,
        altitude_m=ALTITUDE_M,
    )

    assert state.eclipse.in_eclipse is False

    assert state.eclipse.sunlight_fraction == pytest.approx(
        1.0
    )

    assert state.solar.solar_irradiance_w_m2 == pytest.approx(
        1317.637,
        abs=0.01,
    )

    assert state.direct_solar_flux_w_m2 == pytest.approx(
        1317.637,
        abs=0.01,
    )

    assert state.earth_flux.infrared_flux_w_m2 == pytest.approx(
        209.825,
        abs=0.01,
    )

    assert state.earth_flux.albedo_flux_w_m2 == pytest.approx(
        349.966,
        abs=0.01,
    )


def test_thermal_reference_eclipse_case() -> None:
    """Match the validated eclipsed thermal reference case."""

    solar = evaluate_solar_environment(
        TIMESTAMP
    )

    spacecraft_position = scaled_position(
        solar.earth_to_sun_unit,
        -ORBIT_RADIUS_M,
    )

    state = evaluate_thermal_environment(
        timestamp=TIMESTAMP,
        spacecraft_position=spacecraft_position,
        altitude_m=ALTITUDE_M,
    )

    assert state.eclipse.in_eclipse is True

    assert state.eclipse.sunlight_fraction == pytest.approx(
        0.0
    )

    assert state.direct_solar_flux_w_m2 == pytest.approx(
        0.0,
        abs=1e-12,
    )

    assert state.earth_flux.albedo_flux_w_m2 == pytest.approx(
        0.0,
        abs=1e-12,
    )

    assert state.earth_flux.infrared_flux_w_m2 == pytest.approx(
        209.825,
        abs=0.01,
    )


def test_solar_reference_direction_is_unit_vector() -> None:
    """Validated solar direction should remain normalized."""

    solar = evaluate_solar_environment(
        TIMESTAMP
    )

    magnitude_squared = (
        solar.earth_to_sun_unit.x**2
        + solar.earth_to_sun_unit.y**2
        + solar.earth_to_sun_unit.z**2
    )

    assert magnitude_squared == pytest.approx(
        1.0,
        abs=1e-12,
    )


def test_thermal_reference_earth_view_factor() -> None:
    """Match the validated 400-km Earth view factor."""

    solar = evaluate_solar_environment(
        TIMESTAMP
    )

    spacecraft_position = scaled_position(
        solar.earth_to_sun_unit,
        ORBIT_RADIUS_M,
    )

    state = evaluate_thermal_environment(
        timestamp=TIMESTAMP,
        spacecraft_position=spacecraft_position,
        altitude_m=ALTITUDE_M,
    )

    assert state.earth_flux.earth_view_factor == pytest.approx(
        0.885338973,
        abs=1e-9,
    )