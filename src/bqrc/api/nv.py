
"""HTTP endpoints for NV-center magnetometry calculations."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

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
