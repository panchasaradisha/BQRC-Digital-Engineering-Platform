"""Traceable scientific and engineering parameters for the BQRC platform."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ParameterSource(StrEnum):
    """Origin of a scientific or engineering parameter."""

    DATASHEET = "datasheet"
    RESEARCH_PAPER = "research_paper"
    STANDARD = "standard"
    DATASET = "dataset"
    LAB_MEASUREMENT = "lab_measurement"
    CALIBRATION = "calibration"

    PHYSICS_MODEL = "physics_model"
    ENGINEERING_ASSUMPTION = "engineering_assumption"
    BQRC_DEFAULT = "bqrc_default"

    USER_OVERRIDE = "user_override"


class Parameter(BaseModel):
    """A traceable parameter used by a BQRC model or hardware profile."""

    name: str = Field(min_length=1)
    value: float
    unit: str = Field(min_length=1)

    source: ParameterSource

    reference: str | None = None
    hardware_model: str | None = None
    notes: str | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)