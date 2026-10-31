"""Deprecated import path; use ``bqrc.sensors.nv.odmr_model``.

The ODMR spectrum generator is a sensor forward model, so it now lives
in the sensors layer. This shim keeps old imports working.
"""

from bqrc.sensors.nv.odmr_model import (
    ODMRSpectrum,
    lorentzian,
    simulate_odmr_spectrum,
)

__all__ = ["ODMRSpectrum", "lorentzian", "simulate_odmr_spectrum"]
