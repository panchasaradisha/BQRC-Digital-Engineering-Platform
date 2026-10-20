
"""NOAA IGRF2025 angular reference regression tests.

Reference values were recorded from the NOAA/NCEI Magnetic
Field Calculator at 0 km GPS elevation on 2025-01-01.

NOAA displays declination and inclination to 0.0001 degree.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from bqrc.environment.earth.geodetic import GeodeticPosition
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

IGRF14_DATASET = Path(
    "data/reference/geomagnetic/igrf14/raw/igrf14coeffs.txt"
)

# Tolerance accounts for NOAA's displayed rounding.
ANGLE_TOLERANCE_DEG = 0.00005


@pytest.mark.parametrize(
    (
        "latitude_deg",
        "longitude_deg",
        "expected_declination_deg",
        "expected_inclination_deg",
    ),
    [
        pytest.param(
            0.0,
            0.0,
            -4.0137,
            -30.1657,
            id="greenwich",
        ),
        pytest.param(
            45.0,
            0.0,
            1.2724,
            60.5393,
            id="northern-mid-latitude",
        ),
        pytest.param(
            20.0,
            -75.0,
            -9.5365,
            46.8674,
            id="western-longitude",
        ),
        pytest.param(
            -35.0,
            140.0,
            8.7438,
            -66.8079,
            id="southern-hemisphere",
        ),
    ],
)
def test_igrf14_angles_against_noaa(
    latitude_deg: float,
    longitude_deg: float,
    expected_declination_deg: float,
    expected_inclination_deg: float,
) -> None:
    """Compare BQRC angles with displayed NOAA reference values."""

    coefficients = load_igrf14_2025(IGRF14_DATASET)

    geodetic = GeodeticPosition(
        latitude_deg=latitude_deg,
        longitude_deg=longitude_deg,
        altitude_m=0.0,
    )

    spherical_position = geodetic_to_igrf_spherical(
        geodetic
    )

    spherical_field = evaluate_igrf_spherical(
        coefficients=coefficients,
        position=spherical_position,
    )

    field = spherical_to_geodetic_ned(
        field=spherical_field,
        geodetic_position=geodetic,
        spherical_position=spherical_position,
    )

    assert field.declination_deg == pytest.approx(
        expected_declination_deg,
        abs=ANGLE_TOLERANCE_DEG,
        rel=0,
    )

    assert field.inclination_deg == pytest.approx(
        expected_inclination_deg,
        abs=ANGLE_TOLERANCE_DEG,
        rel=0,
    )
