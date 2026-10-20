
"""HTTP endpoints for NV-center magnetometry calculations."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from bqrc.algorithms.odmr.field_estimator import estimate_nv_field_from_odmr
from bqrc.algorithms.odmr.shot_noise import NoisyODMRSpectrum, simulate_photon_shot_noise
from bqrc.algorithms.odmr.spectrum import simulate_odmr_spectrum
from bqrc.sensors.nv.resonance import (
    ZERO_FIELD_SPLITTING_MHZ,
    calculate_nv_resonance,
)

FiniteFloat = Annotated[float, Field(allow_inf_nan=False)]
PositiveFiniteFloat = Annotated[
    float,
    Field(gt=0.0, allow_inf_nan=False),
]

Vector3 = tuple[FiniteFloat, FiniteFloat, FiniteFloat]

router = APIRouter(prefix="/api/v1/nv", tags=["NV Magnetometry"])


class NVResonanceRequest(BaseModel):
    """Validated input for an NV resonance calculation."""

    magnetic_field_nt: Vector3
    nv_axis: Vector3
    zero_field_splitting_mhz: PositiveFiniteFloat = (
        ZERO_FIELD_SPLITTING_MHZ
    )

    @field_validator("nv_axis")
    @classmethod
    def validate_nv_axis(cls, value: Vector3) -> Vector3:
        """Reject an NV orientation vector with zero magnitude."""
        if all(component == 0.0 for component in value):
            raise ValueError("nv_axis must have nonzero magnitude")
        return value


class NVResonanceResponse(BaseModel):
    """NV transition frequencies and signed field projection."""

    lower_mhz: float
    upper_mhz: float
    projected_field_nt: float


class ODMRSpectrumRequest(NVResonanceRequest):
    """Input parameters for an ideal ODMR spectrum simulation."""

    frequencies_mhz: list[FiniteFloat] = Field(
        min_length=1,
        max_length=5000,
    )
    contrast: FiniteFloat = Field(default=0.1, ge=0.0, le=0.5)
    linewidth_mhz: PositiveFiniteFloat = 1.0


class ODMRSpectrumResponse(BaseModel):
    """Simulated ODMR frequencies and normalized fluorescence."""

    frequencies_mhz: list[float]
    fluorescence: list[float]
    lower_mhz: float
    upper_mhz: float
    projected_field_nt: float


@router.post("/resonance", response_model=NVResonanceResponse)
def calculate_resonance(
    request: NVResonanceRequest,
) -> NVResonanceResponse:
    """Calculate axial NV-center resonance frequencies."""
    try:
        result = calculate_nv_resonance(
            magnetic_field_nt=request.magnetic_field_nt,
            nv_axis=request.nv_axis,
            zero_field_splitting_mhz=request.zero_field_splitting_mhz,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return NVResonanceResponse(
        lower_mhz=result.lower_mhz,
        upper_mhz=result.upper_mhz,
        projected_field_nt=result.projected_field_nt,
    )


@router.post("/odmr/spectrum", response_model=ODMRSpectrumResponse)
def calculate_odmr_spectrum(
    request: ODMRSpectrumRequest,
) -> ODMRSpectrumResponse:
    """Simulate an ideal two-resonance NV ODMR spectrum."""
    try:
        resonance = calculate_nv_resonance(
            magnetic_field_nt=request.magnetic_field_nt,
            nv_axis=request.nv_axis,
            zero_field_splitting_mhz=request.zero_field_splitting_mhz,
        )

        spectrum = simulate_odmr_spectrum(
            resonance=resonance,
            frequencies_mhz=tuple(request.frequencies_mhz),
            contrast=request.contrast,
            linewidth_mhz=request.linewidth_mhz,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return ODMRSpectrumResponse(
        frequencies_mhz=list(spectrum.frequencies_mhz),
        fluorescence=list(spectrum.fluorescence),
        lower_mhz=resonance.lower_mhz,
        upper_mhz=resonance.upper_mhz,
        projected_field_nt=resonance.projected_field_nt,
    )

class NoisyODMRSpectrumRequest(ODMRSpectrumRequest):
    """Input parameters for photon shot-noise ODMR simulation."""

    reference_photon_count: PositiveFiniteFloat = Field(
        default=100_000.0,
        le=1e12,
    )
    seed: int | None = Field(default=42, ge=0, le=2**32 - 1)


class NoisyODMRSpectrumResponse(BaseModel):
    """Ideal and noisy ODMR measurements with resonance metadata."""

    frequencies_mhz: list[float]
    ideal_fluorescence: list[float]
    measured_fluorescence: list[float]
    photon_counts: list[int]
    reference_photon_count: float
    lower_mhz: float
    upper_mhz: float
    projected_field_nt: float


@router.post("/odmr/noisy-spectrum", response_model=NoisyODMRSpectrumResponse)
def calculate_noisy_odmr_spectrum(
    request: NoisyODMRSpectrumRequest,
) -> NoisyODMRSpectrumResponse:
    """Simulate an NV ODMR spectrum with Poisson photon shot noise."""
    try:
        resonance = calculate_nv_resonance(
            magnetic_field_nt=request.magnetic_field_nt,
            nv_axis=request.nv_axis,
            zero_field_splitting_mhz=request.zero_field_splitting_mhz,
        )

        ideal = simulate_odmr_spectrum(
            resonance=resonance,
            frequencies_mhz=tuple(request.frequencies_mhz),
            contrast=request.contrast,
            linewidth_mhz=request.linewidth_mhz,
        )

        noisy = simulate_photon_shot_noise(
            spectrum=ideal,
            reference_photon_count=request.reference_photon_count,
            seed=request.seed,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return NoisyODMRSpectrumResponse(
        frequencies_mhz=list(noisy.frequencies_mhz),
        ideal_fluorescence=list(ideal.fluorescence),
        measured_fluorescence=list(noisy.fluorescence),
        photon_counts=list(noisy.photon_counts),
        reference_photon_count=noisy.reference_photon_count,
        lower_mhz=resonance.lower_mhz,
        upper_mhz=resonance.upper_mhz,
        projected_field_nt=resonance.projected_field_nt,
    )

class NVFieldEstimationRequest(BaseModel):
    """Measured photon-count data for NV magnetic-field estimation."""

    frequencies_mhz: list[FiniteFloat] = Field(
        min_length=5,
        max_length=5000,
    )
    photon_counts: list[int] = Field(
        min_length=5,
        max_length=5000,
    )
    reference_photon_count: PositiveFiniteFloat = Field(
        gt=0.0,
        le=1e12,
    )
    contrast: FiniteFloat = Field(
        default=0.1,
        gt=0.0,
        le=0.5,
    )
    linewidth_mhz: PositiveFiniteFloat = 1.0
    zero_field_splitting_mhz: PositiveFiniteFloat = (
        ZERO_FIELD_SPLITTING_MHZ
    )

    @field_validator("photon_counts")
    @classmethod
    def validate_photon_counts(cls, value: list[int]) -> list[int]:
        """Reject negative photon counts."""
        if any(count < 0 for count in value):
            raise ValueError("photon_counts must be nonnegative")
        return value


class NVFieldEstimationResponse(BaseModel):
    """Estimated NV-axis field magnitude and fitting diagnostics."""

    lower_mhz: float
    upper_mhz: float
    projected_field_magnitude_nt: float
    residual_rmse: float
    fit_success: bool


@router.post("/odmr/estimate-field", response_model=NVFieldEstimationResponse)
def estimate_odmr_field(
    request: NVFieldEstimationRequest,
) -> NVFieldEstimationResponse:
    """Estimate projected field magnitude from measured photon counts."""
    if len(request.frequencies_mhz) != len(request.photon_counts):
        raise HTTPException(
            status_code=422,
            detail="frequency and photon-count arrays must have equal lengths",
        )

    measured_fluorescence = tuple(
        count / request.reference_photon_count
        for count in request.photon_counts
    )

    measured = NoisyODMRSpectrum(
        frequencies_mhz=tuple(request.frequencies_mhz),
        photon_counts=tuple(request.photon_counts),
        fluorescence=measured_fluorescence,
        reference_photon_count=request.reference_photon_count,
    )

    try:
        estimate = estimate_nv_field_from_odmr(
            measured=measured,
            contrast=request.contrast,
            linewidth_mhz=request.linewidth_mhz,
            zero_field_splitting_mhz=request.zero_field_splitting_mhz,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return NVFieldEstimationResponse(
        lower_mhz=estimate.lower_mhz,
        upper_mhz=estimate.upper_mhz,
        projected_field_magnitude_nt=estimate.projected_field_magnitude_nt,
        residual_rmse=estimate.residual_rmse,
        fit_success=estimate.fit_success,
    )
