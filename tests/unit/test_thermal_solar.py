"""Tests for the BQRC solar thermal-environment model."""

from datetime import UTC, datetime
from math import sqrt

import pytest

from bqrc.environment.thermal import (
    ASTRONOMICAL_UNIT_M,
    SolarEnvironment,
    evaluate_solar_environment,
    julian_date,
)
from bqrc.frames import ReferenceFrame


def test_j2000_julian_date() -> None:
    """J2000 epoch should map to its defining Julian Date."""

    timestamp = datetime(
        2000,
        1,
        1,
        12,
        0,
        0,
        tzinfo=UTC,
    )

    assert julian_date(timestamp) == pytest.approx(
        2_451_545.0,
        abs=1e-9,
    )


def test_julian_date_requires_timezone() -> None:
    """Solar calculations must reject naive timestamps."""

    timestamp = datetime(
        2027,
        7,
        18,
        10,
        0,
    )

    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        julian_date(timestamp)


def test_solar_direction_is_unit_vector() -> None:
    """Calculated Earth-to-Sun direction should have unit magnitude."""

    solar = evaluate_solar_environment(
        datetime(
            2027,
            7,
            18,
            10,
            0,
            tzinfo=UTC,
        )
    )

    direction = solar.earth_to_sun_unit

    magnitude = sqrt(
        direction.x**2
        + direction.y**2
        + direction.z**2
    )

    assert magnitude == pytest.approx(
        1.0,
        abs=1e-12,
    )

    assert direction.frame == ReferenceFrame.ECI
    assert direction.unit == "1"


def test_earth_sun_distance_is_physical() -> None:
    """Earth-Sun distance should remain near one astronomical unit."""

    solar = evaluate_solar_environment(
        datetime(
            2027,
            7,
            18,
            10,
            0,
            tzinfo=UTC,
        )
    )

    distance_au = (
        solar.earth_sun_distance_m
        / ASTRONOMICAL_UNIT_M
    )

    assert 0.98 < distance_au < 1.02


def test_solar_irradiance_is_physical() -> None:
    """Solar irradiance near Earth should remain physically plausible."""

    solar = evaluate_solar_environment(
        datetime(
            2027,
            7,
            18,
            10,
            0,
            tzinfo=UTC,
        )
    )

    assert 1300.0 < solar.solar_irradiance_w_m2 < 1450.0


def test_solar_environment_rejects_wrong_direction_frame() -> None:
    """Solar environment should require an ECI Sun direction."""

    valid = evaluate_solar_environment(
        datetime(
            2027,
            7,
            18,
            10,
            0,
            tzinfo=UTC,
        )
    )

    from bqrc.frames import Vector3

    with pytest.raises(
        ValueError,
        match="ECI",
    ):
        SolarEnvironment(
            timestamp=valid.timestamp,
            earth_to_sun_unit=Vector3(
                x=1.0,
                y=0.0,
                z=0.0,
                unit="1",
                frame=ReferenceFrame.ECEF,
            ),
            earth_sun_distance_m=valid.earth_sun_distance_m,
            solar_irradiance_w_m2=valid.solar_irradiance_w_m2,
        )