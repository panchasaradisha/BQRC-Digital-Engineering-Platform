"""Thermal and radiative environment models for BQRC."""

from bqrc.environment.thermal.earth_flux import (
    EARTH_MEAN_ALBEDO,
    EARTH_MEAN_RADIUS_M,
    EARTH_SURFACE_IR_FLUX_W_M2,
    EarthRadiativeFlux,
    earth_view_factor,
    evaluate_earth_radiative_flux,
)
from bqrc.environment.thermal.eclipse import (
    EARTH_SHADOW_RADIUS_M,
    EclipseState,
    evaluate_earth_eclipse,
)
from bqrc.environment.thermal.model import (
    ThermalEnvironmentState,
    evaluate_thermal_environment,
)
from bqrc.environment.thermal.solar import (
    ASTRONOMICAL_UNIT_M,
    SOLAR_CONSTANT_W_M2,
    SolarEnvironment,
    evaluate_solar_environment,
    julian_date,
)

__all__ = [
    "ASTRONOMICAL_UNIT_M",
    "EARTH_MEAN_ALBEDO",
    "EARTH_MEAN_RADIUS_M",
    "EARTH_SHADOW_RADIUS_M",
    "EARTH_SURFACE_IR_FLUX_W_M2",
    "SOLAR_CONSTANT_W_M2",
    "EarthRadiativeFlux",
    "EclipseState",
    "SolarEnvironment",
    "ThermalEnvironmentState",
    "earth_view_factor",
    "evaluate_earth_radiative_flux",
    "evaluate_earth_eclipse",
    "evaluate_solar_environment",
    "evaluate_thermal_environment",
    "julian_date",
]