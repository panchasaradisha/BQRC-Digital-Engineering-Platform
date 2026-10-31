"""L0 hidden simulation truth.

``TruthState`` may be imported only by ``bqrc.simulation`` and
``bqrc.verification`` (enforced by ``tests/unit/test_architecture_rules.py``).
Sensors and algorithms never see it; they receive a ``SensorStimulus``.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from bqrc.environment.orbit import OrbitalState
from bqrc.environment.simulator import SpaceEnvironmentState
from bqrc.frames.attitude import Quaternion
from bqrc.sensors.stimulus import SensorStimulus


@dataclass(frozen=True, slots=True)
class TruthState:
    """Physical truth at one instant."""

    timestamp: datetime
    orbital_state: OrbitalState
    attitude_body_to_ned: Quaternion
    environment: SpaceEnvironmentState

    def sensor_stimulus(self) -> SensorStimulus:
        """The only hand-off from truth to sensors: physical field in the body frame."""

        field = self.environment.magnetic_field
        ned = (field.north_nt, field.east_nt, field.down_nt)
        body = self.attitude_body_to_ned.conjugate().rotate_components(ned)

        return SensorStimulus(
            timestamp=self.timestamp,
            magnetic_field_body_nt=body,
        )
