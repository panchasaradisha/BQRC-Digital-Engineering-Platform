"""Clock-driven V1 NV scenario runner.

Per acquisition tick the runner executes the V1 vertical slice:

    clock -> orbit -> environment -> truth (L0) -> sensor stimulus
          -> NV sensor -> raw acquisition (L1) -> estimator -> Measurement (L4)
          -> verification against truth

Truth is evaluated only at sensor-acquisition ticks (the orbit is
propagated every step; the environment is evaluated on demand). The
field is held constant during one ODMR sweep (quasi-static assumption).
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from pathlib import Path

import numpy as np

from bqrc.algorithms.odmr.field_measurement import estimate_field_measurement
from bqrc.core.measurement import Measurement
from bqrc.environment import SpaceEnvironmentSimulator
from bqrc.sensors.interface import SensorInterface
from bqrc.sensors.nv.acquisition import ODMRAcquisition
from bqrc.sensors.nv.simulated_sensor import SimulatedNVSensor
from bqrc.simulation.attitude import attitude_at
from bqrc.simulation.clock import SimulationClock, period_in_steps
from bqrc.simulation.config import ScenarioConfig
from bqrc.simulation.orbit import advance_orbit, circular_orbit_state
from bqrc.simulation.truth import TruthState
from bqrc.verification.error import ErrorRecord, compute_error_record

NV_SENSOR_INDEX = 0


def derive_seed(master_seed: int, sensor_index: int, tick: int) -> int:
    """Deterministic, independent noise seed for one sensor at one tick.

    Reusing a single seed at every tick would repeat identical noise;
    deriving it from ``(master_seed, sensor_index, tick)`` keeps runs
    reproducible while decorrelating acquisitions.
    """

    sequence = np.random.SeedSequence(entropy=master_seed, spawn_key=(sensor_index, tick))
    return int(sequence.generate_state(1, dtype=np.uint64)[0])


@dataclass(frozen=True)
class RunResult:
    """Everything produced by one scenario run (truth itself is not kept)."""

    config: ScenarioConfig
    configuration_id: str
    acquisitions: tuple[ODMRAcquisition, ...]
    measurements: tuple[Measurement, ...]
    errors: tuple[ErrorRecord, ...]

    def summary(self) -> dict[str, float | int | None]:
        """Headline verification statistics."""

        errs = [e.error_nt for e in self.errors]
        zs = [abs(e.z_score) for e in self.errors if e.z_score is not None]
        stds = [e.claimed_std_nt for e in self.errors if e.claimed_std_nt is not None]

        return {
            "acquisitions": len(self.acquisitions),
            "rmse_nt": sqrt(sum(e * e for e in errs) / len(errs)) if errs else None,
            "mean_claimed_std_nt": sum(stds) / len(stds) if stds else None,
            "max_abs_z": max(zs) if zs else None,
            "fit_failures": sum(1 for e in self.errors if not e.fit_success),
        }


def run_nv_scenario(
    config: ScenarioConfig,
    simulator: SpaceEnvironmentSimulator | None = None,
    sensor: SensorInterface | None = None,
) -> RunResult:
    """Run the V1 NV scenario deterministically from ``config``."""

    if simulator is None:
        simulator = SpaceEnvironmentSimulator.from_igrf14_dataset(Path(config.igrf_dataset))

    configuration_id = config.configuration_id

    if sensor is None:
        sensor = SimulatedNVSensor(config.nv_sensor, configuration_id=configuration_id)

    clock = SimulationClock.from_duration(config.epoch, config.duration_s, config.step_s)
    acquire_every = period_in_steps(config.nv_sensor.acquisition_period_s, config.step_s)
    estimator = config.estimator

    state = circular_orbit_state(clock.epoch, config.orbit)

    acquisitions: list[ODMRAcquisition] = []
    measurements: list[Measurement] = []
    errors: list[ErrorRecord] = []

    for tick in clock.ticks():
        if tick > 0:
            state = advance_orbit(state, config.step_s)
            # Re-anchor to the exact clock time so sub-step rounding cannot drift.
            state = state.model_copy(update={"timestamp": clock.time_at(tick)})

        if not clock.is_due(tick, acquire_every):
            continue

        truth = TruthState(
            timestamp=clock.time_at(tick),
            orbital_state=state,
            attitude_body_to_ned=attitude_at(config.attitude, clock.elapsed_at(tick)),
            environment=simulator.evaluate(state),
        )

        acquisition = sensor.sample(
            truth.sensor_stimulus(),
            seed=derive_seed(config.seed, NV_SENSOR_INDEX, tick),
        )

        measurement = estimate_field_measurement(
            acquisition,
            assumed_contrast=estimator.assumed_contrast,
            assumed_linewidth_mhz=estimator.assumed_linewidth_mhz,
            assumed_zero_field_splitting_mhz=estimator.assumed_zero_field_splitting_mhz,
        )

        acquisitions.append(acquisition)
        measurements.append(measurement)
        errors.append(compute_error_record(measurement, truth, config.nv_sensor.nv_axis_body))

    return RunResult(
        config=config,
        configuration_id=configuration_id,
        acquisitions=tuple(acquisitions),
        measurements=tuple(measurements),
        errors=tuple(errors),
    )
