"""Unit tests for the official IGRF-14 coefficient parser."""

from pathlib import Path

import pytest

from bqrc.environment.magnetic.igrf.coefficients import (
    CoefficientKind,
)
from bqrc.environment.magnetic.igrf.parser import (
    IGRFParseError,
    load_igrf14_2025,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

IGRF14_DATASET = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "geomagnetic"
    / "igrf14"
    / "raw"
    / "igrf14coeffs.txt"
)


def test_official_igrf14_dataset_exists() -> None:
    """The authoritative raw coefficient dataset must be available."""

    assert IGRF14_DATASET.is_file()


def test_load_igrf14_2025_identity() -> None:
    """The parser should identify the requested model and epoch."""

    coefficient_set = load_igrf14_2025(
        IGRF14_DATASET
    )

    assert coefficient_set.model == "IGRF-14"
    assert coefficient_set.epoch == 2025.0
    assert coefficient_set.maximum_degree == 13


def test_known_2025_dipole_coefficients() -> None:
    """Known first-degree 2025 coefficients should parse correctly."""

    coefficient_set = load_igrf14_2025(
        IGRF14_DATASET
    )

    g10 = coefficient_set.get(
        CoefficientKind.G,
        1,
        0,
    )

    g11 = coefficient_set.get(
        CoefficientKind.G,
        1,
        1,
    )

    h11 = coefficient_set.get(
        CoefficientKind.H,
        1,
        1,
    )

    assert g10.value_nt == pytest.approx(-29350.0)
    assert g11.value_nt == pytest.approx(-1410.3)
    assert h11.value_nt == pytest.approx(4545.5)


def test_known_2025_secular_variation() -> None:
    """Known predictive secular variation should parse correctly."""

    coefficient_set = load_igrf14_2025(
        IGRF14_DATASET
    )

    g10 = coefficient_set.get(
        CoefficientKind.G,
        1,
        0,
    )

    assert g10.secular_variation_nt_per_year == pytest.approx(
        12.6
    )


def test_degree_13_main_field_is_available() -> None:
    """IGRF-14 2025 main-field coefficients should reach degree 13."""

    coefficient_set = load_igrf14_2025(
        IGRF14_DATASET
    )

    degree_13 = [
        coefficient
        for coefficient in coefficient_set.coefficients
        if coefficient.degree == 13
    ]

    assert degree_13


def test_predictive_secular_variation_stops_after_degree_8() -> None:
    """Predictive secular variation should exist only through degree 8."""

    coefficient_set = load_igrf14_2025(
        IGRF14_DATASET
    )

    degree_8 = [
        coefficient
        for coefficient in coefficient_set.coefficients
        if coefficient.degree == 8
    ]

    higher_degrees = [
        coefficient
        for coefficient in coefficient_set.coefficients
        if coefficient.degree > 8
    ]

    assert degree_8
    assert higher_degrees

    assert all(
        coefficient.secular_variation_nt_per_year is not None
        for coefficient in degree_8
    )

    assert all(
        coefficient.secular_variation_nt_per_year is None
        for coefficient in higher_degrees
    )


def test_missing_dataset_raises_file_not_found(
    tmp_path: Path,
) -> None:
    """A missing authoritative dataset should fail explicitly."""

    missing = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError):
        load_igrf14_2025(missing)


def test_missing_header_is_rejected(
    tmp_path: Path,
) -> None:
    """Malformed coefficient files must not be silently accepted."""

    malformed = tmp_path / "malformed.txt"

    malformed.write_text(
        "g 1 0 -29350.0 12.6\n",
        encoding="utf-8",
    )

    with pytest.raises(
        IGRFParseError,
        match="header",
    ):
        load_igrf14_2025(malformed)