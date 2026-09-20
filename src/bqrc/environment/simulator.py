"""Unified BQRC space-environment simulator.

This module coordinates the validated BQRC environment models and
exposes them through a single environment-state interface.

The unified environment currently includes:

- orbital state to WGS-84 Earth location,
- IGRF-14 geomagnetic field,
- residual microgravity,
- solar environment,
- Earth eclipse state,
- Earth infrared radiation,
- Earth albedo radiation.

Additional environment models such as radiation will be integrated
through this orchestration layer as they mature.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from math import isfinite
from pathlib import Path

from bqrc.environment.earth import ecef_to_geodetic
from bqrc.environment.earth.geodetic import GeodeticPosition
from bqrc.environment.magnetic.igrf.coefficients import (
    IGRFCoefficientSet,
)
from bqrc.environment.magnetic.igrf.components import (
    GeodeticMagneticField,
    spherical_to_geodetic_ned,
)
from bqrc.environment.magnetic.igrf.coordinates import (
    geodetic_to_igrf_spherical,
)
from bqrc.environment.magnetic.igrf.field import (
    evaluate_igrf_spherical,
)
from bqrc.environment.magnetic.igrf.parser import (
    load_igrf14_2025,
)
from bqrc.environment.magnetic.igrf.temporal import (
    predict_igrf14_coefficients,
)
from bqrc.environment.microgravity import (
    MicrogravityModel,
    MicrogravityState,
)
from bqrc.environment.orbit import OrbitalState
from bqrc.environment.thermal import (
    ThermalEnvironmentState,
    evaluate_thermal_environment,
)
from bqrc.frames import eci_to_ecef


@dataclass(frozen=True, slots=True)
class SpaceEnvironmentState:
    """Environment conditions corresponding to one orbital state.

    Parameters
    ----------
    timestamp:
        UTC simulation timestamp.
    geodetic_position:
        Spacecraft WGS-84 latitude, longitude, and altitude.
    igrf_epoch:
        Decimal-year epoch used for IGRF evaluation.
    magnetic_field:
        Local geomagnetic field in the geodetic North-East-Down frame.
    microgravity:
        Residual microgravity state in the ECI frame.
    thermal:
        Solar, eclipse, Earth infrared, and Earth albedo environment.
    """

    timestamp: datetime
    geodetic_position: GeodeticPosition
    igrf_epoch: float
    magnetic_field: GeodeticMagneticField
    microgravity: MicrogravityState
    thermal: ThermalEnvironmentState

    def __post_init__(self) -> None:
        """Validate basic environment-state invariants."""

        if self.timestamp.tzinfo is None:
            raise ValueError(
                "environment timestamp must be timezone-aware"
            )

        if not isfinite(self.igrf_epoch):
            raise ValueError(
                "IGRF epoch must be finite"
            )


def datetime_to_decimal_year(timestamp: datetime) -> float:
    """Convert a timezone-aware timestamp to decimal year."""

    if timestamp.tzinfo is None:
        raise ValueError(
            "timestamp must be timezone-aware"
        )

    timestamp_utc = timestamp.astimezone(UTC)

    start = datetime(
        timestamp_utc.year,
        1,
        1,
        tzinfo=UTC,
    )

    end = datetime(
        timestamp_utc.year + 1,
        1,
        1,
        tzinfo=UTC,
    )

    elapsed_seconds = (
        timestamp_utc - start
    ).total_seconds()

    year_seconds = (
        end - start
    ).total_seconds()

    return (
        timestamp_utc.year
        + elapsed_seconds / year_seconds
    )


class SpaceEnvironmentSimulator:
    """Coordinate the unified BQRC space-environment models."""

    def __init__(
        self,
        igrf_base_coefficients: IGRFCoefficientSet,
    ) -> None:
        """Create a simulator from validated IGRF base coefficients."""

        if igrf_base_coefficients.model != "IGRF-14":
            raise ValueError(
                "space environment simulator requires IGRF-14"
            )

        if igrf_base_coefficients.epoch != 2025.0:
            raise ValueError(
                "IGRF base coefficients must represent epoch 2025.0"
            )

        self._igrf_base_coefficients = (
            igrf_base_coefficients
        )

        self._microgravity_model = MicrogravityModel()

    @classmethod
    def from_igrf14_dataset(
        cls,
        dataset: Path,
    ) -> SpaceEnvironmentSimulator:
        """Create a simulator directly from the IGRF-14 dataset."""

        coefficients = load_igrf14_2025(
            dataset
        )

        return cls(
            igrf_base_coefficients=coefficients
        )

    def evaluate(
        self,
        orbital_state: OrbitalState,
    ) -> SpaceEnvironmentState:
        """Evaluate all integrated environment models for one state."""

        ecef_position = eci_to_ecef(
            orbital_state.position,
            orbital_state.timestamp,
        )

        geodetic_position = ecef_to_geodetic(
            ecef_position
        )

        epoch = datetime_to_decimal_year(
            orbital_state.timestamp
        )

        coefficients = predict_igrf14_coefficients(
            base=self._igrf_base_coefficients,
            epoch=epoch,
        )

        spherical_position = (
            geodetic_to_igrf_spherical(
                geodetic_position
            )
        )

        spherical_field = evaluate_igrf_spherical(
            coefficients=coefficients,
            position=spherical_position,
        )

        magnetic_field = spherical_to_geodetic_ned(
            field=spherical_field,
            geodetic_position=geodetic_position,
            spherical_position=spherical_position,
        )

        microgravity = self._microgravity_model.evaluate(
            orbital_state
        )

        thermal = evaluate_thermal_environment(
            timestamp=orbital_state.timestamp,
            spacecraft_position=orbital_state.position,
            altitude_m=geodetic_position.altitude_m,
        )

        return SpaceEnvironmentState(
            timestamp=orbital_state.timestamp,
            geodetic_position=geodetic_position,
            igrf_epoch=epoch,
            magnetic_field=magnetic_field,
            microgravity=microgravity,
            thermal=thermal,
        )