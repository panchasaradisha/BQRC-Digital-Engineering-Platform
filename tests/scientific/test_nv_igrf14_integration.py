
"""Scientific integration tests for orbit-to-NV-to-ODMR simulation."""

from __future__ import annotations

from datetime import UTC, datetime
from math import cos, radians, sin, sqrt
from pathlib import Path

import pytest

from bqrc.environment.earth import (
    EARTH_GRAVITATIONAL_PARAMETER_M3_S2,
)
from bqrc.environment.orbit import OrbitalState
from bqrc.environment.simulator import SpaceEnvironmentSimulator
from bqrc.frames import ReferenceFrame, Vector3
from bqrc.frames.attitude import Quaternion
from bqrc.sensors.nv.environment_adapter import (
    simulate_attitude_aware_nv_response,
    simulate_nv_environment_response,
)
from bqrc.sensors.nv.resonance import (
    ELECTRON_GYROMAGNETIC_RATIO_MHZ_PER_T,
    ZERO_FIELD_SPLITTING_MHZ,
)

IGRF14_DATASET = Path(
    "data/reference/geomagnetic/igrf14/raw/igrf14coeffs.txt"
)


def create_orbital_state() -> OrbitalState:
    """Create a controlled inclined-orbit state."""

    radius_m = 6_771_000.0
    inclination_rad = radians(51.6)

    speed_m_s = sqrt(
        EARTH_GRAVITATIONAL_PARAMETER_M3_S2 / radius_m
    )

    return OrbitalState(
        timestamp=datetime(2027, 7, 18, 10, 0, tzinfo=UTC),
        position=Vector3(
            x=radius_m,
            y=0.0,
            z=0.0,
            unit="m",
            frame=ReferenceFrame.ECI,
        ),
        velocity=Vector3(
            x=0.0,
            y=speed_m_s * cos(inclination_rad),
            z=speed_m_s * sin(inclination_rad),
            unit="m/s",
            frame=ReferenceFrame.ECI,
        ),
    )


def test_real_igrf14_to_nv_odmr_pipeline() -> None:
    """Real IGRF field must produce consistent NV and ODMR signals."""

    simulator = SpaceEnvironmentSimulator.from_igrf14_dataset(
        IGRF14_DATASET
    )

    environment = simulator.evaluate(create_orbital_state())

    magnetic_field = environment.magnetic_field

    # Use a non-axis-aligned NV orientation in the NED frame.
    nv_axis_ned = (1.0, 1.0, 1.0)

    # Independently calculate the normalized vector projection.
    expected_projection_nt = (
        magnetic_field.north_nt
        + magnetic_field.east_nt
        + magnetic_field.down_nt
    ) / sqrt(3.0)

    expected_shift_mhz = (
        ELECTRON_GYROMAGNETIC_RATIO_MHZ_PER_T
        * abs(expected_projection_nt)
        / 1_000_000_000.0
    )

    lower_mhz = ZERO_FIELD_SPLITTING_MHZ - expected_shift_mhz
    upper_mhz = ZERO_FIELD_SPLITTING_MHZ + expected_shift_mhz

    frequencies_mhz = (
        lower_mhz,
        ZERO_FIELD_SPLITTING_MHZ,
        upper_mhz,
    )

    response = simulate_nv_environment_response(
        environment=environment,
        nv_axis_ned=nv_axis_ned,
        frequencies_mhz=frequencies_mhz,
        contrast=0.1,
        linewidth_mhz=1.0,
    )

    assert environment.geodetic_position.altitude_m == pytest.approx(
        392_863.0,
        abs=5.0,
    )

    assert magnetic_field.total_intensity_nt == pytest.approx(
        24_031.4,
        abs=1.0,
    )

    assert response.resonance.projected_field_nt == pytest.approx(
        expected_projection_nt,
        abs=1e-8,
    )

    assert response.resonance.lower_mhz == pytest.approx(
        lower_mhz,
        abs=1e-9,
    )

    assert response.resonance.upper_mhz == pytest.approx(
        upper_mhz,
        abs=1e-9,
    )

    # Independently evaluate the two Lorentzian contributions.
    expected_fluorescence = []

    for frequency in frequencies_mhz:
        lower_offset = 2.0 * (frequency - lower_mhz)
        upper_offset = 2.0 * (frequency - upper_mhz)

        lower_dip = 1.0 / (1.0 + lower_offset**2)
        upper_dip = 1.0 / (1.0 + upper_offset**2)

        expected_fluorescence.append(
            1.0 - 0.1 * (lower_dip + upper_dip)
        )

    assert response.spectrum.frequencies_mhz == frequencies_mhz

    assert response.spectrum.fluorescence == pytest.approx(
        expected_fluorescence,
        abs=1e-12,
    )

    assert all(
        0.0 <= value <= 1.0
        for value in response.spectrum.fluorescence
    )

def test_real_igrf14_attitude_aware_nv_pipeline() -> None:
    """Verify spacecraft attitude changes NV projection in real IGRF-14 field."""

    simulator = SpaceEnvironmentSimulator.from_igrf14_dataset(
        IGRF14_DATASET
    )
    environment = simulator.evaluate(create_orbital_state())

    magnetic_field = environment.magnetic_field
    frequencies = (2868.0, 2870.0, 2872.0)
    axis_body = (1.0, 0.0, 0.0)

    identity_response = simulate_attitude_aware_nv_response(
        environment=environment,
        nv_axis_body=axis_body,
        attitude_body_to_ned=Quaternion(1.0, 0.0, 0.0, 0.0),
        frequencies_mhz=frequencies,
    )

    half_sqrt = sqrt(0.5)

    rotated_response = simulate_attitude_aware_nv_response(
        environment=environment,
        nv_axis_body=axis_body,
        attitude_body_to_ned=Quaternion(
            half_sqrt, 0.0, 0.0, half_sqrt
        ),
        frequencies_mhz=frequencies,
    )

    assert identity_response.resonance.projected_field_nt == pytest.approx(
        magnetic_field.north_nt,
        abs=1e-8,
    )

    assert rotated_response.resonance.projected_field_nt == pytest.approx(
        magnetic_field.east_nt,
        abs=1e-8,
    )

    assert identity_response.resonance.projected_field_nt != pytest.approx(
        rotated_response.resonance.projected_field_nt
    )

    assert (
        identity_response.resonance.upper_mhz
        - identity_response.resonance.lower_mhz
    ) == pytest.approx(
        2.0
        * ELECTRON_GYROMAGNETIC_RATIO_MHZ_PER_T
        * abs(magnetic_field.north_nt)
        / 1e9
    )

    assert (
        rotated_response.resonance.upper_mhz
        - rotated_response.resonance.lower_mhz
    ) == pytest.approx(
        2.0
        * ELECTRON_GYROMAGNETIC_RATIO_MHZ_PER_T
        * abs(magnetic_field.east_nt)
        / 1e9
    )
