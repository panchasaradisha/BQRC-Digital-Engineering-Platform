"""Universal scientific measurement contract for the BQRC platform."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from bqrc.core.provenance import DataSource
from bqrc.core.quality import QualityFlag
from bqrc.core.uncertainty import Uncertainty


class Measurement(BaseModel):
    """A scalar scientific measurement produced or consumed by BQRC."""

    quantity: str = Field(min_length=1)
    value: float
    unit: str = Field(min_length=1)
    timestamp: datetime

    source: DataSource
    quality: QualityFlag = QualityFlag.NOMINAL
    uncertainty: Uncertainty | None = None

    sensor_id: str | None = None
    frame: str | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_be_timezone_aware(cls, value: datetime) -> datetime:
        """Reject ambiguous timestamps."""
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("measurement timestamp must be timezone-aware")

        return value