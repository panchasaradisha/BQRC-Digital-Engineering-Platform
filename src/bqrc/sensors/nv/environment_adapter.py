
"""Connect the BQRC magnetic environment to NV-center ODMR physics.

The environment magnetic field and NV axis must both use the
local geodetic North-East-Down (NED) coordinate frame.

Magnetic-field inputs are in nanotesla (nT).
Microwave frequencies are in megahertz (MHz).
Fluorescence is normalized and dimensionless.
"""

from __future__ import annotations

from dataclasses import dataclass

from bqrc.algorithms.odmr.spectrum import (
    ODMRSpectrum,
    simulate_odmr_spectrum,
)
from bqrc.environment.simulator import SpaceEnvironmentState
from bqrc.frames.attitude import Quaternion
from bqrc.sensors.nv.resonance import (
    NVResonance,
    calculate_nv_resonance,
)


@dataclass(frozen=True, slots=True)
class NVEnvironmentResponse:
    """Ideal NV resonance and ODMR response to an environment state."""

    resonance: NVResonance
    spectrum: ODMRSpectrum


def simulate_nv_environment_response(
    environment: SpaceEnvironmentState,
    nv_axis_ned: tuple[float, float, float],
    frequencies_mhz: tuple[float, ...],
    contrast: float = 0.1,
    linewidth_mhz: float = 1.0,
) -> NVEnvironmentResponse:
    """Simulate ideal ODMR response using an IGRF magnetic-field state.

    The NV-axis vector must be supplied in the local geodetic NED
    frame. This function does not transform spacecraft body-frame
    orientations into NED coordinates.
    """

    magnetic_field = environment.magnetic_field

    magnetic_field_ned_nt = (
        magnetic_field.north_nt,
        magnetic_field.east_nt,
        magnetic_field.down_nt,
    )

    resonance = calculate_nv_resonance(
        magnetic_field_nt=magnetic_field_ned_nt,
        nv_axis=nv_axis_ned,
    )

    spectrum = simulate_odmr_spectrum(
        resonance=resonance,
        frequencies_mhz=frequencies_mhz,
        contrast=contrast,
        linewidth_mhz=linewidth_mhz,
    )

    return NVEnvironmentResponse(
        resonance=resonance,
        spectrum=spectrum,
    )

def simulate_attitude_aware_nv_response(
    environment: SpaceEnvironmentState,
    nv_axis_body: tuple[float, float, float],
    attitude_body_to_ned: Quaternion,
    frequencies_mhz: tuple[float, ...],
    contrast: float = 0.1,
    linewidth_mhz: float = 1.0,
) -> NVEnvironmentResponse:
    """Simulate NV ODMR using spacecraft body-frame sensor orientation.

    The attitude quaternion actively rotates the body-frame NV axis
    into the local North-East-Down frame.

    The magnetic environment remains expressed in local NED.
    """

    nv_axis_ned = attitude_body_to_ned.rotate_components(nv_axis_body)

    return simulate_nv_environment_response(
        environment=environment,
        nv_axis_ned=nv_axis_ned,
        frequencies_mhz=frequencies_mhz,
        contrast=contrast,
        linewidth_mhz=linewidth_mhz,
    )
