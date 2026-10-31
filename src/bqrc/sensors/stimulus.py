"""Physical stimulus delivered to a sensor.

``SensorStimulus`` is the single, explicit hand-off from the simulated
environment to a sensor model. It carries only physical quantities at
the sensor, expressed in the sensor/body frame. It contains no hidden
truth labels, so sensor models and everything downstream of them cannot
read ground truth by construction.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite


@dataclass(frozen=True, slots=True)
class SensorStimulus:
    """Physical conditions at a sensor at one instant.

    Parameters
    ----------
    timestamp:
        Timezone-aware UTC timestamp.
    magnetic_field_body_nt:
        Magnetic field in the spacecraft body frame, nanotesla.
    temperature_k:
        Sensor temperature in kelvin, if modelled. ``None`` means the
        temperature is not modelled (the NV model is currently
        temperature-independent).
    """

    timestamp: datetime
    magnetic_field_body_nt: tuple[float, float, float]
    temperature_k: float | None = None

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            raise ValueError("stimulus timestamp must be timezone-aware")

        if len(self.magnetic_field_body_nt) != 3 or not all(
            isfinite(c) for c in self.magnetic_field_body_nt
        ):
            raise ValueError("magnetic field must have three finite components")

        if self.temperature_k is not None and (
            not isfinite(self.temperature_k) or self.temperature_k <= 0.0
        ):
            raise ValueError("temperature_k must be finite and positive")
