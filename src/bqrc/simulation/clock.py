"""Deterministic master simulation clock.

Time is ``epoch + k * step`` for an integer step index ``k``, so there is
no accumulated floating-point drift and runs are exactly reproducible.
Multi-rate execution is expressed as "is a subsystem due at step k",
using integer step ratios.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from math import isfinite

_RATIO_TOLERANCE = 1e-9


def period_in_steps(period_s: float, step_s: float) -> int:
    """Return ``period_s / step_s`` as an integer, or raise if not integral."""

    if not (isfinite(period_s) and isfinite(step_s)) or period_s <= 0 or step_s <= 0:
        raise ValueError("period and step must be finite and positive")

    ratio = period_s / step_s
    steps = round(ratio)

    if steps < 1 or abs(ratio - steps) > _RATIO_TOLERANCE * max(1.0, ratio):
        raise ValueError(
            f"period {period_s} s must be a positive integer multiple of step {step_s} s"
        )

    return steps


@dataclass(frozen=True, slots=True)
class SimulationClock:
    """Fixed-step master clock covering ``n_steps`` steps (``n_steps + 1`` ticks)."""

    epoch: datetime
    step_seconds: float
    n_steps: int

    def __post_init__(self) -> None:
        if self.epoch.tzinfo is None or self.epoch.utcoffset() is None:
            raise ValueError("clock epoch must be timezone-aware")

        if not isfinite(self.step_seconds) or self.step_seconds <= 0.0:
            raise ValueError("step_seconds must be finite and positive")

        if self.n_steps < 0:
            raise ValueError("n_steps must be nonnegative")

        object.__setattr__(self, "epoch", self.epoch.astimezone(UTC))

    @classmethod
    def from_duration(
        cls, epoch: datetime, duration_s: float, step_s: float
    ) -> SimulationClock:
        """Create a clock; the duration must be an integer number of steps."""

        return cls(epoch=epoch, step_seconds=step_s, n_steps=period_in_steps(duration_s, step_s))

    def elapsed_at(self, step_index: int) -> float:
        """Elapsed simulation seconds at a step index."""

        self._check_index(step_index)
        return step_index * self.step_seconds

    def time_at(self, step_index: int) -> datetime:
        """UTC timestamp at a step index."""

        return self.epoch + timedelta(seconds=self.elapsed_at(step_index))

    def ticks(self) -> range:
        """All step indices, including the final one."""

        return range(self.n_steps + 1)

    @staticmethod
    def is_due(step_index: int, every_n_steps: int) -> bool:
        """Whether a subsystem running every ``every_n_steps`` steps is due."""

        if every_n_steps < 1:
            raise ValueError("every_n_steps must be at least 1")

        return step_index % every_n_steps == 0

    def _check_index(self, step_index: int) -> None:
        if not 0 <= step_index <= self.n_steps:
            raise IndexError(f"step index {step_index} outside 0..{self.n_steps}")
