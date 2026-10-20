
"""Tests for the NV magnetic-field estimation HTTP endpoint."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from bqrc.algorithms.odmr.field_estimator import estimate_nv_field_from_odmr
from bqrc.algorithms.odmr.shot_noise import simulate_photon_shot_noise
from bqrc.algorithms.odmr.spectrum import simulate_odmr_spectrum
from bqrc.api.main import app
from bqrc.sensors.nv.resonance import calculate_nv_resonance

client = TestClient(app)
ENDPOINT = "/api/v1/nv/odmr/estimate-field"


def make_measurement() -> tuple[dict[str, object], object]:
    """Create a reproducible simulated ODMR measurement."""
    frequencies = tuple(
        2867.0 + index * 0.05
        for index in range(121)
    )

    resonance = calculate_nv_resonance(
        magnetic_field_nt=(50_000.0, 0.0, 0.0),
        nv_axis=(1.0, 0.0, 0.0),
    )

    ideal = simulate_odmr_spectrum(
        resonance=resonance,
        frequencies_mhz=frequencies,
    )

    noisy = simulate_photon_shot_noise(
        spectrum=ideal,
        reference_photon_count=1_000_000.0,
        seed=42,
    )

    payload: dict[str, object] = {
        "frequencies_mhz": list(noisy.frequencies_mhz),
        "photon_counts": list(noisy.photon_counts),
        "reference_photon_count": noisy.reference_photon_count,
        "contrast": 0.1,
        "linewidth_mhz": 1.0,
    }

    return payload, noisy


def test_field_estimation_matches_scientific_model() -> None:
    """The API must agree with the existing field estimator."""
    payload, noisy = make_measurement()

    response = client.post(ENDPOINT, json=payload)

    expected = estimate_nv_field_from_odmr(
        measured=noisy,
    )

    assert response.status_code == 200
    result = response.json()

    assert result["lower_mhz"] == pytest.approx(expected.lower_mhz)
    assert result["upper_mhz"] == pytest.approx(expected.upper_mhz)
    assert result["projected_field_magnitude_nt"] == pytest.approx(
        expected.projected_field_magnitude_nt
    )
    assert result["residual_rmse"] == pytest.approx(expected.residual_rmse)
    assert result["fit_success"] == expected.fit_success


def test_estimated_field_is_close_to_true_field() -> None:
    """High-photon-count measurements should recover this test field."""
    payload, _ = make_measurement()

    response = client.post(ENDPOINT, json=payload)

    assert response.status_code == 200
    result = response.json()
    assert result["fit_success"] is True
    assert result["projected_field_magnitude_nt"] == pytest.approx(
        50_000.0,
        abs=500.0,
    )


@pytest.mark.parametrize(
    "overrides",
    [
        {"frequencies_mhz": [2869.0, 2870.0]},
        {"photon_counts": [100, 200]},
        {"photon_counts": [-1] * 121},
        {"reference_photon_count": 0.0},
        {"reference_photon_count": -1.0},
        {"contrast": 0.0},
        {"contrast": 0.8},
        {"linewidth_mhz": 0.0},
        {"zero_field_splitting_mhz": -1.0},
    ],
)
def test_invalid_field_estimation_inputs_return_422(
    overrides: dict[str, object],
) -> None:
    """Invalid measurements and model parameters must be rejected."""
    payload, _ = make_measurement()
    payload.update(overrides)

    response = client.post(ENDPOINT, json=payload)

    assert response.status_code == 422


def test_mismatched_arrays_return_422() -> None:
    """Frequency and photon-count arrays must have equal lengths."""
    payload, _ = make_measurement()
    payload["photon_counts"] = [100] * 10

    response = client.post(ENDPOINT, json=payload)

    assert response.status_code == 422


def test_frequency_grid_must_span_center() -> None:
    """The frequency grid must span zero-field splitting."""
    payload, _ = make_measurement()
    payload["frequencies_mhz"] = [
        2880.0 + index * 0.05
        for index in range(121)
    ]

    response = client.post(ENDPOINT, json=payload)

    assert response.status_code == 422


def test_estimation_endpoint_is_in_openapi_schema() -> None:
    """The estimation endpoint must appear in API documentation."""
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert ENDPOINT in response.json()["paths"]
