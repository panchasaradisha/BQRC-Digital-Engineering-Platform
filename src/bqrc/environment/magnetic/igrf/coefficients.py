"""Data models for International Geomagnetic Reference Field coefficients."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite


class CoefficientKind(StrEnum):
    """Supported IGRF Gauss coefficient families."""

    G = "g"
    H = "h"


@dataclass(frozen=True, slots=True)
class IGRFCoefficient:
    """One spherical-harmonic Gauss coefficient at a specific epoch.

    Parameters
    ----------
    kind:
        Gauss coefficient family: ``g`` or ``h``.
    degree:
        Spherical-harmonic degree n.
    order:
        Spherical-harmonic order m.
    epoch:
        Decimal-year epoch represented by the coefficient.
    value_nt:
        Main-field coefficient value in nanotesla.
    secular_variation_nt_per_year:
        Optional secular variation in nanotesla per year.
    """

    kind: CoefficientKind
    degree: int
    order: int
    epoch: float
    value_nt: float
    secular_variation_nt_per_year: float | None = None

    def __post_init__(self) -> None:
        """Validate the scientific structure of the coefficient."""

        if isinstance(self.degree, bool) or not isinstance(self.degree, int):
            raise TypeError("degree must be an integer")

        if isinstance(self.order, bool) or not isinstance(self.order, int):
            raise TypeError("order must be an integer")

        if self.degree < 1:
            raise ValueError("degree must be at least 1")

        if self.order < 0:
            raise ValueError("order must be non-negative")

        if self.order > self.degree:
            raise ValueError("order cannot exceed degree")

        if not isfinite(self.epoch):
            raise ValueError("epoch must be finite")

        if not isfinite(self.value_nt):
            raise ValueError("coefficient value must be finite")

        if (
            self.secular_variation_nt_per_year is not None
            and not isfinite(self.secular_variation_nt_per_year)
        ):
            raise ValueError("secular variation must be finite when provided")

        if self.kind is CoefficientKind.H and self.order == 0:
            raise ValueError("h coefficients require order greater than zero")

    @property
    def key(self) -> tuple[CoefficientKind, int, int]:
        """Return the coefficient identity independent of epoch."""

        return self.kind, self.degree, self.order


@dataclass(frozen=True, slots=True)
class IGRFCoefficientSet:
    """Collection of IGRF coefficients representing one model epoch."""

    model: str
    epoch: float
    maximum_degree: int
    coefficients: tuple[IGRFCoefficient, ...]

    def __post_init__(self) -> None:
        """Validate the coefficient collection."""

        if not self.model.strip():
            raise ValueError("model name must not be empty")

        if not isfinite(self.epoch):
            raise ValueError("epoch must be finite")

        if (
            isinstance(self.maximum_degree, bool)
            or not isinstance(self.maximum_degree, int)
        ):
            raise TypeError("maximum_degree must be an integer")

        if self.maximum_degree < 1:
            raise ValueError("maximum_degree must be at least 1")

        if not self.coefficients:
            raise ValueError("coefficient set must not be empty")

        seen: set[tuple[CoefficientKind, int, int]] = set()

        for coefficient in self.coefficients:
            if coefficient.epoch != self.epoch:
                raise ValueError(
                    "all coefficients must use the coefficient-set epoch"
                )

            if coefficient.degree > self.maximum_degree:
                raise ValueError(
                    "coefficient degree exceeds maximum_degree"
                )

            if coefficient.key in seen:
                raise ValueError(
                    f"duplicate coefficient detected: {coefficient.key}"
                )

            seen.add(coefficient.key)

    def get(
        self,
        kind: CoefficientKind,
        degree: int,
        order: int,
    ) -> IGRFCoefficient:
        """Return a coefficient identified by kind, degree, and order."""

        target = (kind, degree, order)

        for coefficient in self.coefficients:
            if coefficient.key == target:
                return coefficient

        raise KeyError(
            f"coefficient not found: {kind.value}({degree}, {order})"
        )