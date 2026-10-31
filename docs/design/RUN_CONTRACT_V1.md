# Run Contract V1

**Status:** Implemented (V1 vertical slice)
**Parents:** `SYSTEM_ARCHITECTURE.md` sections 3, 7, 13, 14, 15, 64, 68

This document records the contracts that make a simulation run reproducible
and keep ground truth away from sensors and algorithms.

## 1. Objects by processing level

| Level | Type | Module |
|---|---|---|
| Config | `ScenarioConfig` (frozen, hashed to `configuration_id`) | `bqrc.simulation.config` |
| L0 truth | `TruthState` | `bqrc.simulation.truth` |
| Boundary | `SensorStimulus` | `bqrc.sensors.stimulus` |
| L1 raw | `ODMRAcquisition` | `bqrc.sensors.nv.acquisition` |
| L4 estimated | `Measurement` (`level=L4_ESTIMATED`) | `bqrc.algorithms.odmr.field_measurement` |
| Verification | `ErrorRecord` | `bqrc.verification.error` |

`TruthState.sensor_stimulus()` is the only path from truth to a sensor. A
stimulus carries physical quantities at the sensor (body-frame field), not
truth labels.

## 2. Truth isolation

* `ODMRAcquisition` has no ideal spectrum, true field, or other truth field.
* The estimator receives only frequencies and normalized fluorescence
  (`MeasuredODMR` protocol).
* Estimator assumptions (`EstimatorConfig`) are separate from the sensor's
  physical parameters (`NVSensorConfig`), so model mismatch can be studied.
* `tests/unit/test_architecture_rules.py` fails the build if `sensors/`,
  `algorithms/` or any module outside `simulation/` and `verification/`
  imports `bqrc.simulation.truth`, and enforces the downward layering
  `core < environment < sensors < algorithms < simulation/verification < api`.

## 3. Determinism

* `SimulationClock`: time is `epoch + k * step` for integer `k`; multi-rate
  scheduling uses integer step ratios (`period_in_steps`).
* Noise seeds are derived per sensor and per tick from the master seed
  (`derive_seed`), never reused across ticks.
* `configuration_id` is a SHA-256 prefix of the canonical config JSON and is
  stamped on acquisitions and measurements.

## 4. Run output (`bqrc.simulation.storage.write_run`)

`config.json`, `manifest.json` (config hash, git commit and dirty flag,
package versions, summary), `acquisitions.npz` (raw L1), `measurements.jsonl`,
`errors.jsonl`.

## 5. Module moves (NV forward models)

| Old | New |
|---|---|
| `algorithms/odmr/spectrum.py` | `sensors/nv/odmr_model.py` |
| `algorithms/odmr/shot_noise.py` | `sensors/nv/photodetection.py` |
| NV constants in `sensors/nv/resonance.py` | `core/constants.py` (re-exported) |
| `simulate_*_performance` in `sensors/nv/environment_adapter.py` | `simulation/nv_performance.py` |

The old `algorithms/odmr/spectrum.py` and `shot_noise.py` paths are deprecated
shims and should be removed once nothing imports them.

## 6. Known limitations

* Kinematic attitude only (fixed or constant spin); nadir pointing is not implemented.
* Quasi-static sweep: the field is held constant during one ODMR sweep.
* Truth is evaluated only at acquisition ticks; the orbit is propagated every step.
* No calibration stage: all L4 products carry `UNCALIBRATED`.
* The reported CRLB assumes contrast, linewidth and D are exactly known.
* The estimator is slow (about 2 s per 401-point sweep; 15 multi-start solves).
