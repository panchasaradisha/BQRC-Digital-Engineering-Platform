"""Time primitives for the BQRC simulation platform."""

from datetime import UTC, datetime, timedelta

from pydantic import BaseModel, Field, field_validator


class SimulationTime(BaseModel):
    """Current time state of a BQRC simulation."""

    epoch: datetime
    elapsed_seconds: float = Field(default=0.0, ge=0.0)
    time_scale: float = Field(default=1.0, gt=0.0)

    @field_validator("epoch")
    @classmethod
    def epoch_must_be_timezone_aware(cls, value: datetime) -> datetime:
        """Require an unambiguous timezone-aware simulation epoch."""
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("simulation epoch must be timezone-aware")

        return value.astimezone(UTC)

    @property
    def current_datetime(self) -> datetime:
        """Return the UTC datetime represented by the simulation state."""
        return self.epoch + timedelta(seconds=self.elapsed_seconds)

    def advance(self, wall_seconds: float) -> "SimulationTime":
        """Return a new simulation state advanced by wall-clock seconds."""
        if wall_seconds < 0.0:
            raise ValueError("wall_seconds cannot be negative")

        return self.model_copy(
            update={
                "elapsed_seconds": self.elapsed_seconds
                + wall_seconds * self.time_scale
            }
        )