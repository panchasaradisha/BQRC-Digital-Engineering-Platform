"""Scientific regression tests for BQRC Earth geometry and reference frames."""

from datetime import UTC, datetime
from math import cos, pi, radians, sin, sqrt

from bqrc.environment.earth import (
    EARTH_GRAVITATIONAL_PARAMETER_M3_S2,
    WGS84_SEMI_MAJOR_AXIS_M,
    GeodeticPosition,
    ecef_to_geodetic,
    geodetic_to_ecef,
)
from bqrc.environment.orbit import OrbitalState, propagate_rk4
from bqrc.frames import ReferenceFrame, Vector3, eci_to_ecef

TEST_RADIUS_M = 6_771_000.0
TEST_INCLINATION_DEG = 51.6
TEST_STEP_SECONDS = 10.0


def _create_inclined_orbit() -> tuple[OrbitalState, float]:
    """Create the verified inclined circular-orbit scenario."""

    circular_speed = sqrt(
        EARTH_GRAVITATIONAL_PARAMETER_M3_S2 / TEST_RADIUS_M
    )

    inclination_rad = radians(TEST_INCLINATION_DEG)

    theoretical_period = 2.0 * pi * sqrt(
        TEST_RADIUS_M**3
        / EARTH_GRAVITATIONAL_PARAMETER_M3_S2
    )

    state = OrbitalState(
        timestamp=datetime(
            2032,
            7,
            18,
            10,
            0,
            tzinfo=UTC,
        ),
        position=Vector3(
            x=TEST_RADIUS_M,
            y=0.0,
            z=0.0,
            unit="m",
            frame=ReferenceFrame.ECI,
        ),
        velocity=Vector3(
            x=0.0,
            y=circular_speed * cos(inclination_rad),
            z=circular_speed * sin(inclination_rad),
            unit="m/s",
            frame=ReferenceFrame.ECI,
        ),
    )

    return state, theoretical_period


def _to_geodetic(state: OrbitalState) -> GeodeticPosition:
    """Convert an orbital ECI position to WGS-84 geodetic coordinates."""

    ecef_position = eci_to_ecef(
        state.position,
        state.timestamp,
    )

    return ecef_to_geodetic(ecef_position)


def test_geodetic_ecef_round_trip_remains_precise() -> None:
    """A representative orbital location should survive a round trip."""

    original = GeodeticPosition(
        latitude_deg=37.25,
        longitude_deg=-122.10,
        altitude_m=400_000.0,
    )

    ecef = geodetic_to_ecef(original)
    recovered = ecef_to_geodetic(ecef)

    assert abs(
        recovered.latitude_deg - original.latitude_deg
    ) < 1e-9

    assert abs(
        recovered.longitude_deg - original.longitude_deg
    ) < 1e-9

    assert abs(
        recovered.altitude_m - original.altitude_m
    ) < 1e-4


def test_equatorial_orbit_altitude_matches_wgs84_geometry() -> None:
    """The common test radius should produce the expected equatorial altitude."""

    position = Vector3(
        x=TEST_RADIUS_M,
        y=0.0,
        z=0.0,
        unit="m",
        frame=ReferenceFrame.ECEF,
    )

    geodetic = ecef_to_geodetic(position)

    expected_altitude = (
        TEST_RADIUS_M - WGS84_SEMI_MAJOR_AXIS_M
    )

    assert abs(
        geodetic.altitude_m - expected_altitude
    ) < 1e-6


def test_inclined_orbit_geodetic_latitude_range() -> None:
    """Inclined-orbit geodetic latitude should remain near verified bounds."""

    state, theoretical_period = _create_inclined_orbit()

    elapsed_seconds = 0.0

    maximum_latitude = -90.0
    minimum_latitude = 90.0

    while elapsed_seconds < theoretical_period:
        geodetic = _to_geodetic(state)

        maximum_latitude = max(
            maximum_latitude,
            geodetic.latitude_deg,
        )

        minimum_latitude = min(
            minimum_latitude,
            geodetic.latitude_deg,
        )

        remaining_seconds = (
            theoretical_period - elapsed_seconds
        )

        step = min(
            TEST_STEP_SECONDS,
            remaining_seconds,
        )

        state = propagate_rk4(state, step)
        elapsed_seconds += step

    final_geodetic = _to_geodetic(state)

    maximum_latitude = max(
        maximum_latitude,
        final_geodetic.latitude_deg,
    )

    minimum_latitude = min(
        minimum_latitude,
        final_geodetic.latitude_deg,
    )

    assert 51.7 < maximum_latitude < 51.9
    assert -51.9 < minimum_latitude < -51.7


def test_inclined_orbit_latitude_is_approximately_symmetric() -> None:
    """North and south geodetic latitude extrema should be nearly symmetric."""

    state, theoretical_period = _create_inclined_orbit()

    elapsed_seconds = 0.0

    maximum_latitude = -90.0
    minimum_latitude = 90.0

    while elapsed_seconds < theoretical_period:
        geodetic = _to_geodetic(state)

        maximum_latitude = max(
            maximum_latitude,
            geodetic.latitude_deg,
        )

        minimum_latitude = min(
            minimum_latitude,
            geodetic.latitude_deg,
        )

        remaining_seconds = (
            theoretical_period - elapsed_seconds
        )

        step = min(
            TEST_STEP_SECONDS,
            remaining_seconds,
        )

        state = propagate_rk4(state, step)
        elapsed_seconds += step

    assert abs(
        maximum_latitude + minimum_latitude
    ) < 0.01