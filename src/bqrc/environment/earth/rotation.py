"""Earth-rotation calculations for BQRC reference-frame transformations."""

from datetime import UTC, datetime
from math import pi

SECONDS_PER_DAY = 86_400.0
JULIAN_DATE_UNIX_EPOCH = 2_440_587.5
JULIAN_DATE_J2000 = 2_451_545.0


def julian_date_utc(timestamp: datetime) -> float:
    """Convert a timezone-aware timestamp to Julian Date using UTC."""

    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")

    utc_timestamp = timestamp.astimezone(UTC)

    return (
        JULIAN_DATE_UNIX_EPOCH
        + utc_timestamp.timestamp() / SECONDS_PER_DAY
    )


def earth_rotation_angle(timestamp: datetime) -> float:
    """Calculate Earth Rotation Angle using the V1 UT1≈UTC approximation."""

    julian_date = julian_date_utc(timestamp)

    days_since_j2000 = julian_date - JULIAN_DATE_J2000

    turns = (
        0.7790572732640
        + 1.00273781191135448 * days_since_j2000
    )

    fractional_turn = turns % 1.0

    return 2.0 * pi * fractional_turn