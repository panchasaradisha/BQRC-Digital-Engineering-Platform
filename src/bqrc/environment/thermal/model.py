"""Unified thermal-radiative environment model for BQRC."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite

from bqrc.environment.thermal.earth_flux import (
    EarthRadiativeFlux,
    evaluate_earth_radiative_flux,
)
from bqrc.environment.thermal.eclipse import (
    EclipseState,
    evaluate_earth_eclipse,
)
from bqrc.environment.thermal.solar import (
    SolarEnvironment,
    evaluate_solar_environment,
)
from bqrc.frames import Vector3


@dataclass(frozen=True, slots=True)
class ThermalEnvironmentState:
    """Combined radiative thermal environment for one spacecraft state.

    Parameters
    ----------
    solar:
        Solar geometry and irradiance.
    eclipse:
        Earth occultation and direct-sunlight fraction.
    earth_flux:
        Earth infrared and reflected-solar radiation.
    direct_solar_flux_w_m2:
        Direct solar irradiance remaining after Earth occultation.
    """

    solar: SolarEnvironment
    eclipse: EclipseState
    earth_flux: EarthRadiativeFlux
    direct_solar_flux_w_m2: float

    def __post_init__(self) -> None:
        """Validate combined thermal-environment quantities."""

        if not isfinite(
            self.direct_solar_flux_w_m2
        ):
            raise ValueError(
                "direct solar flux must be finite"
            )

        if self.direct_solar_flux_w_m2 < 0.0:
            raise ValueError(
                "direct solar flux cannot be negative"
            )


def evaluate_thermal_environment(
    timestamp: datetime,
    spacecraft_position: Vector3,
    altitude_m: float,
) -> ThermalEnvironmentState:
    """Evaluate the BQRC radiative thermal environment.

    Parameters
    ----------
    timestamp:
        Time of the spacecraft state.
    spacecraft_position:
        Spacecraft Earth-centred position used for eclipse geometry.
    altitude_m:
        WGS-84 spacecraft altitude in metres.

    Returns
    -------
    ThermalEnvironmentState
        Solar, eclipse, Earth IR, and albedo conditions.
    """

    solar = evaluate_solar_environment(
        timestamp
    )

    eclipse = evaluate_earth_eclipse(
        spacecraft_position=spacecraft_position,
        earth_to_sun_unit=solar.earth_to_sun_unit,
    )

    direct_solar_flux_w_m2 = (
        solar.solar_irradiance_w_m2
        * eclipse.sunlight_fraction
    )

    earth_flux = evaluate_earth_radiative_flux(
        altitude_m=altitude_m,
        solar_irradiance_w_m2=solar.solar_irradiance_w_m2,
        sunlight_fraction=eclipse.sunlight_fraction,
    )

    return ThermalEnvironmentState(
        solar=solar,
        eclipse=eclipse,
        earth_flux=earth_flux,
        direct_solar_flux_w_m2=direct_solar_flux_w_m2,
    )
