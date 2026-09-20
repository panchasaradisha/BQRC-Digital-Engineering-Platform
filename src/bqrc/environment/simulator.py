"""Unified BQRC space-environment simulator.

This module coordinates the validated orbital, Earth-coordinate, and
geomagnetic environment models and exposes them through a single
environment-state interface.

Additional environment models such as microgravity, radiation, and
thermal conditions will be integrated through this orchestration layer
as they mature.
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
from bqrc.environment.orbit import OrbitalState
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
    """

    timestamp: datetime
    geodetic_position: GeodeticPosition
    igrf_epoch: float
    magnetic_field: GeodeticMagneticField

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
    """Coordinate BQRC space-environment models."""

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
        """Evaluate the environment for one orbital state."""

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

        return SpaceEnvironmentState(
            timestamp=orbital_state.timestamp,
            geodetic_position=geodetic_position,
            igrf_epoch=epoch,
            magnetic_field=magnetic_field,
        )