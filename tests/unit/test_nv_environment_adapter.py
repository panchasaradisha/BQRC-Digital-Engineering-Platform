
"""Integration tests for the NV-center environment adapter."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

import pytest

from bqrc.environment.simulator import SpaceEnvironmentState
from bqrc.sensors.nv.environment_adapter import (
    simulate_nv_environment_response,
)


def make_environment(
    north_nt: float,
    east_nt: float,
    down_nt: float,
) -> SpaceEnvironmentState:
    """Construct a controlled magnetic environment test fixture."""

    magnetic_field = SimpleNamespace(
        north_nt=north_nt,
        east_nt=east_nt,
        down_nt=down_nt,
    )

    environment = SimpleNamespace(magnetic_field=magnetic_field)

    return cast(SpaceEnvironmentState, cast(Any, environment))


def test_north_aligned_nv_axis() -> None:
    """The north magnetic component is projected onto a north NV axis."""

    environment = make_environment(
        north_nt=30_000.0,
        east_nt=4_000.0,
        down_nt=20_000.0,
    )

    response = simulate_nv_environment_response(
        environment=environment,
        nv_axis_ned=(1.0, 0.0, 0.0),
        frequencies_mhz=(2869.0, 2870.0, 2871.0),
    )

    assert response.resonance.projected_field_nt == pytest.approx(
        30_000.0
    )
    assert len(response.spectrum.fluorescence) == 3


def test_east_aligned_nv_axis() -> None:
    """The east magnetic component is projected onto an east NV axis."""

    environment = make_environment(
        north_nt=30_000.0,
        east_nt=4_000.0,
        down_nt=20_000.0,
    )

    response = simulate_nv_environment_response(
        environment=environment,
        nv_axis_ned=(0.0, 1.0, 0.0),
        frequencies_mhz=(2870.0,),
    )

    assert response.resonance.projected_field_nt == pytest.approx(
        4_000.0
    )


def test_down_aligned_nv_axis() -> None:
    """The down magnetic component is projected onto a down NV axis."""

    environment = make_environment(
        north_nt=30_000.0,
        east_nt=4_000.0,
        down_nt=20_000.0,
    )

    response = simulate_nv_environment_response(
        environment=environment,
        nv_axis_ned=(0.0, 0.0, 1.0),
        frequencies_mhz=(2870.0,),
    )

    assert response.resonance.projected_field_nt == pytest.approx(
        20_000.0
    )


def test_opposite_nv_axis_reverses_projection() -> None:
    """Reversing the NV axis reverses the signed field projection."""

    environment = make_environment(
        north_nt=30_000.0,
        east_nt=4_000.0,
        down_nt=20_000.0,
    )

    positive = simulate_nv_environment_response(
        environment=environment,
        nv_axis_ned=(1.0, 0.0, 0.0),
        frequencies_mhz=(2870.0,),
    )

    negative = simulate_nv_environment_response(
        environment=environment,
        nv_axis_ned=(-1.0, 0.0, 0.0),
        frequencies_mhz=(2870.0,),
    )

    assert negative.resonance.projected_field_nt == pytest.approx(
        -positive.resonance.projected_field_nt
    )

    assert negative.resonance.lower_mhz == pytest.approx(
        positive.resonance.lower_mhz
    )


def test_zero_magnetic_field() -> None:
    """Zero magnetic field produces overlapping NV resonances."""

    environment = make_environment(
        north_nt=0.0,
        east_nt=0.0,
        down_nt=0.0,
    )

    response = simulate_nv_environment_response(
        environment=environment,
        nv_axis_ned=(1.0, 0.0, 0.0),
        frequencies_mhz=(2870.0,),
        contrast=0.1,
    )

    assert response.resonance.lower_mhz == pytest.approx(2870.0)
    assert response.resonance.upper_mhz == pytest.approx(2870.0)
    assert response.spectrum.fluorescence[0] == pytest.approx(0.8)


def test_invalid_nv_axis_is_rejected() -> None:
    """A zero-length NV axis must raise ValueError."""

    environment = make_environment(
        north_nt=30_000.0,
        east_nt=0.0,
        down_nt=0.0,
    )

    with pytest.raises(ValueError):
        simulate_nv_environment_response(
            environment=environment,
            nv_axis_ned=(0.0, 0.0, 0.0),
            frequencies_mhz=(2870.0,),
        )


def test_invalid_odmr_contrast_is_rejected() -> None:
    """The adapter must preserve ODMR parameter validation."""

    environment = make_environment(
        north_nt=30_000.0,
        east_nt=0.0,
        down_nt=0.0,
    )

    with pytest.raises(ValueError):
        simulate_nv_environment_response(
            environment=environment,
            nv_axis_ned=(1.0, 0.0, 0.0),
            frequencies_mhz=(2870.0,),
            contrast=0.8,
        )
