"""Data processing levels for BQRC measurements (SYSTEM_ARCHITECTURE section 15)."""

from enum import StrEnum


class ProcessingLevel(StrEnum):
    """Stage of the processing chain at which a value was produced."""

    L0_TRUTH = "L0_truth"
    L1_RAW = "L1_raw"
    L2_CONDITIONED = "L2_conditioned"
    L3_CALIBRATED = "L3_calibrated"
    L4_ESTIMATED = "L4_estimated"
    L5_FUSED = "L5_fused"
    L6_APPLICATION = "L6_application"
