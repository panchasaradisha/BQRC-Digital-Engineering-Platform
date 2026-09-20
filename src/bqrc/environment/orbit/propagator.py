"""Numerical orbital propagation for the BQRC environment model."""

from datetime import timedelta

from bqrc.environment.orbit.gravity import two_body_acceleration
from bqrc.environment.orbit.state import OrbitalState
from bqrc.frames import ReferenceFrame, Vector3


def _derivatives(
    position: tuple[float, float, float],
    velocity: tuple[float, float, float],
) -> tuple[
    tuple[float, float, float],
    tuple[float, float, float],
]:
    """Return position and velocity derivatives for two-body motion."""

    position_vector = Vector3(
        x=position[0],
        y=position[1],
        z=position[2],
        unit="m",
        frame=ReferenceFrame.ECI,
    )

    acceleration = two_body_acceleration(position_vector)

    dr_dt = velocity
    dv_dt = (
        acceleration.x,
        acceleration.y,
        acceleration.z,
    )

    return dr_dt, dv_dt


def _add_scaled(
    base: tuple[float, float, float],
    derivative: tuple[float, float, float],
    scale: float,
) -> tuple[float, float, float]:
    """Add a scaled derivative to a three-component state."""

    return (
        base[0] + derivative[0] * scale,
        base[1] + derivative[1] * scale,
        base[2] + derivative[2] * scale,
    )


def propagate_rk4(
    state: OrbitalState,
    step_seconds: float,
) -> OrbitalState:
    """Advance an ECI orbital state by one RK4 integration step."""

    if step_seconds <= 0.0:
        raise ValueError("step_seconds must be positive")

    if state.position.frame != ReferenceFrame.ECI:
        raise ValueError("RK4 propagator currently requires the ECI frame")

    if state.position.unit != "m":
        raise ValueError("orbital position must use metres")

    if state.velocity.unit != "m/s":
        raise ValueError("orbital velocity must use metres per second")

    r0 = (
        state.position.x,
        state.position.y,
        state.position.z,
    )

    v0 = (
        state.velocity.x,
        state.velocity.y,
        state.velocity.z,
    )

    k1_r, k1_v = _derivatives(r0, v0)

    r2 = _add_scaled(r0, k1_r, step_seconds / 2.0)
    v2 = _add_scaled(v0, k1_v, step_seconds / 2.0)
    k2_r, k2_v = _derivatives(r2, v2)

    r3 = _add_scaled(r0, k2_r, step_seconds / 2.0)
    v3 = _add_scaled(v0, k2_v, step_seconds / 2.0)
    k3_r, k3_v = _derivatives(r3, v3)

    r4 = _add_scaled(r0, k3_r, step_seconds)
    v4 = _add_scaled(v0, k3_v, step_seconds)
    k4_r, k4_v = _derivatives(r4, v4)

    new_position = tuple(
        r0[index]
        + step_seconds
        * (
            k1_r[index]
            + 2.0 * k2_r[index]
            + 2.0 * k3_r[index]
            + k4_r[index]
        )
        / 6.0
        for index in range(3)
    )

    new_velocity = tuple(
        v0[index]
        + step_seconds
        * (
            k1_v[index]
            + 2.0 * k2_v[index]
            + 2.0 * k3_v[index]
            + k4_v[index]
        )
        / 6.0
        for index in range(3)
    )

    return OrbitalState(
        timestamp=state.timestamp + timedelta(seconds=step_seconds),
        position=Vector3(
            x=new_position[0],
            y=new_position[1],
            z=new_position[2],
            unit="m",
            frame=ReferenceFrame.ECI,
        ),
        velocity=Vector3(
            x=new_velocity[0],
            y=new_velocity[1],
            z=new_velocity[2],
            unit="m/s",
            frame=ReferenceFrame.ECI,
        ),
    )