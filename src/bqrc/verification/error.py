"""Estimate-versus-truth verification.

This is the only place (besides the runner that feeds it) where truth
and estimates meet.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from bqrc.core.measurement import Measurement
from bqrc.sensors.nv.resonance import project_magnetic_field
from bqrc.simulation.truth import TruthState


@dataclass(frozen=True, slots=True)
class ErrorRecord:
    """Error of one field estimate against truth."""

    timestamp: datetime
    estimated_nt: float
    true_nt: float
    error_nt: float
    claimed_std_nt: float | None
    z_score: float | None
    fit_success: bool


def true_axis_field_magnitude_nt(
    truth: TruthState,
    nv_axis_body: tuple[float, float, float],
) -> float:
    """True unsigned field projection on the NV axis."""

    body = truth.sensor_stimulus().magnetic_field_body_nt
    return abs(project_magnetic_field(body, nv_axis_body))


def compute_error_record(
    measurement: Measurement,
    truth: TruthState,
    nv_axis_body: tuple[float, float, float],
) -> ErrorRecord:
    """Compare a field ``Measurement`` with truth."""

    true_nt = true_axis_field_magnitude_nt(truth, nv_axis_body)
    error = measurement.value - true_nt

    std = measurement.uncertainty.value if measurement.uncertainty else None
    z = error / std if std else None

    return ErrorRecord(
        timestamp=measurement.timestamp,
        estimated_nt=measurement.value,
        true_nt=true_nt,
        error_nt=error,
        claimed_std_nt=std,
        z_score=z,
        fit_success=bool(measurement.metadata.get("fit_success", False)),
    )
