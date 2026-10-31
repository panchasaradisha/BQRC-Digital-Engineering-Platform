"""Tests for the stimulus boundary, sensor interface and L1 acquisition."""

import dataclasses
from datetime import UTC, datetime

import pytest

from bqrc.core.provenance import DataSource
from bqrc.sensors.interface import SensorInterface
from bqrc.sensors.nv.acquisition import ODMRAcquisition
from bqrc.sensors.nv.config import NVSensorConfig
from bqrc.sensors.nv.simulated_sensor import SimulatedNVSensor
from bqrc.sensors.stimulus import SensorStimulus

NOW = datetime(2027, 7, 18, 10, 0, tzinfo=UTC)
COARSE = NVSensorConfig(sweep_start_mhz=2860.0, sweep_stop_mhz=2880.0, sweep_points=81)


def stimulus(field=(0.0, 0.0, 20_000.0)) -> SensorStimulus:
    return SensorStimulus(timestamp=NOW, magnetic_field_body_nt=field)


def test_simulated_sensor_satisfies_interface() -> None:
    assert isinstance(SimulatedNVSensor(COARSE), SensorInterface)


def test_sample_is_reproducible_and_seed_sensitive() -> None:
    sensor = SimulatedNVSensor(COARSE, configuration_id="abc")

    a = sensor.sample(stimulus(), seed=1)
    b = sensor.sample(stimulus(), seed=1)
    c = sensor.sample(stimulus(), seed=2)

    assert a == b
    assert a.photon_counts != c.photon_counts
    assert a.configuration_id == "abc"
    assert a.data_source == DataSource.SIMULATED_SENSOR


def test_acquisition_exposes_no_truth_or_ideal_spectrum() -> None:
    names = {f.name for f in dataclasses.fields(ODMRAcquisition)}

    assert names == {
        "sensor_id", "timestamp", "frequencies_mhz", "photon_counts",
        "reference_photon_count", "model_version", "configuration_id", "data_source",
    }


def test_field_projects_on_body_axis() -> None:
    sensor = SimulatedNVSensor(COARSE.model_copy(update={"nv_axis_body": (1.0, 0.0, 0.0)}))

    # Field entirely along body z: zero projection on the x-axis NV -> dips at D.
    acq = sensor.sample(stimulus((0.0, 0.0, 30_000.0)), seed=0)
    freqs = acq.frequencies_mhz
    counts = acq.photon_counts
    lowest = freqs[counts.index(min(counts))]

    assert lowest == pytest.approx(2870.0, abs=0.5)


def test_fluorescence_is_counts_over_reference() -> None:
    acq = SimulatedNVSensor(COARSE).sample(stimulus(), seed=3)

    assert acq.fluorescence[0] == acq.photon_counts[0] / acq.reference_photon_count


def test_stimulus_validation() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        SensorStimulus(timestamp=datetime(2027, 1, 1), magnetic_field_body_nt=(0, 0, 1))

    with pytest.raises(ValueError, match="finite"):
        SensorStimulus(timestamp=NOW, magnetic_field_body_nt=(0, float("nan"), 1))

    with pytest.raises(ValueError, match="temperature"):
        SensorStimulus(timestamp=NOW, magnetic_field_body_nt=(0, 0, 1), temperature_k=-1.0)


def test_health_reports_nominal() -> None:
    assert SimulatedNVSensor(COARSE).health().nominal is True
