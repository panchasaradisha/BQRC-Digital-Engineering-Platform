"""Tests for BQRC traceable scientific parameters."""

from bqrc.core.parameter import Parameter, ParameterSource


def test_datasheet_parameter_preserves_source() -> None:
    """Hardware parameters should preserve datasheet provenance."""
    parameter = Parameter(
        name="accelerometer_noise_density",
        value=80e-6,
        unit="m/s^2/sqrt(Hz)",
        source=ParameterSource.DATASHEET,
        reference="Example manufacturer datasheet",
        hardware_model="IMU_EXAMPLE",
    )

    assert parameter.source == ParameterSource.DATASHEET
    assert parameter.hardware_model == "IMU_EXAMPLE"


def test_engineering_assumption_is_explicit() -> None:
    """Assumed values should remain identifiable as assumptions."""
    parameter = Parameter(
        name="station_local_magnetic_disturbance",
        value=2e-6,
        unit="T",
        source=ParameterSource.ENGINEERING_ASSUMPTION,
        notes="Placeholder pending validated station-environment evidence.",
    )

    assert parameter.source == ParameterSource.ENGINEERING_ASSUMPTION


def test_user_override_is_traceable() -> None:
    """Manual parameter changes should preserve user-override provenance."""
    parameter = Parameter(
        name="apd_dark_count_rate",
        value=10_000.0,
        unit="count/s",
        source=ParameterSource.USER_OVERRIDE,
    )

    assert parameter.source == ParameterSource.USER_OVERRIDE


def test_parameter_metadata_is_independent() -> None:
    """Parameter metadata dictionaries must not be shared."""
    first = Parameter(
        name="parameter_a",
        value=1.0,
        unit="1",
        source=ParameterSource.BQRC_DEFAULT,
    )

    second = Parameter(
        name="parameter_b",
        value=2.0,
        unit="1",
        source=ParameterSource.BQRC_DEFAULT,
    )

    first.metadata["test"] = True

    assert "test" not in second.metadata