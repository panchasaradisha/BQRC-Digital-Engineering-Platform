"""Deprecated import path; use ``bqrc.sensors.nv.photodetection``.

Photon shot-noise simulation is a detector forward model, so it now
lives in the sensors layer. This shim keeps old imports working.
"""

from bqrc.sensors.nv.photodetection import (
    NoisyODMRSpectrum,
    simulate_photon_shot_noise,
)

__all__ = ["NoisyODMRSpectrum", "simulate_photon_shot_noise"]
