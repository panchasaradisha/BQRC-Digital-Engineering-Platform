
"""Tests for the NV resonance HTTP endpoint."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from bqrc.api.main import app
from bqrc.sensors.nv.resonance import calculate_nv_resonance

client = TestClient(app)

ENDPOINT = "/api/v1/nv/resonance"


def test_resonance_matches_scientific_model() -> None:
    """The HTTP endpoint must reuse the validated NV calculation."""
    payload = {
        "magnetic_field_nt": [50_000.0, 0.0, 0.0],
        "nv_axis": [1.0, 0.0, 0.0],
    }

    response = client.post(ENDPOINT, json=payload)

    expected = calculate_nv_resonance(
        magnetic_field_nt=(50_000.0, 0.0, 0.0),
        nv_axis=(1.0, 0.0, 0.0),
    )

    assert response.status_code == 200
    assert response.json() == pytest.approx(
        {
            "lower_mhz": expected.lower_mhz,
            "upper_mhz": expected.upper_mhz,
            "projected_field_nt": expected.projected_field_nt,
        }
    )


def test_negative_projection_preserves_sign() -> None:
    """Signed projection must remain available in the API response."""
    response = client.post(
        ENDPOINT,
        json={
            "magnetic_field_nt": [-50_000.0, 0.0, 0.0],
            "nv_axis": [1.0, 0.0, 0.0],
        },
    )

    assert response.status_code == 200
    assert response.json()["projected_field_nt"] == pytest.approx(
        -50_000.0
    )


@pytest.mark.parametrize(
    "payload",
    [
        {
            "magnetic_field_nt": [50_000.0, 0.0],
            "nv_axis": [1.0, 0.0, 0.0],
        },
        {
            "magnetic_field_nt": [50_000.0, 0.0, 0.0],
            "nv_axis": [0.0, 0.0, 0.0],
        },
        {
            "magnetic_field_nt": [50_000.0, 0.0, 0.0],
            "nv_axis": [1.0, 0.0, 0.0],
            "zero_field_splitting_mhz": -1.0,
        },
        {
            "magnetic_field_nt": ["invalid", 0.0, 0.0],
            "nv_axis": [1.0, 0.0, 0.0],
        },
    ],
)
def test_invalid_inputs_return_422(
    payload: dict[str, object],
) -> None:
    """Invalid input must be rejected without a server error."""
    response = client.post(ENDPOINT, json=payload)

    assert response.status_code == 422


def test_endpoint_is_in_openapi_schema() -> None:
    """The NV resonance endpoint must appear in API documentation."""
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert ENDPOINT in response.json()["paths"]
