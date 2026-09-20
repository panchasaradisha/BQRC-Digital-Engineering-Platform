"""Scientific uncertainty definitions for the BQRC platform."""

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class UncertaintyType(StrEnum):
    """Supported interpretations of a reported BQRC uncertainty."""

    STANDARD_DEVIATION = "standard_deviation"
    STANDARD_UNCERTAINTY = "standard_uncertainty"
    EXPANDED_UNCERTAINTY = "expanded_uncertainty"
    CONFIDENCE_INTERVAL = "confidence_interval"
    MODEL_ESTIMATE = "model_estimate"
    UNKNOWN = "unknown"


class Uncertainty(BaseModel):
    """Uncertainty information associated with a scientific value."""

    value: float = Field(ge=0.0)
    uncertainty_type: UncertaintyType
    confidence_level: float | None = Field(default=None, gt=0.0, lt=1.0)
    coverage_factor: float | None = Field(default=None, gt=0.0)
    method: str | None = None

    @model_validator(mode="after")
    def validate_context(self) -> "Uncertainty":
        """Check fields that depend on the selected uncertainty type."""
        if (
            self.uncertainty_type == UncertaintyType.CONFIDENCE_INTERVAL
            and self.confidence_level is None
        ):
            raise ValueError(
                "confidence_level is required for confidence interval uncertainty"
            )

        if (
            self.uncertainty_type == UncertaintyType.EXPANDED_UNCERTAINTY
            and self.coverage_factor is None
        ):
            raise ValueError(
                "coverage_factor is required for expanded uncertainty"
            )

        return self