"""Scientific provenance definitions for the BQRC platform."""

from enum import StrEnum


class DataSource(StrEnum):
    """Origin of a value or measurement within BQRC."""

    SIMULATION_TRUTH = "simulation_truth"
    SIMULATED_SENSOR = "simulated_sensor"
    DATASET_REPLAY = "dataset_replay"
    REAL_HARDWARE = "real_hardware"
    DERIVED = "derived"
    USER_OVERRIDE = "user_override"