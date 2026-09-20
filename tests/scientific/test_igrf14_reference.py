"""Scientific regression tests for the BQRC IGRF-14 implementation."""

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


def test_igrf14_2025_equator_greenwich_official_reference() -> None:
    """Match the independently verified Geomag IGRF-14 reference point."""

    coefficients = load_igrf14_2025(
        IGRF14_DATASET
    )

    geodetic_position = GeodeticPosition(
        latitude_deg=0.0,
        longitude_deg=0.0,
        altitude_m=0.0,
    )

    spherical_position = geodetic_to_igrf_spherical(
        geodetic_position
    )

    spherical_field = evaluate_igrf_spherical(
        coefficients=coefficients,
        position=spherical_position,
    )

    field = spherical_to_geodetic_ned(
        field=spherical_field,
        geodetic_position=geodetic_position,
        spherical_position=spherical_position,
    )

    assert field.north_nt == pytest.approx(
        27456.6,
        abs=0.1,
    )

    assert field.east_nt == pytest.approx(
        -1926.5,
        abs=0.1,
    )

    assert field.down_nt == pytest.approx(
        -15997.4,
        abs=0.1,
    )

    assert field.horizontal_intensity_nt == pytest.approx(
        27524.1,
        abs=0.1,
    )

    assert field.total_intensity_nt == pytest.approx(
        31835.4,
        abs=0.1,
    )