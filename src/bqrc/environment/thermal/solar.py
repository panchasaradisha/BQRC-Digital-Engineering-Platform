"""Solar-environment modelling for the BQRC thermal environment.

This module provides deterministic solar quantities required by the
BQRC space-environment simulator.  It represents the external solar
environment rather than the thermal response of a spacecraft component.

The initial implementation provides:

* approximate Earth-to-Sun direction in the ECI frame,
* approximate Earth-Sun distance,
* distance-corrected solar irradiance.

The solar-position approximation is intended for engineering simulation
and thermal-environment development.  Higher-fidelity ephemerides may
replace this implementation later without changing the public thermal
environment interface.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from math import (
    cos,
    isfinite,
    radians,
    sin,
    sqrt,
)

from bqrc.frames import ReferenceFrame, Vector3

ASTRONOMICAL_UNIT_M = 149_597_870_700.0

SOLAR_CONSTANT_W_M2 = 1361.0

J2000_JULIAN_DATE = 2_451_545.0


@dataclass(frozen=True, slots=True)
class SolarEnvironment:
    """Solar environment evaluated at one simulation timestamp.

    Parameters
    ----------
    timestamp:
        Time at which the solar environment is evaluated.
    earth_to_sun_unit:
        Unit vector from Earth toward the Sun in the ECI frame.
    earth_sun_distance_m:
        Approximate distance between Earth and Sun in metres.
    solar_irradiance_w_m2:
        Solar irradiance normal to the Sun direction at Earth's
        instantaneous orbital distance.
    """

    timestamp: datetime
    earth_to_sun_unit: Vector3
    earth_sun_distance_m: float
    solar_irradiance_w_m2: float

    def __post_init__(self) -> None:
        """Validate the solar-environment state."""

        if self.timestamp.tzinfo is None:
            raise ValueError(
                "solar timestamp must be timezone-aware"
            )

        if self.earth_to_sun_unit.frame != ReferenceFrame.ECI:
            raise ValueError(
                "Sun direction must use the ECI frame"
            )

        if self.earth_to_sun_unit.unit != "1":
            raise ValueError(
                "Sun direction must be dimensionless"
            )

        if (
            not isfinite(self.earth_sun_distance_m)
            or self.earth_sun_distance_m <= 0.0
        ):
            raise ValueError(
                "Earth-Sun distance must be finite and positive"
            )

        if (
            not isfinite(self.solar_irradiance_w_m2)
            or self.solar_irradiance_w_m2 <= 0.0
        ):
            raise ValueError(
                "solar irradiance must be finite and positive"
            )


def julian_date(timestamp: datetime) -> float:
    """Convert a timezone-aware datetime to Julian Date.

    Parameters
    ----------
    timestamp:
        Time to convert. The value may use any timezone but must be
        timezone-aware.

    Returns
    -------
    float
        Julian Date corresponding to the UTC timestamp.
    """

    if timestamp.tzinfo is None:
        raise ValueError(
            "timestamp must be timezone-aware"
        )

    timestamp_utc = timestamp.astimezone(UTC)

    year = timestamp_utc.year
    month = timestamp_utc.month

    day_fraction = (
        timestamp_utc.day
        + (
            timestamp_utc.hour
            + (
                timestamp_utc.minute
                + (
                    timestamp_utc.second
                    + timestamp_utc.microsecond / 1_000_000.0
                )
                / 60.0
            )
            / 60.0
        )
        / 24.0
    )

    if month <= 2:
        year -= 1
        month += 12

    century = year // 100

    correction = (
        2
        - century
        + century // 4
    )

    return (
        int(365.25 * (year + 4716))
        + int(30.6001 * (month + 1))
        + day_fraction
        + correction
        - 1524.5
    )


def _normalize_angle_deg(angle_deg: float) -> float:
    """Normalize an angle to the interval 0 <= angle < 360 degrees."""

    return angle_deg % 360.0


def evaluate_solar_environment(
    timestamp: datetime,
) -> SolarEnvironment:
    """Evaluate the approximate solar environment at a timestamp.

    The calculation uses a compact low-order solar-position model based
    on the number of days from the J2000 epoch.  The resulting apparent
    solar longitude and obliquity are converted into an Earth-centred
    equatorial direction suitable for the BQRC ECI environment model.

    Solar irradiance is adjusted using the inverse-square relationship
    with the estimated Earth-Sun distance.

    Parameters
    ----------
    timestamp:
        Time at which the solar environment is required.

    Returns
    -------
    SolarEnvironment
        Earth-to-Sun direction, Earth-Sun distance, and solar irradiance.
    """

    jd = julian_date(timestamp)

    days_since_j2000 = (
        jd - J2000_JULIAN_DATE
    )

    mean_longitude_deg = _normalize_angle_deg(
        280.460
        + 0.9856474 * days_since_j2000
    )

    mean_anomaly_deg = _normalize_angle_deg(
        357.528
        + 0.9856003 * days_since_j2000
    )

    mean_anomaly_rad = radians(
        mean_anomaly_deg
    )

    ecliptic_longitude_deg = _normalize_angle_deg(
        mean_longitude_deg
        + 1.915 * sin(mean_anomaly_rad)
        + 0.020 * sin(2.0 * mean_anomaly_rad)
    )

    obliquity_deg = (
        23.439
        - 0.0000004 * days_since_j2000
    )

    ecliptic_longitude_rad = radians(
        ecliptic_longitude_deg
    )

    obliquity_rad = radians(
        obliquity_deg
    )

    x = cos(
        ecliptic_longitude_rad
    )

    y = (
        cos(obliquity_rad)
        * sin(ecliptic_longitude_rad)
    )

    z = (
        sin(obliquity_rad)
        * sin(ecliptic_longitude_rad)
    )

    norm = sqrt(
        x * x
        + y * y
        + z * z
    )

    sun_direction = Vector3(
        x=x / norm,
        y=y / norm,
        z=z / norm,
        unit="1",
        frame=ReferenceFrame.ECI,
    )

    earth_sun_distance_au = (
        1.00014
        - 0.01671 * cos(mean_anomaly_rad)
        - 0.00014 * cos(
            2.0 * mean_anomaly_rad
        )
    )

    earth_sun_distance_m = (
        earth_sun_distance_au
        * ASTRONOMICAL_UNIT_M
    )

    solar_irradiance_w_m2 = (
        SOLAR_CONSTANT_W_M2
        / earth_sun_distance_au**2
    )

    return SolarEnvironment(
        timestamp=timestamp,
        earth_to_sun_unit=sun_direction,
        earth_sun_distance_m=earth_sun_distance_m,
        solar_irradiance_w_m2=solar_irradiance_w_m2,
    )