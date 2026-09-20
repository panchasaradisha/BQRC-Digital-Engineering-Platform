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
from bqrc.environment.magnetic.igrf.temporal import (
    predict_igrf14_coefficients,
)

IGRF14_DATASET = Path(
    "data/reference/geomagnetic/igrf14/raw/igrf14coeffs.txt"
)


@pytest.mark.parametrize(
    (
        "epoch",
        "latitude_deg",
        "longitude_deg",
        "altitude_m",
        "expected_north_nt",
        "expected_east_nt",
        "expected_down_nt",
        "expected_horizontal_nt",
        "expected_total_nt",
    ),
    [
        pytest.param(
            2025.0,
            0.0,
            0.0,
            0.0,
            27456.6,
            -1926.5,
            -15997.4,
            27524.1,
            31835.4,
            id="equator-greenwich-surface-2025",
        ),
        pytest.param(
            2025.0,
            45.0,
            0.0,
            0.0,
            23117.8,
            513.5,
            40936.1,
            23123.5,
            47015.6,
            id="northern-mid-latitude-surface-2025",
        ),
        pytest.param(
            2025.0,
            20.0,
            -75.0,
            0.0,
            26093.2,
            -4383.6,
            28242.3,
            26458.8,
            38700.1,
            id="western-longitude-surface-2025",
        ),
        pytest.param(
            2025.0,
            -35.0,
            140.0,
            0.0,
            23018.9,
            3540.4,
            -54359.2,
            23289.6,
            59138.2,
            id="southern-hemisphere-surface-2025",
        ),
        pytest.param(
            2027.5,
            23.0,
            72.5,
            400_000.0,
            30050.4,
            225.2,
            21375.6,
            30051.3,
            36878.1,
            id="ahmedabad-region-orbital-altitude-2027-5",
        ),
    ],
)
def test_igrf14_against_official_geomag_reference(
    epoch: float,
    latitude_deg: float,
    longitude_deg: float,
    altitude_m: float,
    expected_north_nt: float,
    expected_east_nt: float,
    expected_down_nt: float,
    expected_horizontal_nt: float,
    expected_total_nt: float,
) -> None:
    """Match independently verified Geomag 7.0 IGRF-14 results."""

    coefficients = load_igrf14_2025(
        IGRF14_DATASET
    )

    if epoch != 2025.0:
        coefficients = predict_igrf14_coefficients(
            base=coefficients,
            epoch=epoch,
        )

    geodetic_position = GeodeticPosition(
        latitude_deg=latitude_deg,
        longitude_deg=longitude_deg,
        altitude_m=altitude_m,
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
        expected_north_nt,
        abs=0.1,
    )

    assert field.east_nt == pytest.approx(
        expected_east_nt,
        abs=0.1,
    )

    assert field.down_nt == pytest.approx(
        expected_down_nt,
        abs=0.1,
    )

    assert field.horizontal_intensity_nt == pytest.approx(
        expected_horizontal_nt,
        abs=0.1,
    )

    assert field.total_intensity_nt == pytest.approx(
        expected_total_nt,
        abs=0.1,
    )