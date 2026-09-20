"""Orbit-coupled IGRF-14 magnetic-field experiment for BQRC.

This experiment connects the validated BQRC environment-model chain:

    orbital propagation
        -> unified SpaceEnvironmentSimulator
        -> ECI to ECEF
        -> WGS-84 geodetic position
        -> IGRF-14 epoch prediction
        -> geomagnetic field

The experiment deliberately uses an epoch inside the validated IGRF-14
predictive interval of 2025.0 through 2030.0.
"""

from __future__ import annotations

from datetime import UTC, datetime
from math import cos, pi, radians, sin, sqrt
from pathlib import Path

from bqrc.environment import SpaceEnvironmentSimulator
from bqrc.environment.earth import (
    EARTH_GRAVITATIONAL_PARAMETER_M3_S2,
)
from bqrc.environment.orbit import OrbitalState, propagate_rk4
from bqrc.frames import ReferenceFrame, Vector3


IGRF14_DATASET = Path(
    "data/reference/geomagnetic/igrf14/raw/igrf14coeffs.txt"
)

ORBIT_RADIUS_M = 6_771_000.0
ORBIT_INCLINATION_DEG = 51.6

PROPAGATION_STEP_SECONDS = 10.0
OUTPUT_INTERVAL_SECONDS = 300.0


def create_inclined_orbit() -> tuple[OrbitalState, float]:
    """Create an ideal circular 51.6-degree inclined orbit."""

    inclination_rad = radians(
        ORBIT_INCLINATION_DEG
    )

    circular_speed = sqrt(
        EARTH_GRAVITATIONAL_PARAMETER_M3_S2
        / ORBIT_RADIUS_M
    )

    theoretical_period = (
        2.0
        * pi
        * sqrt(
            ORBIT_RADIUS_M**3
            / EARTH_GRAVITATIONAL_PARAMETER_M3_S2
        )
    )

    state = OrbitalState(
        timestamp=datetime(
            2027,
            7,
            18,
            10,
            0,
            tzinfo=UTC,
        ),
        position=Vector3(
            x=ORBIT_RADIUS_M,
            y=0.0,
            z=0.0,
            unit="m",
            frame=ReferenceFrame.ECI,
        ),
        velocity=Vector3(
            x=0.0,
            y=circular_speed * cos(inclination_rad),
            z=circular_speed * sin(inclination_rad),
            unit="m/s",
            frame=ReferenceFrame.ECI,
        ),
    )

    return state, theoretical_period


def evaluate_state(
    state: OrbitalState,
    simulator: SpaceEnvironmentSimulator,
):
    """Evaluate the unified environment for one orbital state."""

    environment = simulator.evaluate(state)

    return (
        environment.igrf_epoch,
        environment.geodetic_position,
        environment.magnetic_field,
    )


def main() -> None:
    """Propagate one orbit while evaluating the IGRF-14 field."""

    simulator = SpaceEnvironmentSimulator.from_igrf14_dataset(
        IGRF14_DATASET
    )

    state, theoretical_period = create_inclined_orbit()

    elapsed_seconds = 0.0
    next_output_seconds = 0.0

    minimum_field_nt = float("inf")
    maximum_field_nt = float("-inf")

    print(
        "BQRC ORBIT + IGRF-14 MAGNETIC-FIELD EXPERIMENT"
    )
    print("=" * 106)

    print(
        f"Orbit inclination       : "
        f"{ORBIT_INCLINATION_DEG:.1f} deg"
    )

    print(
        f"Orbit radius            : "
        f"{ORBIT_RADIUS_M / 1000.0:.3f} km"
    )

    print(
        f"Theoretical period      : "
        f"{theoretical_period:.3f} s"
    )

    print(
        f"Propagation timestep    : "
        f"{PROPAGATION_STEP_SECONDS:.1f} s"
    )

    print(
        f"Displayed interval      : "
        f"{OUTPUT_INTERVAL_SECONDS:.1f} s"
    )

    print()

    print(
        f"{'Timestamp':<27}"
        f"{'Lat':>9}"
        f"{'Lon':>10}"
        f"{'Alt km':>10}"
        f"{'B_N nT':>12}"
        f"{'B_E nT':>12}"
        f"{'B_D nT':>12}"
        f"{'F nT':>12}"
    )

    print("-" * 104)

    while elapsed_seconds <= theoretical_period:
        if (
            elapsed_seconds
            + 1e-9
            >= next_output_seconds
        ):
            (
                epoch,
                geodetic_position,
                magnetic_field,
            ) = evaluate_state(
                state,
                simulator,
            )

            total_field = (
                magnetic_field.total_intensity_nt
            )

            minimum_field_nt = min(
                minimum_field_nt,
                total_field,
            )

            maximum_field_nt = max(
                maximum_field_nt,
                total_field,
            )

            print(
                f"{state.timestamp.isoformat():<27}"
                f"{geodetic_position.latitude_deg:>9.3f}"
                f"{geodetic_position.longitude_deg:>10.3f}"
                f"{geodetic_position.altitude_m / 1000.0:>10.3f}"
                f"{magnetic_field.north_nt:>12.1f}"
                f"{magnetic_field.east_nt:>12.1f}"
                f"{magnetic_field.down_nt:>12.1f}"
                f"{total_field:>12.1f}"
            )

            next_output_seconds += (
                OUTPUT_INTERVAL_SECONDS
            )

        state = propagate_rk4(
            state,
            PROPAGATION_STEP_SECONDS,
        )

        elapsed_seconds += (
            PROPAGATION_STEP_SECONDS
        )

    print()
    print("=" * 106)

    print(
        f"Minimum sampled field : "
        f"{minimum_field_nt:.3f} nT"
    )

    print(
        f"Maximum sampled field : "
        f"{maximum_field_nt:.3f} nT"
    )

    print(
        f"Field range           : "
        f"{maximum_field_nt - minimum_field_nt:.3f} nT"
    )

    print()

    print(
        "Orbit -> SpaceEnvironmentSimulator -> "
        "IGRF-14 integration complete."
    )


if __name__ == "__main__":
    main()