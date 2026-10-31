"""Scenario configuration for a reproducible simulation run."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from bqrc.core.constants import ZERO_FIELD_SPLITTING_MHZ
from bqrc.sensors.nv.config import NVSensorConfig
from bqrc.simulation.clock import period_in_steps

DEFAULT_IGRF14_DATASET = "data/reference/geomagnetic/igrf14/raw/igrf14coeffs.txt"
EARTH_EQUATORIAL_RADIUS_M = 6_378_137.0


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True)


class OrbitConfig(_Frozen):
    """Ideal circular two-body orbit (no J2, drag or third bodies)."""

    radius_m: float = Field(default=6_771_000.0, gt=EARTH_EQUATORIAL_RADIUS_M)
    inclination_deg: float = Field(default=51.6, ge=0.0, le=180.0)


class AttitudeProfile(_Frozen):
    """Body-to-NED attitude: a fixed quaternion, optionally spinning.

    ``initial_body_to_ned`` is scalar-first (w, x, y, z) and need not be
    pre-normalized. If ``rate_rad_s`` is nonzero the body spins at a
    constant rate about ``rate_axis_body`` (a body-fixed axis). There is
    no attitude dynamics; this is a kinematic profile only. Nadir
    pointing is not implemented yet.
    """

    initial_body_to_ned: tuple[float, float, float, float] = (1.0, 0.0, 0.0, 0.0)
    rate_axis_body: tuple[float, float, float] = (0.0, 0.0, 1.0)
    rate_rad_s: float = 0.0

    @model_validator(mode="after")
    def _validate(self) -> AttitudeProfile:
        if not any(self.initial_body_to_ned):
            raise ValueError("initial_body_to_ned must be nonzero")

        if self.rate_rad_s != 0.0 and not any(self.rate_axis_body):
            raise ValueError("rate_axis_body must be nonzero when spinning")

        return self


class EstimatorConfig(_Frozen):
    """Values the estimator *assumes* about the sensor.

    Kept separate from ``NVSensorConfig`` so the estimator is never
    handed the sensor's true parameters implicitly. Defaults match the
    default sensor; change them to study model mismatch.
    """

    assumed_contrast: float = Field(default=0.1, gt=0.0, le=0.5)
    assumed_linewidth_mhz: float = Field(default=1.0, gt=0.0)
    assumed_zero_field_splitting_mhz: float = Field(default=ZERO_FIELD_SPLITTING_MHZ, gt=0.0)


class ScenarioConfig(_Frozen):
    """Complete, hashable description of one simulation run."""

    scenario_id: str = Field(min_length=1)
    epoch: datetime
    duration_s: float = Field(gt=0.0)
    step_s: float = Field(default=10.0, gt=0.0)
    orbit: OrbitConfig = OrbitConfig()
    attitude: AttitudeProfile = AttitudeProfile()
    nv_sensor: NVSensorConfig = NVSensorConfig()
    estimator: EstimatorConfig = EstimatorConfig()
    seed: int = Field(default=0, ge=0)
    igrf_dataset: str = DEFAULT_IGRF14_DATASET

    @field_validator("epoch")
    @classmethod
    def _epoch_tz(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("scenario epoch must be timezone-aware")

        return value.astimezone(UTC)

    @model_validator(mode="after")
    def _validate_rates(self) -> ScenarioConfig:
        period_in_steps(self.duration_s, self.step_s)
        period_in_steps(self.nv_sensor.acquisition_period_s, self.step_s)
        return self

    @property
    def configuration_id(self) -> str:
        """Stable 16-hex-digit hash of the full configuration."""

        canonical = json.dumps(self.model_dump(mode="json"), sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()[:16]
