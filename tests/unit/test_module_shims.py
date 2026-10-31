"""Old import paths must keep resolving to the relocated implementations."""

from bqrc.algorithms.odmr import shot_noise as old_shot
from bqrc.algorithms.odmr import spectrum as old_spectrum
from bqrc.sensors.nv import odmr_model, photodetection


def test_spectrum_shim_points_to_sensor_model() -> None:
    assert old_spectrum.simulate_odmr_spectrum is odmr_model.simulate_odmr_spectrum
    assert old_spectrum.ODMRSpectrum is odmr_model.ODMRSpectrum
    assert old_spectrum.lorentzian is odmr_model.lorentzian


def test_shot_noise_shim_points_to_photodetection() -> None:
    assert old_shot.simulate_photon_shot_noise is photodetection.simulate_photon_shot_noise
    assert old_shot.NoisyODMRSpectrum is photodetection.NoisyODMRSpectrum
