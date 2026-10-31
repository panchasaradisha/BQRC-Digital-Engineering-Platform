"""Raw (L1) NV ODMR acquisition."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from bqrc.core.provenance import DataSource


@dataclass(frozen=True, slots=True)
class ODMRAcquisition:
    """One raw ODMR sweep as the electronics would deliver it.

    This is the *only* thing the estimator receives. It contains photon
    counts and acquisition metadata; it does not contain the ideal
    spectrum, the true field, or any other simulation truth.

    ``reference_photon_count`` is the off-resonance count scale used to
    normalize fluorescence. Treat it as acquisition metadata (a measured
    baseline), not as truth.
    """

    sensor_id: str
    timestamp: datetime
    frequencies_mhz: tuple[float, ...]
    photon_counts: tuple[int, ...]
    reference_photon_count: float
    model_version: str
    configuration_id: str | None = None
    data_source: DataSource = DataSource.SIMULATED_SENSOR

    def __post_init__(self) -> None:
        if len(self.frequencies_mhz) != len(self.photon_counts):
            raise ValueError("frequencies and photon counts must have equal length")

        if self.timestamp.tzinfo is None:
            raise ValueError("acquisition timestamp must be timezone-aware")

        if self.reference_photon_count <= 0.0:
            raise ValueError("reference_photon_count must be positive")

    @property
    def fluorescence(self) -> tuple[float, ...]:
        """Normalized fluorescence (counts / reference count)."""

        return tuple(c / self.reference_photon_count for c in self.photon_counts)
