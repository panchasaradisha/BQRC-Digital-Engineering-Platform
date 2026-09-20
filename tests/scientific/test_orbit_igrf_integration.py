"""Scientific integration tests for orbit-coupled IGRF-14 evaluation."""

from __future__ import annotations

from datetime import UTC, datetime
from math import cos, radians, sin, sqrt
from pathlib import Path

import pytest

from bqrc.environment.earth import (
    EARTH_GRAVITATIONAL_PARAMETER_M3_S2,
    ecef_to_geodetic,
)
from bqrc.environment.magnetic.igrf.components import (
    spherical_to_geodetic_ned,
)
from bqrc.environment.magnetic.igrf.coordinates import (
    geodetic_to_igrf_spherical,
)
from bqrc.environment.magnetic.igrf.field import (
    evaluate_igrf_spherical,
)
from bqrc.environment.magnetic.igrf.parser import (
    load_igrf14_2025,
)
from bqrc.environment.magnetic.igrf.temporal import (
    predict_igrf14_coefficients,
)
from bqrc.environment.orbit import OrbitalState, propagate_rk4
from bqrc.frames import ReferenceFrame, Vector3, eci_to_ecef

IGRF14_DATASET = Path(
    "data/reference/geomagnetic/igrf14/raw/igrf14coeffs.txt"
)

ORBIT_RADIUS_M = 6_771_000.0
INCLINATION_DEG = 51.6


def decimal_year(timestamp: datetime) -> float:
    """Convert UTC datetime to decimal year."""

    start = datetime(
        timestamp.year,
        1,
        1,
        tzinfo=UTC,
    )

    end = datetime(
        timestamp.year + 1,
        1,
        1,
        tzinfo=UTC,
    )

    return timestamp.year + (
        (timestamp - start).total_seconds()
        / (end - start).total_seconds()
    )


def create_test_orbit() -> OrbitalState:
    """Create the controlled inclined orbit used by this test."""

    inclination = radians(INCLINATION_DEG)

    circular_speed = sqrt(
        EARTH_GRAVITATIONAL_PARAMETER_M3_S2
        / ORBIT_RADIUS_M
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
            x=ORBIT_RADIUS_M,
            y=0.0,
            z=0.0,
            unit="m",
            frame=ReferenceFrame.ECI,
        ),
        velocity=Vector3(
            x=0.0,
            y=circular_speed * cos(inclination),
            z=circular_speed * sin(inclination),
            unit="m/s",
            frame=ReferenceFrame.ECI,
        ),
    )


def magnetic_field_for_state(
    state: OrbitalState,
    base_coefficients,
):
    """Evaluate geodetic location and magnetic field for an orbit state."""

    ecef = eci_to_ecef(
        state.position,
        state.timestamp,
    )

    geodetic = ecef_to_geodetic(ecef)

    coefficients = predict_igrf14_coefficients(
        base=base_coefficients,
        epoch=decimal_year(state.timestamp),
    )

    spherical_position = geodetic_to_igrf_spherical(
        geodetic
    )

    spherical_field = evaluate_igrf_spherical(
        coefficients=coefficients,
        position=spherical_position,
    )

    magnetic_field = spherical_to_geodetic_ned(
        field=spherical_field,
        geodetic_position=geodetic,
        spherical_position=spherical_position,
    )

    return geodetic, magnetic_field


def test_orbit_to_igrf_pipeline() -> None:
    """Verify orbit propagation can drive the IGRF environment model."""

    base_coefficients = load_igrf14_2025(
        IGRF14_DATASET
    )

    state = create_test_orbit()

    geodetic_initial, field_initial = magnetic_field_for_state(
        state,
        base_coefficients,
    )

    for _ in range(30):
        state = propagate_rk4(
            state,
            10.0,
        )

    geodetic_later, field_later = magnetic_field_for_state(
        state,
        base_coefficients,
    )

    assert geodetic_initial.latitude_deg == pytest.approx(
        0.0,
        abs=1e-6,
    )

    assert geodetic_initial.altitude_m == pytest.approx(
        392_863.0,
        abs=5.0,
    )

    assert field_initial.total_intensity_nt == pytest.approx(
        24_031.4,
        abs=1.0,
    )

    assert geodetic_later.latitude_deg == pytest.approx(
        15.240,
        abs=0.01,
    )

    assert field_later.total_intensity_nt == pytest.approx(
        29_466.7,
        abs=2.0,
    )

    assert (
        field_later.total_intensity_nt
        != field_initial.total_intensity_nt
    )