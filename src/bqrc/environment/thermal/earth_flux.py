"""Earth-originating radiative flux models for the BQRC environment.

This module provides engineering-level models for:

1. Earth thermal infrared radiation.
2. Reflected solar radiation (albedo).

These quantities represent environmental radiative inputs at spacecraft
altitude. They are not spacecraft temperatures or absorbed component
heat loads.

Higher-fidelity angular, geographic, seasonal, and cloud-dependent
models can later replace these approximations while preserving the
public thermal-environment interface.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

EARTH_MEAN_RADIUS_M = 6_371_000.0

EARTH_SURFACE_IR_FLUX_W_M2 = 237.0

EARTH_MEAN_ALBEDO = 0.30


@dataclass(frozen=True, slots=True)
class EarthRadiativeFlux:
    """Earth-originating radiative environment at spacecraft altitude.

    Parameters
    ----------
    infrared_flux_w_m2:
        Approximate Earth thermal-infrared flux at spacecraft altitude.
    albedo_flux_w_m2:
        Approximate reflected solar flux at spacecraft altitude.
    earth_view_factor:
        Engineering geometric dilution factor used by the model.
    """

    infrared_flux_w_m2: float
    albedo_flux_w_m2: float
    earth_view_factor: float

    def __post_init__(self) -> None:
        """Validate Earth radiative-flux quantities."""

        for value in (
            self.infrared_flux_w_m2,
            self.albedo_flux_w_m2,
            self.earth_view_factor,
        ):
            if not isfinite(value):
                raise ValueError(
                    "Earth radiative-flux values must be finite"
                )

        if self.infrared_flux_w_m2 < 0.0:
            raise ValueError(
                "infrared flux cannot be negative"
            )

        if self.albedo_flux_w_m2 < 0.0:
            raise ValueError(
                "albedo flux cannot be negative"
            )

        if not 0.0 <= self.earth_view_factor <= 1.0:
            raise ValueError(
                "Earth view factor must be between 0 and 1"
            )


def earth_view_factor(
    altitude_m: float,
) -> float:
    """Return engineering geometric dilution with spacecraft altitude.

    The current model uses the squared Earth-radius ratio

        (R_E / (R_E + h))^2

    as a deterministic first-order approximation.

    Parameters
    ----------
    altitude_m:
        Spacecraft altitude above the Earth reference surface.

    Returns
    -------
    float
        Dimensionless geometric factor between zero and one.
    """

    if not isfinite(altitude_m):
        raise ValueError(
            "altitude must be finite"
        )

    if altitude_m < 0.0:
        raise ValueError(
            "altitude cannot be negative"
        )

    orbital_radius_m = (
        EARTH_MEAN_RADIUS_M + altitude_m
    )

    return (
        EARTH_MEAN_RADIUS_M
        / orbital_radius_m
    ) ** 2


def evaluate_earth_radiative_flux(
    altitude_m: float,
    solar_irradiance_w_m2: float,
    sunlight_fraction: float,
) -> EarthRadiativeFlux:
    """Evaluate Earth IR and reflected-solar environmental flux.

    Parameters
    ----------
    altitude_m:
        Spacecraft altitude above Earth in metres.
    solar_irradiance_w_m2:
        Solar irradiance at the Earth-spacecraft system.
    sunlight_fraction:
        Direct-solar illumination fraction from the eclipse model.

    Returns
    -------
    EarthRadiativeFlux
        Approximate Earth IR and albedo fluxes.
    """

    if not isfinite(solar_irradiance_w_m2):
        raise ValueError(
            "solar irradiance must be finite"
        )

    if solar_irradiance_w_m2 < 0.0:
        raise ValueError(
            "solar irradiance cannot be negative"
        )

    if not isfinite(sunlight_fraction):
        raise ValueError(
            "sunlight fraction must be finite"
        )

    if not 0.0 <= sunlight_fraction <= 1.0:
        raise ValueError(
            "sunlight fraction must be between 0 and 1"
        )

    view_factor = earth_view_factor(
        altitude_m
    )

    infrared_flux_w_m2 = (
        EARTH_SURFACE_IR_FLUX_W_M2
        * view_factor
    )

    albedo_flux_w_m2 = (
        solar_irradiance_w_m2
        * EARTH_MEAN_ALBEDO
        * view_factor
        * sunlight_fraction
    )

    return EarthRadiativeFlux(
        infrared_flux_w_m2=infrared_flux_w_m2,
        albedo_flux_w_m2=albedo_flux_w_m2,
        earth_view_factor=view_factor,
    )