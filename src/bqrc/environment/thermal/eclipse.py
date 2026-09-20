"""Earth-shadow and eclipse geometry for the BQRC thermal environment.

This module determines whether a spacecraft is illuminated by direct
sunlight or occulted by Earth.

The first BQRC implementation uses a cylindrical Earth-shadow model.
This is deterministic, inexpensive, and suitable for the current
engineering environment simulator. A higher-fidelity conical
umbra/penumbra model may replace it later without changing the public
thermal-environment interface.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt

from bqrc.frames import ReferenceFrame, Vector3

EARTH_SHADOW_RADIUS_M = 6_378_137.0


@dataclass(frozen=True, slots=True)
class EclipseState:
    """Direct-solar-illumination state for a spacecraft.

    Parameters
    ----------
    in_eclipse:
        True when Earth blocks direct sunlight.
    sunlight_fraction:
        Fraction of direct solar irradiance reaching the spacecraft.
        The current cylindrical model produces either 0.0 or 1.0.
    axial_distance_m:
        Signed spacecraft distance along the Earth-to-Sun axis.
        Negative values indicate the anti-solar side of Earth.
    shadow_axis_distance_m:
        Perpendicular distance from the spacecraft to the
        Earth-Sun shadow axis.
    """

    in_eclipse: bool
    sunlight_fraction: float
    axial_distance_m: float
    shadow_axis_distance_m: float

    def __post_init__(self) -> None:
        """Validate eclipse-state quantities."""

        if not isfinite(self.sunlight_fraction):
            raise ValueError(
                "sunlight fraction must be finite"
            )

        if not 0.0 <= self.sunlight_fraction <= 1.0:
            raise ValueError(
                "sunlight fraction must be between 0 and 1"
            )

        if not isfinite(self.axial_distance_m):
            raise ValueError(
                "axial distance must be finite"
            )

        if not isfinite(self.shadow_axis_distance_m):
            raise ValueError(
                "shadow-axis distance must be finite"
            )

        if self.shadow_axis_distance_m < 0.0:
            raise ValueError(
                "shadow-axis distance cannot be negative"
            )


def evaluate_earth_eclipse(
    spacecraft_position: Vector3,
    earth_to_sun_unit: Vector3,
) -> EclipseState:
    """Evaluate Earth occultation using a cylindrical shadow model.

    Parameters
    ----------
    spacecraft_position:
        Spacecraft position relative to Earth's centre in ECI metres.
    earth_to_sun_unit:
        Unit vector pointing from Earth toward the Sun in ECI.

    Returns
    -------
    EclipseState
        Binary direct-sunlight state and diagnostic shadow geometry.
    """

    if spacecraft_position.frame != ReferenceFrame.ECI:
        raise ValueError(
            "spacecraft position must use the ECI frame"
        )

    if spacecraft_position.unit != "m":
        raise ValueError(
            "spacecraft position must use metres"
        )

    if earth_to_sun_unit.frame != ReferenceFrame.ECI:
        raise ValueError(
            "Sun direction must use the ECI frame"
        )

    if earth_to_sun_unit.unit != "1":
        raise ValueError(
            "Sun direction must be dimensionless"
        )

    sun_norm = sqrt(
        earth_to_sun_unit.x**2
        + earth_to_sun_unit.y**2
        + earth_to_sun_unit.z**2
    )

    if sun_norm <= 0.0:
        raise ValueError(
            "Sun direction must have non-zero magnitude"
        )

    sun_x = earth_to_sun_unit.x / sun_norm
    sun_y = earth_to_sun_unit.y / sun_norm
    sun_z = earth_to_sun_unit.z / sun_norm

    axial_distance_m = (
        spacecraft_position.x * sun_x
        + spacecraft_position.y * sun_y
        + spacecraft_position.z * sun_z
    )

    radial_squared_m2 = (
        spacecraft_position.x**2
        + spacecraft_position.y**2
        + spacecraft_position.z**2
    )

    perpendicular_squared_m2 = max(
        0.0,
        radial_squared_m2
        - axial_distance_m**2,
    )

    shadow_axis_distance_m = sqrt(
        perpendicular_squared_m2
    )

    in_eclipse = (
        axial_distance_m < 0.0
        and shadow_axis_distance_m
        < EARTH_SHADOW_RADIUS_M
    )

    sunlight_fraction = (
        0.0 if in_eclipse else 1.0
    )

    return EclipseState(
        in_eclipse=in_eclipse,
        sunlight_fraction=sunlight_fraction,
        axial_distance_m=axial_distance_m,
        shadow_axis_distance_m=shadow_axis_distance_m,
    )