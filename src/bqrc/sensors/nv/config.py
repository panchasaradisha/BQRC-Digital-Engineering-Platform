"""Configuration of a simulated NV ODMR sensor."""

from __future__ import annotations

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, model_validator

from bqrc.core.constants import ZERO_FIELD_SPLITTING_MHZ


class NVSensorConfig(BaseModel):
    """Physical and acquisition parameters of the simulated NV sensor.

    Contrast, linewidth and zero-field splitting here are the *sensor's*
    physical values. The estimator is configured separately (see
    ``EstimatorConfig`` in ``bqrc.simulation.config``) so that a
    mismatch between truth and assumed values can be studied.
    """

    model_config = ConfigDict(frozen=True)

    sensor_id: str = Field(default="nv-0", min_length=1)
    nv_axis_body: tuple[float, float, float] = (0.0, 0.0, 1.0)
    contrast: float = Field(default=0.1, gt=0.0, le=0.5)
    linewidth_mhz: float = Field(default=1.0, gt=0.0)
    zero_field_splitting_mhz: float = Field(default=ZERO_FIELD_SPLITTING_MHZ, gt=0.0)
    reference_photon_count: float = Field(default=1.0e6, gt=0.0)
    sweep_start_mhz: float = 2850.0
    sweep_stop_mhz: float = 2890.0
    sweep_points: int = Field(default=401, ge=5, le=5000)
    acquisition_period_s: float = Field(default=60.0, gt=0.0)

    @model_validator(mode="after")
    def _validate(self) -> NVSensorConfig:
        if not all(np.isfinite(self.nv_axis_body)) or not any(self.nv_axis_body):
            raise ValueError("nv_axis_body must be finite and nonzero")

        if self.sweep_stop_mhz <= self.sweep_start_mhz:
            raise ValueError("sweep_stop_mhz must exceed sweep_start_mhz")

        if not (
            self.sweep_start_mhz < self.zero_field_splitting_mhz < self.sweep_stop_mhz
        ):
            raise ValueError("frequency sweep must span the zero-field splitting")

        return self

    def frequencies_mhz(self) -> tuple[float, ...]:
        """Return the ODMR sweep frequency grid."""

        grid = np.linspace(self.sweep_start_mhz, self.sweep_stop_mhz, self.sweep_points)
        return tuple(float(f) for f in grid)
