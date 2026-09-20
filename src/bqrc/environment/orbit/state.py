"""Orbital-state definitions for the BQRC space-environment model."""

from datetime import UTC, datetime

from pydantic import BaseModel, field_validator, model_validator

from bqrc.frames import Vector3


class OrbitalState(BaseModel):
    """Position and velocity of BQRC at a specific instant."""

    timestamp: datetime
    position: Vector3
    velocity: Vector3

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_be_timezone_aware(cls, value: datetime) -> datetime:
        """Require an unambiguous orbital-state timestamp."""
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("orbital-state timestamp must be timezone-aware")

        return value.astimezone(UTC)

    @model_validator(mode="after")
    def validate_state_consistency(self) -> "OrbitalState":
        """Ensure position and velocity describe the same reference frame."""
        if self.position.frame != self.velocity.frame:
            raise ValueError(
                "orbital position and velocity must use the same reference frame"
            )

        return self