"""Reference-frame definitions for the BQRC platform."""

from enum import StrEnum


class ReferenceFrame(StrEnum):
    """Standard reference-frame identifiers used by BQRC."""

    ECI = "eci"
    ECEF = "ecef"

    ORBITAL = "orbital"
    STATION = "station"
    BQRC_BODY = "bqrc_body"

    NV_SENSOR = "nv_sensor"
    IMU_SENSOR = "imu_sensor"

    LOCAL_NED = "local_ned"
    LOCAL_ENU = "local_enu"