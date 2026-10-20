
"""Tests for the NV field-uncertainty HTTP endpoint."""

from __future__ import annotations

from math import sqrt

import pytest
from fastapi.testclient import TestClient

from bqrc.algorithms.odmr.field_uncertainty import (
    analyze_nv_field_uncertainty,
)
from bqrc.api.main import app

client = TestClient(app)
ENDPOINT = "/api/v1/nv/odmr/field-uncertainty"


def make_payload() -> dict[str, object]:
    """Create a well-resolved ODMR frequency grid."""
    return {
        "frequencies_mhz": [
            2865.0 + index * 0.025
            for index in range(401)
        ],
        "projected_field_magnitude_nt": 50_000.0,
        "reference_photon_count": 1_000_000.0,
        "contrast": 0.1,
        "linewidth_mhz": 1.0,
        "zero_field_splitting_mhz": 2870.0,
    }


def test_uncertainty_matches_scientific_model() -> None:
    """The HTTP endpoint must agree with the scientific algorithm."""
    payload = make_payload()

    response = client.post(ENDPOINT, json=payload)

    assert response.status_code == 200
    result = response.json()

    expected = analyze_nv_field_uncertainty(
        frequencies_mhz=tuple(payload["frequencies_mhz"]),
        projected_field_magnitude_nt=50_000.0,
        reference_photon_count=1_000_000.0,
    )

    assert result["fisher_information_per_nt_squared"] == pytest.approx(
        expected.fisher_information_per_nt_squared
    )
    assert result["crlb_std_nt"] == pytest.approx(expected.crlb_std_nt)
    assert result["identifiable_locally"] is True


def test_crlb_is_inverse_square_root_of_information() -> None:
    """The CRLB must follow the Fisher information relationship."""
    response = client.post(ENDPOINT, json=make_payload())

    assert response.status_code == 200
    result = response.json()

    assert result["crlb_std_nt"] == pytest.approx(
        1.0 / sqrt(result["fisher_information_per_nt_squared"])
    )


def test_zero_field_returns_null_crlb() -> None:
    """A zero field has no first-order magnitude information."""
    payload = make_payload()
    payload["projected_field_magnitude_nt"] = 0.0

    response = client.post(ENDPOINT, json=payload)

    assert response.status_code == 200
    result = response.json()
    assert result["identifiable_locally"] is False
    assert result["fisher_information_per_nt_squared"] == 0.0
    assert result["crlb_std_nt"] is None


def test_zero_contrast_returns_null_crlb() -> None:
    """Zero contrast makes the field locally unidentifiable."""
    payload = make_payload()
    payload["contrast"] = 0.0

    response = client.post(ENDPOINT, json=payload)

    assert response.status_code == 200
    result = response.json()
    assert result["identifiable_locally"] is False
    assert result["crlb_std_nt"] is None


def test_more_photons_reduce_uncertainty() -> None:
    """A hundredfold photon increase reduces CRLB by tenfold."""
    low_payload = make_payload()
    high_payload = make_payload()

    low_payload["reference_photon_count"] = 10_000.0
    high_payload["reference_photon_count"] = 1_000_000.0

    low = client.post(ENDPOINT, json=low_payload)
    high = client.post(ENDPOINT, json=high_payload)

    assert low.status_code == 200
    assert high.status_code == 200

    assert low.json()["crlb_std_nt"] / high.json()["crlb_std_nt"] == (
        pytest.approx(10.0)
    )


@pytest.mark.parametrize(
    "overrides",
    [
        {"frequencies_mhz": []},
        {"projected_field_magnitude_nt": -1.0},
        {"reference_photon_count": 0.0},
        {"reference_photon_count": -1.0},
        {"reference_photon_count": 1e13},
        {"contrast": -0.1},
        {"contrast": 0.6},
        {"linewidth_mhz": 0.0},
        {"zero_field_splitting_mhz": -1.0},
    ],
)
def test_invalid_inputs_return_422(
    overrides: dict[str, object],
) -> None:
    """Invalid inputs must produce validation errors."""
    payload = make_payload()
    payload.update(overrides)

    response = client.post(ENDPOINT, json=payload)

    assert response.status_code == 422


def test_endpoint_is_registered_in_openapi() -> None:
    """The endpoint must appear in the generated API documentation."""
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert ENDPOINT in response.json()["paths"]
