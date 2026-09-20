"""Tests for the BQRC RK4 orbital propagator."""

from datetime import UTC, datetime
from math import isclose, sqrt

import pytest

from bqrc.environment.earth import EARTH_GRAVITATIONAL_PARAMETER_M3_S2
from bqrc.environment.orbit import OrbitalState, propagate_rk4
from bqrc.frames import ReferenceFrame, Vector3


def _circular_orbit_state() -> OrbitalState:
    """Create a simple circular two-body test state."""

    radius = 6_771_000.0

    circular_speed = sqrt(
        EARTH_GRAVITATIONAL_PARAMETER_M3_S2 / radius
    )

    return OrbitalState(
        timestamp=datetime(2032, 7, 18, 10, 0, tzinfo=UTC),
        position=Vector3(
            x=radius,
            y=0.0,
            z=0.0,
            unit="m",
            frame=ReferenceFrame.ECI,
        ),
        velocity=Vector3(
            x=0.0,
            y=circular_speed,
            z=0.0,
            unit="m/s",
            frame=ReferenceFrame.ECI,
        ),
    )


def test_propagator_advances_timestamp() -> None:
    """Propagation should advance the state's timestamp."""

    state = _circular_orbit_state()

    propagated = propagate_rk4(state, 10.0)

    assert (
        propagated.timestamp - state.timestamp
    ).total_seconds() == 10.0


def test_propagator_changes_position() -> None:
    """An orbiting spacecraft should move during propagation."""

    state = _circular_orbit_state()

    propagated = propagate_rk4(state, 10.0)

    assert propagated.position != state.position


def test_circular_orbit_radius_is_nearly_preserved() -> None:
    """A short RK4 step should preserve circular-orbit radius closely."""

    state = _circular_orbit_state()

    propagated = propagate_rk4(state, 10.0)

    assert isclose(
        propagated.position.magnitude,
        state.position.magnitude,
        rel_tol=1e-9,
    )


def test_specific_orbital_energy_is_nearly_preserved() -> None:
    """A short two-body RK4 step should nearly conserve orbital energy."""

    state = _circular_orbit_state()
    propagated = propagate_rk4(state, 10.0)

    initial_energy = (
        state.velocity.magnitude**2 / 2.0
        - EARTH_GRAVITATIONAL_PARAMETER_M3_S2
        / state.position.magnitude
    )

    propagated_energy = (
        propagated.velocity.magnitude**2 / 2.0
        - EARTH_GRAVITATIONAL_PARAMETER_M3_S2
        / propagated.position.magnitude
    )

    assert isclose(
        propagated_energy,
        initial_energy,
        rel_tol=1e-10,
    )


def test_non_positive_step_is_rejected() -> None:
    """The V1 propagator should only accept positive time steps."""

    state = _circular_orbit_state()

    with pytest.raises(ValueError):
        propagate_rk4(state, 0.0)

    with pytest.raises(ValueError):
        propagate_rk4(state, -1.0)


def test_wrong_velocity_unit_is_rejected() -> None:
    """The propagator should reject incompatible velocity units."""

    state = OrbitalState(
        timestamp=datetime(2032, 7, 18, 10, 0, tzinfo=UTC),
        position=Vector3(
            x=6_771_000.0,
            y=0.0,
            z=0.0,
            unit="m",
            frame=ReferenceFrame.ECI,
        ),
        velocity=Vector3(
            x=0.0,
            y=7.67,
            z=0.0,
            unit="km/s",
            frame=ReferenceFrame.ECI,
        ),
    )

    with pytest.raises(ValueError):
        propagate_rk4(state, 10.0)