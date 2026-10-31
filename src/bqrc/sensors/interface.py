"""Common sensor interface (SYSTEM_ARCHITECTURE section 13).

Simulated, dataset-replay and real-hardware sensors implement the same
interface so downstream processing does not depend on the data source.
V1 defines only ``configure``, ``sample`` and ``health``; ``calibrate``,
``initialize`` and ``shutdown`` are added when something needs them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from bqrc.sensors.stimulus import SensorStimulus


@dataclass(frozen=True, slots=True)
class SensorHealth:
    """Minimal sensor health report."""

    sensor_id: str
    nominal: bool
    detail: str = ""


@runtime_checkable
class SensorInterface(Protocol):
    """Interface implemented by every BQRC sensor source."""

    @property
    def sensor_id(self) -> str: ...

    def configure(self, config: Any) -> None:
        """Replace the sensor configuration."""

    def sample(self, stimulus: SensorStimulus, seed: int | None = None) -> Any:
        """Produce one raw (L1) acquisition for the given stimulus."""

    def health(self) -> SensorHealth:
        """Report sensor health."""
