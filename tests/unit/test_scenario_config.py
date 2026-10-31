"""Tests for scenario configuration and its hash."""

from datetime import UTC, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from bqrc.sensors.nv.config import NVSensorConfig
from bqrc.simulation.config import EstimatorConfig, ScenarioConfig

EPOCH = datetime(2027, 7, 18, 10, 0, tzinfo=UTC)


def make(**overrides) -> ScenarioConfig:
    base = {"scenario_id": "t", "epoch": EPOCH, "duration_s": 600.0}
    base.update(overrides)
    return ScenarioConfig(**base)


def test_hash_is_stable_and_json_roundtrips() -> None:
    config = make()
    clone = ScenarioConfig.model_validate_json(config.model_dump_json())

    assert clone == config
    assert clone.configuration_id == config.configuration_id
    assert len(config.configuration_id) == 16


def test_hash_changes_with_any_field() -> None:
    base = make().configuration_id

    assert make(seed=1).configuration_id != base
    assert make(estimator=EstimatorConfig(assumed_linewidth_mhz=2.0)).configuration_id != base


def test_epoch_normalized_to_utc() -> None:
    ist = timezone(timedelta(hours=5, minutes=30))
    config = make(epoch=datetime(2027, 7, 18, 15, 30, tzinfo=ist))

    assert config.epoch == EPOCH
    assert config.configuration_id == make().configuration_id


def test_naive_epoch_rejected() -> None:
    with pytest.raises(ValidationError):
        make(epoch=datetime(2027, 7, 18, 10, 0))


def test_acquisition_period_must_be_multiple_of_step() -> None:
    sensor = NVSensorConfig(acquisition_period_s=25.0)

    with pytest.raises(ValidationError, match="integer multiple"):
        make(nv_sensor=sensor, step_s=10.0)


def test_sweep_must_span_zero_field_splitting() -> None:
    with pytest.raises(ValidationError, match="span"):
        NVSensorConfig(sweep_start_mhz=2880.0, sweep_stop_mhz=2900.0)


def test_orbit_must_be_above_earth() -> None:
    with pytest.raises(ValidationError):
        make(orbit={"radius_m": 6_000_000.0})


def test_estimator_assumptions_are_separate_from_sensor_truth() -> None:
    config = make(
        nv_sensor=NVSensorConfig(linewidth_mhz=1.5),
        estimator=EstimatorConfig(assumed_linewidth_mhz=1.0),
    )

    assert config.nv_sensor.linewidth_mhz != config.estimator.assumed_linewidth_mhz
