"""Scientific regression tests for the BQRC two-body orbit model."""

from datetime import UTC, datetime
from math import pi, sqrt

from bqrc.environment.earth import EARTH_GRAVITATIONAL_PARAMETER_M3_S2
from bqrc.environment.orbit import OrbitalState, propagate_rk4
from bqrc.frames import ReferenceFrame, Vector3

TEST_RADIUS_M = 6_771_000.0
TEST_STEP_SECONDS = 10.0


def _create_circular_orbit() -> tuple[OrbitalState, float]:
    """Create the verified circular two-body regression scenario."""

    circular_speed = sqrt(
        EARTH_GRAVITATIONAL_PARAMETER_M3_S2 / TEST_RADIUS_M
    )

    theoretical_period = 2.0 * pi * sqrt(
        TEST_RADIUS_M**3 / EARTH_GRAVITATIONAL_PARAMETER_M3_S2
    )

    state = OrbitalState(
        timestamp=datetime(2032, 7, 18, 10, 0, tzinfo=UTC),
        position=Vector3(
            x=TEST_RADIUS_M,
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

    return state, theoretical_period


def _vector_difference_magnitude(
    first: Vector3,
    second: Vector3,
) -> float:
    """Calculate Euclidean vector-difference magnitude."""

    dx = first.x - second.x
    dy = first.y - second.y
    dz = first.z - second.z

    return sqrt(dx**2 + dy**2 + dz**2)


def _specific_orbital_energy(state: OrbitalState) -> float:
    """Calculate two-body specific orbital energy."""

    return (
        state.velocity.magnitude**2 / 2.0
        - EARTH_GRAVITATIONAL_PARAMETER_M3_S2
        / state.position.magnitude
    )


def _propagate_one_orbit() -> tuple[OrbitalState, OrbitalState, float]:
    """Propagate the verified scenario for one theoretical orbit."""

    initial_state, theoretical_period = _create_circular_orbit()

    full_steps = int(theoretical_period // TEST_STEP_SECONDS)

    remaining_seconds = (
        theoretical_period
        - full_steps * TEST_STEP_SECONDS
    )

    state = initial_state
    maximum_radius_error = 0.0

    for _ in range(full_steps):
        state = propagate_rk4(
            state,
            TEST_STEP_SECONDS,
        )

        radius_error = abs(
            state.position.magnitude
            - initial_state.position.magnitude
        )

        maximum_radius_error = max(
            maximum_radius_error,
            radius_error,
        )

    if remaining_seconds > 0.0:
        state = propagate_rk4(
            state,
            remaining_seconds,
        )

        radius_error = abs(
            state.position.magnitude
            - initial_state.position.magnitude
        )

        maximum_radius_error = max(
            maximum_radius_error,
            radius_error,
        )

    return initial_state, state, maximum_radius_error


def test_one_orbit_position_closure_remains_below_threshold() -> None:
    """One-orbit RK4 position closure should remain below 5 cm."""

    initial_state, final_state, _ = _propagate_one_orbit()

    position_error = _vector_difference_magnitude(
        final_state.position,
        initial_state.position,
    )

    assert position_error < 0.05


def test_one_orbit_velocity_closure_remains_below_threshold() -> None:
    """One-orbit RK4 velocity closure should remain below 50 micrometres/s."""

    initial_state, final_state, _ = _propagate_one_orbit()

    velocity_error = _vector_difference_magnitude(
        final_state.velocity,
        initial_state.velocity,
    )

    assert velocity_error < 50e-6


def test_one_orbit_radius_drift_remains_below_threshold() -> None:
    """Circular-orbit radial drift should remain below 1 cm."""

    _, _, maximum_radius_error = _propagate_one_orbit()

    assert maximum_radius_error < 0.01


def test_one_orbit_energy_drift_remains_below_threshold() -> None:
    """Specific-energy drift should remain below 0.002 J/kg."""

    initial_state, final_state, _ = _propagate_one_orbit()

    energy_error = abs(
        _specific_orbital_energy(final_state)
        - _specific_orbital_energy(initial_state)
    )

    assert energy_error < 0.002