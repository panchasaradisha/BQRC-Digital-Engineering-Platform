"""Tests for processing levels and the extended Measurement/DataSource contracts."""

from datetime import UTC, datetime

from bqrc.core import DataSource, Measurement, ProcessingLevel

NOW = datetime(2027, 7, 18, 10, 0, tzinfo=UTC)


def test_levels_cover_l0_to_l6() -> None:
    assert [level.value[:2] for level in ProcessingLevel] == [
        "L0", "L1", "L2", "L3", "L4", "L5", "L6"
    ]


def test_measurement_new_fields_are_optional() -> None:
    plain = Measurement(
        quantity="x", value=1.0, unit="nT", timestamp=NOW, source=DataSource.DERIVED
    )

    assert plain.level is None
    assert plain.configuration_id is None
    assert plain.model_version is None


def test_measurement_carries_level_and_versions() -> None:
    m = Measurement(
        quantity="x", value=1.0, unit="nT", timestamp=NOW, source=DataSource.SIMULATED_SENSOR,
        level=ProcessingLevel.L4_ESTIMATED, configuration_id="abc", model_version="v1",
    )

    assert Measurement.model_validate_json(m.model_dump_json()) == m


def test_spec_data_origins_present() -> None:
    assert DataSource.HYBRID == "hybrid"
    assert DataSource.MEASURED_PUBLIC == "measured_public"
    assert DataSource.DATASET_REPLAY == "dataset_replay"
