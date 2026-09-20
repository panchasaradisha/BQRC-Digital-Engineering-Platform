"""Tests for BQRC Earth-shadow and eclipse geometry."""

import pytest

from bqrc.environment.thermal import (
    EARTH_SHADOW_RADIUS_M,
    EclipseState,
    evaluate_earth_eclipse,
)
from bqrc.frames import ReferenceFrame, Vector3


def eci_position(
    x: float,
    y: float,
    z: float,
) -> Vector3:
    """Create an ECI spacecraft-position vector."""

    return Vector3(
        x=x,
        y=y,
        z=z,
        unit="m",
        frame=ReferenceFrame.ECI,
    )


def eci_direction(
    x: float,
    y: float,
    z: float,
) -> Vector3:
    """Create an ECI dimensionless direction vector."""

    return Vector3(
        x=x,
        y=y,
        z=z,
        unit="1",
        frame=ReferenceFrame.ECI,
    )


def test_spacecraft_behind_earth_is_in_eclipse() -> None:
    """Spacecraft directly anti-solar should enter Earth shadow."""

    state = evaluate_earth_eclipse(
        spacecraft_position=eci_position(
            -6_771_000.0,
            0.0,
            0.0,
        ),
        earth_to_sun_unit=eci_direction(
            1.0,
            0.0,
            0.0,
        ),
    )

    assert state.in_eclipse is True
    assert state.sunlight_fraction == 0.0

    assert state.axial_distance_m == pytest.approx(
        -6_771_000.0
    )

    assert state.shadow_axis_distance_m == pytest.approx(
        0.0
    )


def test_spacecraft_sunward_is_illuminated() -> None:
    """Spacecraft on the Sun-facing side should remain illuminated."""

    state = evaluate_earth_eclipse(
        spacecraft_position=eci_position(
            6_771_000.0,
            0.0,
            0.0,
        ),
        earth_to_sun_unit=eci_direction(
            1.0,
            0.0,
            0.0,
        ),
    )

    assert state.in_eclipse is False
    assert state.sunlight_fraction == 1.0


def test_spacecraft_outside_shadow_radius_is_illuminated() -> None:
    """Anti-solar spacecraft outside the shadow cylinder sees Sun."""

    state = evaluate_earth_eclipse(
        spacecraft_position=eci_position(
            -6_771_000.0,
            EARTH_SHADOW_RADIUS_M + 100_000.0,
            0.0,
        ),
        earth_to_sun_unit=eci_direction(
            1.0,
            0.0,
            0.0,
        ),
    )

    assert state.in_eclipse is False
    assert state.sunlight_fraction == 1.0

    assert (
        state.shadow_axis_distance_m
        > EARTH_SHADOW_RADIUS_M
    )


def test_non_unit_sun_vector_is_normalized() -> None:
    """Eclipse geometry should tolerate a scaled Sun direction."""

    state = evaluate_earth_eclipse(
        spacecraft_position=eci_position(
            -6_771_000.0,
            0.0,
            0.0,
        ),
        earth_to_sun_unit=eci_direction(
            10.0,
            0.0,
            0.0,
        ),
    )

    assert state.in_eclipse is True


def test_wrong_spacecraft_frame_is_rejected() -> None:
    """Eclipse calculation requires spacecraft position in ECI."""

    spacecraft = Vector3(
        x=-6_771_000.0,
        y=0.0,
        z=0.0,
        unit="m",
        frame=ReferenceFrame.ECEF,
    )

    with pytest.raises(
        ValueError,
        match="ECI",
    ):
        evaluate_earth_eclipse(
            spacecraft_position=spacecraft,
            earth_to_sun_unit=eci_direction(
                1.0,
                0.0,
                0.0,
            ),
        )


def test_invalid_sun_unit_is_rejected() -> None:
    """Sun direction must be represented as dimensionless."""

    invalid_sun = Vector3(
        x=1.0,
        y=0.0,
        z=0.0,
        unit="m",
        frame=ReferenceFrame.ECI,
    )

    with pytest.raises(
        ValueError,
        match="dimensionless",
    ):
        evaluate_earth_eclipse(
            spacecraft_position=eci_position(
                -6_771_000.0,
                0.0,
                0.0,
            ),
            earth_to_sun_unit=invalid_sun,
        )


def test_eclipse_state_rejects_invalid_sunlight_fraction() -> None:
    """Sunlight fraction must remain physically bounded."""

    with pytest.raises(
        ValueError,
        match="between 0 and 1",
    ):
        EclipseState(
            in_eclipse=False,
            sunlight_fraction=1.5,
            axial_distance_m=1.0,
            shadow_axis_distance_m=1.0,
        )