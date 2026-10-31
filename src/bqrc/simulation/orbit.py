"""Orbit setup and stepping helpers for scenario runs."""

from __future__ import annotations

from datetime import datetime
from math import ceil, cos, radians, sin, sqrt

from bqrc.environment.earth import EARTH_GRAVITATIONAL_PARAMETER_M3_S2
from bqrc.environment.orbit import OrbitalState, propagate_rk4
from bqrc.frames import ReferenceFrame, Vector3
from bqrc.simulation.config import OrbitConfig

MAX_INTEGRATION_STEP_S = 10.0


def circular_orbit_state(epoch: datetime, orbit: OrbitConfig) -> OrbitalState:
    """Initial ECI state of an ideal circular inclined orbit at the x axis."""

    inclination = radians(orbit.inclination_deg)
    speed = sqrt(EARTH_GRAVITATIONAL_PARAMETER_M3_S2 / orbit.radius_m)

    return OrbitalState(
        timestamp=epoch,
        position=Vector3(
            x=orbit.radius_m, y=0.0, z=0.0, unit="m", frame=ReferenceFrame.ECI
        ),
        velocity=Vector3(
            x=0.0,
            y=speed * cos(inclination),
            z=speed * sin(inclination),
            unit="m/s",
            frame=ReferenceFrame.ECI,
        ),
    )


def advance_orbit(state: OrbitalState, duration_s: float) -> OrbitalState:
    """Advance by ``duration_s`` using equal RK4 sub-steps of at most 10 s."""

    n_sub = max(1, ceil(duration_s / MAX_INTEGRATION_STEP_S))
    sub = duration_s / n_sub

    for _ in range(n_sub):
        state = propagate_rk4(state, sub)

    return state
