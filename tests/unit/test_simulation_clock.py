"""Tests for the deterministic master simulation clock."""

from datetime import UTC, datetime, timedelta

import pytest

from bqrc.simulation.clock import SimulationClock, period_in_steps

EPOCH = datetime(2027, 7, 18, 10, 0, tzinfo=UTC)


def test_time_is_exact_epoch_plus_steps() -> None:
    clock = SimulationClock.from_duration(EPOCH, duration_s=100.0, step_s=0.1)

    assert clock.n_steps == 1000
    assert clock.time_at(1000) == EPOCH + timedelta(seconds=100.0)
    assert clock.time_at(0) == EPOCH


def test_ticks_include_final_step() -> None:
    clock = SimulationClock.from_duration(EPOCH, 30.0, 10.0)

    assert list(clock.ticks()) == [0, 1, 2, 3]


def test_multirate_due() -> None:
    steps = period_in_steps(60.0, 10.0)

    assert steps == 6
    assert [k for k in range(14) if SimulationClock.is_due(k, steps)] == [0, 6, 12]


def test_non_integer_ratio_rejected() -> None:
    with pytest.raises(ValueError, match="integer multiple"):
        period_in_steps(25.0, 10.0)


def test_non_integer_duration_rejected() -> None:
    with pytest.raises(ValueError, match="integer multiple"):
        SimulationClock.from_duration(EPOCH, 105.0, 10.0)


def test_naive_epoch_rejected() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        SimulationClock(epoch=datetime(2027, 1, 1), step_seconds=1.0, n_steps=1)


def test_index_out_of_range() -> None:
    clock = SimulationClock.from_duration(EPOCH, 10.0, 10.0)

    with pytest.raises(IndexError):
        clock.time_at(2)
