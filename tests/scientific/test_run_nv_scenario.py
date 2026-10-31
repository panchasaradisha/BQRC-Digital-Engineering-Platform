"""End-to-end V1 slice: clock -> orbit -> environment -> NV -> estimate -> truth check."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pytest

from bqrc.core import DataSource, ProcessingLevel, QualityFlag
from bqrc.environment import SpaceEnvironmentSimulator
from bqrc.frames.attitude import Quaternion
from bqrc.sensors.nv.config import NVSensorConfig
from bqrc.sensors.nv.environment_adapter import simulate_attitude_aware_nv_response
from bqrc.sensors.nv.resonance import project_magnetic_field
from bqrc.simulation.attitude import attitude_at
from bqrc.simulation.config import AttitudeProfile, EstimatorConfig, ScenarioConfig
from bqrc.simulation.orbit import advance_orbit, circular_orbit_state
from bqrc.simulation.runner import derive_seed, run_nv_scenario
from bqrc.simulation.storage import write_run
from bqrc.simulation.truth import TruthState

EPOCH = datetime(2027, 7, 18, 10, 0, tzinfo=UTC)
DATASET = Path("data/reference/geomagnetic/igrf14/raw/igrf14coeffs.txt")
COARSE = NVSensorConfig(
    sweep_start_mhz=2860.0, sweep_stop_mhz=2880.0, sweep_points=81,
    nv_axis_body=(0.3, -0.5, 0.8),
)


def scenario(**overrides) -> ScenarioConfig:
    base = {
        "scenario_id": "e2e", "epoch": EPOCH, "duration_s": 120.0, "step_s": 10.0,
        "nv_sensor": COARSE, "seed": 7,
        "attitude": AttitudeProfile(initial_body_to_ned=(0.8, 0.2, -0.3, 0.4)),
    }
    base.update(overrides)
    return ScenarioConfig(**base)


@pytest.fixture(scope="module")
def simulator() -> SpaceEnvironmentSimulator:
    return SpaceEnvironmentSimulator.from_igrf14_dataset(DATASET)


@pytest.fixture(scope="module")
def result(simulator):
    return run_nv_scenario(scenario(), simulator=simulator)


def test_expected_number_of_acquisitions(result) -> None:
    assert len(result.acquisitions) == len(result.measurements) == len(result.errors) == 3


def test_products_are_tagged(result) -> None:
    for m in result.measurements:
        assert m.level == ProcessingLevel.L4_ESTIMATED
        assert m.source == DataSource.SIMULATED_SENSOR
        assert m.configuration_id == result.configuration_id
        assert QualityFlag.UNCALIBRATED in m.quality
        assert m.uncertainty is not None and m.uncertainty.value > 0

    assert all(a.configuration_id == result.configuration_id for a in result.acquisitions)


def test_estimates_consistent_with_claimed_uncertainty(result) -> None:
    for e in result.errors:
        assert e.fit_success
        assert e.z_score is not None and abs(e.z_score) < 5.0
        assert e.true_nt > 1_000.0  # a real geomagnetic field, not a degenerate case


def test_run_is_deterministic(simulator, result) -> None:
    again = run_nv_scenario(scenario(), simulator=simulator)

    assert again.acquisitions == result.acquisitions
    assert again.errors == result.errors


def test_seed_changes_noise(simulator, result) -> None:
    other = run_nv_scenario(scenario(seed=8), simulator=simulator)

    assert other.acquisitions[0].photon_counts != result.acquisitions[0].photon_counts


def test_noise_differs_between_ticks_even_with_identical_field(simulator) -> None:
    # Same stimulus, same master seed, different tick -> different noise.
    assert derive_seed(7, 0, 0) != derive_seed(7, 0, 6)
    assert derive_seed(7, 0, 6) == derive_seed(7, 0, 6)
    assert derive_seed(7, 0, 6) != derive_seed(7, 1, 6)


def test_stimulus_matches_attitude_aware_adapter(simulator) -> None:
    config = scenario()
    state = advance_orbit(circular_orbit_state(EPOCH, config.orbit), 300.0)
    state = state.model_copy(update={"timestamp": EPOCH.replace(minute=5)})
    attitude = attitude_at(config.attitude, 300.0)
    environment = simulator.evaluate(state)

    truth = TruthState(state.timestamp, state, attitude, environment)
    axis = config.nv_sensor.nv_axis_body

    ours = project_magnetic_field(truth.sensor_stimulus().magnetic_field_body_nt, axis)
    reference = simulate_attitude_aware_nv_response(
        environment=environment,
        nv_axis_body=axis,
        attitude_body_to_ned=Quaternion(*config.attitude.initial_body_to_ned),
        frequencies_mhz=config.nv_sensor.frequencies_mhz(),
    ).resonance.projected_field_nt

    assert ours == pytest.approx(reference, abs=1e-6)


def test_spin_about_nv_axis_keeps_true_projection_constant(simulator) -> None:
    axis = (0.3, -0.5, 0.8)
    still = run_nv_scenario(scenario(), simulator=simulator)
    spinning = run_nv_scenario(
        scenario(attitude=AttitudeProfile(
            initial_body_to_ned=(0.8, 0.2, -0.3, 0.4), rate_axis_body=axis, rate_rad_s=0.05,
        )),
        simulator=simulator,
    )

    for a, b in zip(still.errors, spinning.errors, strict=True):
        assert a.true_nt == pytest.approx(b.true_nt, abs=1e-6)


def test_model_mismatch_is_visible_in_errors(simulator, result) -> None:
    wrong = scenario(estimator=EstimatorConfig(assumed_linewidth_mhz=3.0))
    mismatched = run_nv_scenario(wrong, simulator=simulator)

    # Same seed -> identical photon counts; only the estimator's assumption differs.
    assert [a.photon_counts for a in mismatched.acquisitions] == [
        a.photon_counts for a in result.acquisitions
    ]
    assert [m.value for m in mismatched.measurements] != [m.value for m in result.measurements]


def test_storage_roundtrip(result, tmp_path) -> None:
    out = write_run(result, tmp_path / "run")

    assert {p.name for p in out.iterdir()} == {
        "config.json", "manifest.json", "acquisitions.npz", "measurements.jsonl", "errors.jsonl",
    }

    manifest = json.loads((out / "manifest.json").read_text())
    assert manifest["configuration_id"] == result.configuration_id
    assert manifest["n_acquisitions"] == 3

    restored = ScenarioConfig.model_validate_json((out / "config.json").read_text())
    assert restored.configuration_id == result.configuration_id

    data = np.load(out / "acquisitions.npz")
    assert data["photon_counts"].shape == (3, 81)
    assert tuple(data["photon_counts"][0]) == result.acquisitions[0].photon_counts

    lines = (out / "measurements.jsonl").read_text().splitlines()
    assert len(lines) == 3 and json.loads(lines[0])["level"] == "L4_estimated"
