"""Residual-microgravity environment model for BQRC.

The BQRC microgravity model distinguishes gravitational acceleration
from residual acceleration experienced by a freely falling spacecraft.

Earth's gravitational acceleration in low Earth orbit is not close to
zero. Microgravity arises because the spacecraft and objects within it
are approximately in common free fall.

This module therefore represents residual microgravity separately from
the gravitational acceleration already used by the orbital propagator.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from bqrc.environment.orbit import OrbitalState
from bqrc.frames import ReferenceFrame, Vector3


@dataclass(frozen=True, slots=True)
class MicrogravityState:
    """Residual acceleration environment at one simulation instant.

    Parameters
    ----------
    residual_acceleration:
        Net residual/non-gravitational acceleration expressed in the
        ECI frame in metres per second squared.

    Notes
    -----
    The residual acceleration is not Earth's gravitational acceleration.

    For an ideal two-body freely falling spacecraft with no modeled
    disturbances, residual acceleration is zero.
    """

    residual_acceleration: Vector3

    def __post_init__(self) -> None:
        """Validate the residual-acceleration representation."""

        if self.residual_acceleration.frame != ReferenceFrame.ECI:
            raise ValueError(
                "residual acceleration must use the ECI frame"
            )

        if self.residual_acceleration.unit != "m/s^2":
            raise ValueError(
                "residual acceleration must use m/s^2"
            )

        for value in (
            self.residual_acceleration.x,
            self.residual_acceleration.y,
            self.residual_acceleration.z,
        ):
            if not isfinite(value):
                raise ValueError(
                    "residual acceleration components must be finite"
                )

    @property
    def magnitude_m_s2(self) -> float:
        """Return residual-acceleration magnitude in m/s^2."""

        return (
            self.residual_acceleration.x**2
            + self.residual_acceleration.y**2
            + self.residual_acceleration.z**2
        ) ** 0.5

    @property
    def magnitude_micro_g(self) -> float:
        """Return residual acceleration in micro-g."""

        standard_gravity_m_s2 = 9.80665

        return (
            self.magnitude_m_s2
            / standard_gravity_m_s2
            * 1_000_000.0
        )


class MicrogravityModel:
    """Evaluate the BQRC residual-microgravity environment.

    The initial model establishes the ideal orbital free-fall baseline.

    Disturbance models will later contribute non-zero residual
    accelerations without changing this public interface.
    """

    def evaluate(
        self,
        orbital_state: OrbitalState,
    ) -> MicrogravityState:
        """Evaluate residual acceleration for an orbital state.

        The current baseline assumes ideal two-body free fall and no
        non-gravitational disturbances. The resulting residual
        acceleration is therefore zero.

        The orbital state is still required so that future disturbance
        models can depend on position, velocity, and simulation time.
        """

        if orbital_state.position.frame != ReferenceFrame.ECI:
            raise ValueError(
                "microgravity model requires an ECI orbital state"
            )

        return MicrogravityState(
            residual_acceleration=Vector3(
                x=0.0,
                y=0.0,
                z=0.0,
                unit="m/s^2",
                frame=ReferenceFrame.ECI,
            )
        )