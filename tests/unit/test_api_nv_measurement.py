
"""Tests for the integrated NV measurement API."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from bqrc.api.main import app

client = TestClient(app)

ENDPOINT = "/api/v1/nv/odmr/measurement"


def make_payload() -> dict[str, object]:
    """Create a reproducible NV measurement request."""
    return {
        "magnetic_field_nt": [50000.0, 0.0, 0.0],
        "nv_axis": [1.0, 0.0, 0.0],
        "frequencies_mhz": [
            2867.0 + index * 0.05
            for index in range(121)
        ],
        "contrast": 0.1,
        "linewidth_mhz": 1.0,
        "reference_photon_count": 1_000_000.0,
        "seed": 42,
    }


def test_complete_measurement_pipeline() -> None:
    """Simulation, estimation, and uncertainty work together."""
    response = client.post(ENDPOINT, json=make_payload())

    assert response.status_code == 200

    result = response.json()

    assert result["fit_success"] is True
    assert result["estimation"] is not None
    assert result["uncertainty"] is not None

    simulation = result["simulation"]

    assert len(simulation["frequencies_mhz"]) == 121
    assert len(simulation["photon_counts"]) == 121
    assert len(simulation["ideal_fluorescence"]) == 121
    assert len(simulation["measured_fluorescence"]) == 121


def test_field_estimation_accuracy() -> None:
    """The integrated fit recovers the simulated field."""
    response = client.post(ENDPOINT, json=make_payload())

    assert response.status_code == 200

    result = response.json()
    estimate = result["estimation"]

    assert estimate is not None
    assert estimate["projected_field_magnitude_nt"] == pytest.approx(
        50000.0,
        abs=500.0,
    )


def test_uncertainty_is_positive() -> None:
    """An identifiable measurement has positive CRLB."""
    response = client.post(ENDPOINT, json=make_payload())

    assert response.status_code == 200

    uncertainty = response.json()["uncertainty"]

    assert uncertainty is not None
    assert uncertainty["identifiable_locally"] is True
    assert uncertainty["crlb_std_nt"] > 0.0
    assert uncertainty["fisher_information_per_nt_squared"] > 0.0


def test_measurement_is_reproducible() -> None:
    """The same random seed reproduces the complete response."""
    payload = make_payload()

    first = client.post(ENDPOINT, json=payload)
    second = client.post(ENDPOINT, json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()


def test_simulation_matches_existing_endpoint() -> None:
    """The integrated pipeline reuses existing simulation behavior."""
    payload = make_payload()

    integrated = client.post(ENDPOINT, json=payload)
    standalone = client.post(
        "/api/v1/nv/odmr/noisy-spectrum",
        json=payload,
    )

    assert integrated.status_code == 200
    assert standalone.status_code == 200
    assert integrated.json()["simulation"] == standalone.json()


def test_estimation_matches_existing_endpoint() -> None:
    """The integrated fit agrees with the standalone estimator."""
    payload = make_payload()

    integrated = client.post(ENDPOINT, json=payload)
    assert integrated.status_code == 200

    result = integrated.json()
    simulation = result["simulation"]

    standalone = client.post(
        "/api/v1/nv/odmr/estimate-field",
        json={
            "frequencies_mhz": simulation["frequencies_mhz"],
            "photon_counts": simulation["photon_counts"],
            "reference_photon_count": (
                simulation["reference_photon_count"]
            ),
            "contrast": payload["contrast"],
            "linewidth_mhz": payload["linewidth_mhz"],
        },
    )

    assert standalone.status_code == 200
    assert result["estimation"] == standalone.json()


def test_uncertainty_matches_existing_endpoint() -> None:
    """The integrated CRLB agrees with standalone uncertainty."""
    payload = make_payload()

    integrated = client.post(ENDPOINT, json=payload)
    assert integrated.status_code == 200

    result = integrated.json()
    estimate = result["estimation"]

    assert estimate is not None

    standalone = client.post(
        "/api/v1/nv/odmr/field-uncertainty",
        json={
            "frequencies_mhz": payload["frequencies_mhz"],
            "projected_field_magnitude_nt": (
                estimate["projected_field_magnitude_nt"]
            ),
            "reference_photon_count": (
                payload["reference_photon_count"]
            ),
            "contrast": payload["contrast"],
            "linewidth_mhz": payload["linewidth_mhz"],
        },
    )

    assert standalone.status_code == 200
    assert result["uncertainty"] == standalone.json()


def test_fit_failure_preserves_simulation() -> None:
    """An unsuccessful fit must not discard valid simulated data."""
    with patch(
        "bqrc.api.nv.estimate_nv_field_from_odmr",
        side_effect=RuntimeError("fit failed"),
    ):
        response = client.post(ENDPOINT, json=make_payload())

    assert response.status_code == 200

    result = response.json()

    assert result["fit_success"] is False
    assert result["estimation"] is None
    assert result["uncertainty"] is None
    assert len(result["simulation"]["photon_counts"]) == 121


@pytest.mark.parametrize(
    "overrides",
    [
        {"frequencies_mhz": [2868.0, 2869.0]},
        {"frequencies_mhz": [2880.0 + i for i in range(5)]},
        {"nv_axis": [0.0, 0.0, 0.0]},
        {"reference_photon_count": 0.0},
        {"contrast": 0.0},
        {"contrast": 0.6},
        {"linewidth_mhz": 0.0},
        {"seed": -1},
    ],
)
def test_invalid_requests_return_422(
    overrides: dict[str, object],
) -> None:
    """Reject invalid measurement parameters."""
    payload = make_payload()
    payload.update(overrides)

    response = client.post(ENDPOINT, json=payload)

    assert response.status_code == 422


def test_endpoint_is_in_openapi() -> None:
    """The measurement endpoint appears in API documentation."""
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert ENDPOINT in response.json()["paths"]
