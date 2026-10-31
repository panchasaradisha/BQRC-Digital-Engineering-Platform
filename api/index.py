"""Size-conscious Vercel ASGI endpoint for the BQRC dashboard.

The main research backend uses SciPy for nonlinear least-squares fitting. Vercel's
serverless bundle limit cannot accommodate that complete scientific environment,
so this deployment entry point implements the same declared one-parameter ODMR
model with a deterministic NumPy grid search and golden-section refinement.
It receives photon observations—not hidden truth—during estimation.
"""

from __future__ import annotations

from math import isfinite, sqrt
from typing import Annotated

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

ZERO_FIELD_SPLITTING_MHZ = 2870.0
ELECTRON_GYROMAGNETIC_RATIO_MHZ_PER_T = 28_024.95
NANOTESLA_PER_TESLA = 1_000_000_000.0
GAMMA_MHZ_PER_NT = (
    ELECTRON_GYROMAGNETIC_RATIO_MHZ_PER_T / NANOTESLA_PER_TESLA
)

FiniteFloat = Annotated[float, Field(allow_inf_nan=False)]
PositiveFiniteFloat = Annotated[float, Field(gt=0.0, allow_inf_nan=False)]
Vector3 = tuple[FiniteFloat, FiniteFloat, FiniteFloat]

app = FastAPI(
    title="BQRC Digital Engineering Platform API",
    description="Serverless NV ODMR measurement endpoint for the BQRC dashboard.",
    version="0.1.0-vercel",
)


class NVMeasurementRequest(BaseModel):
    """Validated inputs for the public dashboard measurement workflow."""

    magnetic_field_nt: Vector3
    nv_axis: Vector3
    frequencies_mhz: list[FiniteFloat] = Field(min_length=5, max_length=5000)
    contrast: FiniteFloat = Field(default=0.1, gt=0.0, le=0.5)
    linewidth_mhz: PositiveFiniteFloat = 1.0
    reference_photon_count: PositiveFiniteFloat = Field(
        default=100_000.0,
        le=1e12,
    )
    seed: int | None = Field(default=42, ge=0, le=2**32 - 1)
    zero_field_splitting_mhz: PositiveFiniteFloat = ZERO_FIELD_SPLITTING_MHZ

    @field_validator("nv_axis")
    @classmethod
    def validate_nv_axis(cls, value: Vector3) -> Vector3:
        if all(component == 0.0 for component in value):
            raise ValueError("nv_axis must have nonzero magnitude")
        return value


class NVSimulationResponse(BaseModel):
    frequencies_mhz: list[float]
    ideal_fluorescence: list[float]
    measured_fluorescence: list[float]
    photon_counts: list[int]
    reference_photon_count: float
    lower_mhz: float
    upper_mhz: float
    projected_field_nt: float


class NVFieldEstimationResponse(BaseModel):
    lower_mhz: float
    upper_mhz: float
    projected_field_magnitude_nt: float
    residual_rmse: float
    fit_success: bool


class NVFieldUncertaintyResponse(BaseModel):
    fisher_information_per_nt_squared: float
    crlb_std_nt: float | None
    identifiable_locally: bool


class NVMeasurementResponse(BaseModel):
    simulation: NVSimulationResponse
    estimation: NVFieldEstimationResponse | None
    uncertainty: NVFieldUncertaintyResponse | None
    fit_success: bool


def _project_field(
    magnetic_field_nt: Vector3,
    nv_axis: Vector3,
) -> float:
    norm = sqrt(sum(component**2 for component in nv_axis))
    if not isfinite(norm) or norm == 0.0:
        raise ValueError("nv_axis must have a finite nonzero norm")
    return sum(
        field * axis / norm
        for field, axis in zip(magnetic_field_nt, nv_axis, strict=True)
    )


def _spectrum(
    frequencies: np.ndarray,
    splitting_mhz: float,
    contrast: float,
    linewidth_mhz: float,
    center_mhz: float,
) -> np.ndarray:
    half_width = linewidth_mhz / 2.0
    lower = center_mhz - splitting_mhz
    upper = center_mhz + splitting_mhz
    lower_dip = 1.0 / (1.0 + ((frequencies - lower) / half_width) ** 2)
    upper_dip = 1.0 / (1.0 + ((frequencies - upper) / half_width) ** 2)
    return 1.0 - contrast * (lower_dip + upper_dip)


def _fit_splitting(
    frequencies: np.ndarray,
    measured: np.ndarray,
    contrast: float,
    linewidth_mhz: float,
    center_mhz: float,
) -> tuple[float, float]:
    """Fit one unsigned splitting without access to the simulated truth value."""

    max_splitting = float(
        max(center_mhz - frequencies.min(), frequencies.max() - center_mhz)
    )
    if max_splitting <= 0.0:
        raise ValueError("frequency grid has insufficient span")

    def objective(splitting: float) -> float:
        residual = (
            _spectrum(
                frequencies,
                splitting,
                contrast,
                linewidth_mhz,
                center_mhz,
            )
            - measured
        )
        return float(np.mean(residual**2))

    coarse = np.linspace(0.0, max_splitting, num=801)
    losses = np.asarray([objective(float(value)) for value in coarse])
    best_index = int(np.argmin(losses))
    step = max_splitting / 800.0
    left = max(0.0, float(coarse[best_index]) - 2.0 * step)
    right = min(max_splitting, float(coarse[best_index]) + 2.0 * step)

    golden_ratio = (sqrt(5.0) - 1.0) / 2.0
    x1 = right - golden_ratio * (right - left)
    x2 = left + golden_ratio * (right - left)
    f1 = objective(x1)
    f2 = objective(x2)

    for _ in range(72):
        if f1 <= f2:
            right = x2
            x2 = x1
            f2 = f1
            x1 = right - golden_ratio * (right - left)
            f1 = objective(x1)
        else:
            left = x1
            x1 = x2
            f1 = f2
            x2 = left + golden_ratio * (right - left)
            f2 = objective(x2)

    fitted_splitting = (left + right) / 2.0
    return fitted_splitting, sqrt(objective(fitted_splitting))


def _field_uncertainty(
    frequencies: np.ndarray,
    field_magnitude_nt: float,
    reference_photon_count: float,
    contrast: float,
    linewidth_mhz: float,
    center_mhz: float,
) -> NVFieldUncertaintyResponse:
    splitting = GAMMA_MHZ_PER_NT * field_magnitude_nt
    lower = center_mhz - splitting
    upper = center_mhz + splitting
    half_width = linewidth_mhz / 2.0
    information = 0.0

    for frequency in frequencies:
        lower_offset = (float(frequency) - lower) / half_width
        upper_offset = (float(frequency) - upper) / half_width
        lower_line = 1.0 / (1.0 + lower_offset**2)
        upper_line = 1.0 / (1.0 + upper_offset**2)
        fluorescence = 1.0 - contrast * (lower_line + upper_line)
        lower_derivative = 2.0 * lower_offset / (
            half_width * (1.0 + lower_offset**2) ** 2
        )
        upper_derivative = 2.0 * upper_offset / (
            half_width * (1.0 + upper_offset**2) ** 2
        )
        fluorescence_derivative = (
            contrast
            * GAMMA_MHZ_PER_NT
            * (lower_derivative - upper_derivative)
        )
        if fluorescence > 0.0:
            information += (
                reference_photon_count
                * fluorescence_derivative**2
                / fluorescence
            )

    identifiable = information > 0.0 and isfinite(information)
    return NVFieldUncertaintyResponse(
        fisher_information_per_nt_squared=information if identifiable else 0.0,
        crlb_std_nt=(1.0 / sqrt(information)) if identifiable else None,
        identifiable_locally=identifiable,
    )


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "bqrc-api-vercel",
        "version": app.version,
    }


@app.post("/", response_model=NVMeasurementResponse)
@app.post("/api/index", response_model=NVMeasurementResponse)
@app.post("/api/v1/nv/odmr/measurement", response_model=NVMeasurementResponse)
def run_nv_measurement(request: NVMeasurementRequest) -> NVMeasurementResponse:
    frequencies = np.asarray(request.frequencies_mhz, dtype=float)
    center = request.zero_field_splitting_mhz
    if not frequencies.min() < center < frequencies.max():
        raise HTTPException(
            status_code=422,
            detail="frequency grid must span the zero-field splitting",
        )

    try:
        projected_field = _project_field(request.magnetic_field_nt, request.nv_axis)
        true_splitting = abs(projected_field) * GAMMA_MHZ_PER_NT
        ideal = _spectrum(
            frequencies,
            true_splitting,
            request.contrast,
            request.linewidth_mhz,
            center,
        )
        expected_counts = ideal * request.reference_photon_count
        if np.any(expected_counts > 1e15):
            raise ValueError("expected photon counts exceed supported range")
        photon_counts_array = np.random.default_rng(request.seed).poisson(
            expected_counts
        )
        measured = photon_counts_array / request.reference_photon_count
        fitted_splitting, residual_rmse = _fit_splitting(
            frequencies,
            measured,
            request.contrast,
            request.linewidth_mhz,
            center,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    lower = center - true_splitting
    upper = center + true_splitting
    field_magnitude = fitted_splitting / GAMMA_MHZ_PER_NT
    fitted_lower = center - fitted_splitting
    fitted_upper = center + fitted_splitting
    uncertainty = _field_uncertainty(
        frequencies,
        field_magnitude,
        request.reference_photon_count,
        request.contrast,
        request.linewidth_mhz,
        center,
    )

    return NVMeasurementResponse(
        simulation=NVSimulationResponse(
            frequencies_mhz=frequencies.tolist(),
            ideal_fluorescence=ideal.tolist(),
            measured_fluorescence=measured.tolist(),
            photon_counts=[int(value) for value in photon_counts_array],
            reference_photon_count=request.reference_photon_count,
            lower_mhz=lower,
            upper_mhz=upper,
            projected_field_nt=projected_field,
        ),
        estimation=NVFieldEstimationResponse(
            lower_mhz=fitted_lower,
            upper_mhz=fitted_upper,
            projected_field_magnitude_nt=field_magnitude,
            residual_rmse=residual_rmse,
            fit_success=True,
        ),
        uncertainty=uncertainty,
        fit_success=True,
    )
