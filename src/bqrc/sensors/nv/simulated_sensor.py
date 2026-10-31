"""Simulated NV ODMR sensor implementing ``SensorInterface``."""

from __future__ import annotations

from bqrc.sensors.interface import SensorHealth
from bqrc.sensors.nv.acquisition import ODMRAcquisition
from bqrc.sensors.nv.config import NVSensorConfig
from bqrc.sensors.nv.odmr_model import simulate_odmr_spectrum
from bqrc.sensors.nv.photodetection import simulate_photon_shot_noise
from bqrc.sensors.nv.resonance import calculate_nv_resonance
from bqrc.sensors.stimulus import SensorStimulus

NV_MODEL_VERSION = "nv-axial-lorentzian-poisson-0.1"


class SimulatedNVSensor:
    """First-order axial NV sensor with Lorentzian ODMR and Poisson noise.

    Model limits (see ``resonance.py``): no transverse-field mixing,
    strain, hyperfine structure or temperature dependence; a single NV
    axis; photon shot noise only.
    """

    def __init__(
        self,
        config: NVSensorConfig,
        configuration_id: str | None = None,
    ) -> None:
        self._config = config
        self._configuration_id = configuration_id

    @property
    def sensor_id(self) -> str:
        return self._config.sensor_id

    @property
    def config(self) -> NVSensorConfig:
        return self._config

    def configure(self, config: NVSensorConfig) -> None:
        self._config = config

    def sample(
        self,
        stimulus: SensorStimulus,
        seed: int | None = None,
    ) -> ODMRAcquisition:
        """Produce one noisy ODMR sweep for the given physical stimulus."""

        cfg = self._config

        resonance = calculate_nv_resonance(
            magnetic_field_nt=stimulus.magnetic_field_body_nt,
            nv_axis=cfg.nv_axis_body,
            zero_field_splitting_mhz=cfg.zero_field_splitting_mhz,
        )

        ideal = simulate_odmr_spectrum(
            resonance=resonance,
            frequencies_mhz=cfg.frequencies_mhz(),
            contrast=cfg.contrast,
            linewidth_mhz=cfg.linewidth_mhz,
        )

        noisy = simulate_photon_shot_noise(
            spectrum=ideal,
            reference_photon_count=cfg.reference_photon_count,
            seed=seed,
        )

        return ODMRAcquisition(
            sensor_id=cfg.sensor_id,
            timestamp=stimulus.timestamp,
            frequencies_mhz=noisy.frequencies_mhz,
            photon_counts=noisy.photon_counts,
            reference_photon_count=noisy.reference_photon_count,
            model_version=NV_MODEL_VERSION,
            configuration_id=self._configuration_id,
        )

    def health(self) -> SensorHealth:
        return SensorHealth(self.sensor_id, True, "simulated sensor nominal")
