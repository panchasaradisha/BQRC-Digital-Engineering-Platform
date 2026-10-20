
"""Tests for the noisy ODMR spectrum HTTP endpoint."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from bqrc.algorithms.odmr.shot_noise import simulate_photon_shot_noise
from bqrc.algorithms.odmr.spectrum import simulate_odmr_spectrum
from bqrc.api.main import app
from bqrc.sensors.nv.resonance import calculate_nv_resonance

client = TestClient(app)
ENDPOINT = "/api/v1/nv/odmr/noisy-spectrum"


def make_payload() -> dict[str, object]:
    """Construct a valid photon shot-noise request."""
    return {
        "magnetic_field_nt": [50_000.0, 0.0, 0.0],
        "nv_axis": [1.0, 0.0, 0.0],
        "frequencies_mhz": [2868.0, 2869.0, 2870.0, 2871.0, 2872.0],
        "contrast": 0.1,
        "linewidth_mhz": 1.0,
        "reference_photon_count": 100_000.0,
        "seed": 42,
    }


def test_noisy_spectrum_matches_scientific_model() -> None:
    """The API must reproduce the existing Poisson noise simulator."""
    payload = make_payload()
    response = client.post(ENDPOINT, json=payload)

    resonance = calculate_nv_resonance(
        magnetic_field_nt=(50_000.0, 0.0, 0.0),
        nv_axis=(1.0, 0.0, 0.0),
    )
    ideal = simulate_odmr_spectrum(
        resonance=resonance,
        frequencies_mhz=(2868.0, 2869.0, 2870.0, 2871.0, 2872.0),
    )
    noisy = simulate_photon_shot_noise(
        spectrum=ideal,
        reference_photon_count=100_000.0,
        seed=42,
    )

    assert response.status_code == 200
    result = response.json()
    assert result["photon_counts"] == list(noisy.photon_counts)
    assert result["ideal_fluorescence"] == pytest.approx(
        ideal.fluorescence
    )
    assert result["measured_fluorescence"] == pytest.approx(
        noisy.fluorescence
    )
    assert result["reference_photon_count"] == 100_000.0


def test_same_seed_produces_same_measurements() -> None:
    """Identical seeded requests must return identical photon counts."""
    payload = make_payload()

    first = client.post(ENDPOINT, json=payload)
    second = client.post(ENDPOINT, json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["photon_counts"] == second.json()["photon_counts"]


def test_different_seeds_produce_different_measurements() -> None:
    """Different seeds should produce different samples in this test."""
    first_payload = make_payload()
    second_payload = make_payload()
    second_payload["seed"] = 43

    first = client.post(ENDPOINT, json=first_payload)
    second = client.post(ENDPOINT, json=second_payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["photon_counts"] != second.json()["photon_counts"]


def test_noisy_spectrum_uses_defaults() -> None:
    """Default photon budget and seed should be accepted."""
    payload = make_payload()
    payload.pop("reference_photon_count")
    payload.pop("seed")

    response = client.post(ENDPOINT, json=payload)

    assert response.status_code == 200
    assert response.json()["reference_photon_count"] == 100_000.0


@pytest.mark.parametrize(
    "overrides",
    [
        {"reference_photon_count": 0.0},
        {"reference_photon_count": -100.0},
        {"reference_photon_count": 1e13},
        {"seed": -1},
        {"seed": 2**32},
        {"frequencies_mhz": []},
        {"contrast": 0.8},
        {"linewidth_mhz": 0.0},
    ],
)
def test_invalid_noise_inputs_return_422(
    overrides: dict[str, object],
) -> None:
    """Invalid noise-model inputs must be rejected."""
    payload = make_payload()
    payload.update(overrides)

    response = client.post(ENDPOINT, json=payload)

    assert response.status_code == 422


def test_noisy_endpoint_is_in_openapi_schema() -> None:
    """The new endpoint must appear in the API documentation."""
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert ENDPOINT in response.json()["paths"]
