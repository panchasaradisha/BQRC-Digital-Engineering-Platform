
"""Tests for the ODMR spectrum HTTP endpoint."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from bqrc.algorithms.odmr.spectrum import simulate_odmr_spectrum
from bqrc.api.main import app
from bqrc.sensors.nv.resonance import calculate_nv_resonance

client = TestClient(app)

ENDPOINT = "/api/v1/nv/odmr/spectrum"


def test_odmr_spectrum_matches_scientific_model() -> None:
    """API fluorescence must match the existing scientific simulator."""
    frequencies = [2868.0, 2869.0, 2870.0, 2871.0, 2872.0]

    response = client.post(
        ENDPOINT,
        json={
            "magnetic_field_nt": [50_000.0, 0.0, 0.0],
            "nv_axis": [1.0, 0.0, 0.0],
            "frequencies_mhz": frequencies,
            "contrast": 0.1,
            "linewidth_mhz": 1.0,
        },
    )

    resonance = calculate_nv_resonance(
        magnetic_field_nt=(50_000.0, 0.0, 0.0),
        nv_axis=(1.0, 0.0, 0.0),
    )
    expected = simulate_odmr_spectrum(
        resonance=resonance,
        frequencies_mhz=tuple(frequencies),
        contrast=0.1,
        linewidth_mhz=1.0,
    )

    assert response.status_code == 200

    result = response.json()
    assert result["frequencies_mhz"] == frequencies
    assert result["fluorescence"] == pytest.approx(expected.fluorescence)
    assert result["lower_mhz"] == pytest.approx(resonance.lower_mhz)
    assert result["upper_mhz"] == pytest.approx(resonance.upper_mhz)
    assert result["projected_field_nt"] == pytest.approx(
        resonance.projected_field_nt
    )


def test_odmr_spectrum_uses_defaults() -> None:
    """Optional contrast and linewidth values should have defaults."""
    response = client.post(
        ENDPOINT,
        json={
            "magnetic_field_nt": [50_000.0, 0.0, 0.0],
            "nv_axis": [1.0, 0.0, 0.0],
            "frequencies_mhz": [2869.0, 2870.0, 2871.0],
        },
    )

    assert response.status_code == 200
    assert len(response.json()["fluorescence"]) == 3


@pytest.mark.parametrize(
    "overrides",
    [
        {"frequencies_mhz": []},
        {"frequencies_mhz": [2869.0, "invalid"]},
        {"contrast": -0.1},
        {"contrast": 0.6},
        {"linewidth_mhz": 0.0},
        {"linewidth_mhz": -1.0},
        {"nv_axis": [0.0, 0.0, 0.0]},
    ],
)
def test_invalid_odmr_inputs_return_422(
    overrides: dict[str, object],
) -> None:
    """Invalid simulation inputs must be rejected."""
    payload: dict[str, object] = {
        "magnetic_field_nt": [50_000.0, 0.0, 0.0],
        "nv_axis": [1.0, 0.0, 0.0],
        "frequencies_mhz": [2869.0, 2870.0, 2871.0],
    }
    payload.update(overrides)

    response = client.post(ENDPOINT, json=payload)

    assert response.status_code == 422


def test_odmr_spectrum_is_in_openapi_schema() -> None:
    """The spectrum endpoint must appear in API documentation."""
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert ENDPOINT in response.json()["paths"]
