
"""First-order axial NV-center magnetic resonance model.

Magnetic-field inputs are in nanotesla (nT).
Resonance-frequency outputs are in megahertz (MHz).

This model neglects transverse-field mixing, strain,
hyperfine interactions, and temperature dependence.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt

from bqrc.core.constants import (
    ELECTRON_GYROMAGNETIC_RATIO_MHZ_PER_T,
    NANOTESLA_PER_TESLA,
    ZERO_FIELD_SPLITTING_MHZ,
)


@dataclass(frozen=True)
class NVResonance:
    """Two first-order NV-center resonance frequencies."""

    lower_mhz: float
    upper_mhz: float
    projected_field_nt: float


def _validate_vector(
    vector: tuple[float, float, float],
    name: str,
) -> None:
    """Require a finite three-component vector."""
    if len(vector) != 3 or not all(isfinite(x) for x in vector):
        raise ValueError(f"{name} must contain three finite components")


def project_magnetic_field(
    magnetic_field_nt: tuple[float, float, float],
    nv_axis: tuple[float, float, float],
) -> float:
    """Project a magnetic field onto a normalized NV axis.

    Both vectors must be expressed in the same coordinate frame.
    """

    _validate_vector(magnetic_field_nt, "magnetic_field_nt")
    _validate_vector(nv_axis, "nv_axis")

    axis_norm = sqrt(sum(component**2 for component in nv_axis))

    if not isfinite(axis_norm) or axis_norm == 0.0:
        raise ValueError("nv_axis must have a finite nonzero norm")

    normalized_axis = tuple(
        component / axis_norm for component in nv_axis
    )

    return sum(
        field_component * axis_component
        for field_component, axis_component in zip(
            magnetic_field_nt,
            normalized_axis,
            strict=True,
        )
    )


def calculate_nv_resonance(
    magnetic_field_nt: tuple[float, float, float],
    nv_axis: tuple[float, float, float],
    zero_field_splitting_mhz: float = ZERO_FIELD_SPLITTING_MHZ,
) -> NVResonance:
    """Calculate axial NV-center ODMR transition frequencies.

    The returned frequencies are sorted in ascending order.
    The signed projected magnetic field is preserved separately.
    """

    if (
        not isfinite(zero_field_splitting_mhz)
        or zero_field_splitting_mhz <= 0.0
    ):
        raise ValueError(
            "zero_field_splitting_mhz must be finite and positive"
        )

    projected_field_nt = project_magnetic_field(
        magnetic_field_nt=magnetic_field_nt,
        nv_axis=nv_axis,
    )

    zeeman_shift_mhz = (
        ELECTRON_GYROMAGNETIC_RATIO_MHZ_PER_T
        * projected_field_nt
        / NANOTESLA_PER_TESLA
    )

    frequency_a = zero_field_splitting_mhz - zeeman_shift_mhz
    frequency_b = zero_field_splitting_mhz + zeeman_shift_mhz

    return NVResonance(
        lower_mhz=min(frequency_a, frequency_b),
        upper_mhz=max(frequency_a, frequency_b),
        projected_field_nt=projected_field_nt,
    )
