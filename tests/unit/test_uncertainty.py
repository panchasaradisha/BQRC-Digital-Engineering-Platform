"""Tests for BQRC scientific uncertainty models."""

import pytest
from pydantic import ValidationError

from bqrc.core.uncertainty import Uncertainty, UncertaintyType


def test_standard_deviation_uncertainty() -> None:
    """A standard-deviation uncertainty should accept a non-negative value."""
    uncertainty = Uncertainty(
        value=0.035,
        uncertainty_type=UncertaintyType.STANDARD_DEVIATION,
        method="Monte Carlo simulation",
    )

    assert uncertainty.value == 0.035
    assert uncertainty.uncertainty_type == UncertaintyType.STANDARD_DEVIATION


def test_negative_uncertainty_is_rejected() -> None:
    """Uncertainty magnitude cannot be negative."""
    with pytest.raises(ValidationError):
        Uncertainty(
            value=-0.1,
            uncertainty_type=UncertaintyType.STANDARD_UNCERTAINTY,
        )


def test_confidence_interval_requires_confidence_level() -> None:
    """Confidence intervals must state their confidence level."""
    with pytest.raises(ValidationError):
        Uncertainty(
            value=0.05,
            uncertainty_type=UncertaintyType.CONFIDENCE_INTERVAL,
        )


def test_confidence_interval_accepts_valid_level() -> None:
    """A confidence interval should accept a valid confidence level."""
    uncertainty = Uncertainty(
        value=0.05,
        uncertainty_type=UncertaintyType.CONFIDENCE_INTERVAL,
        confidence_level=0.95,
    )

    assert uncertainty.confidence_level == 0.95


def test_expanded_uncertainty_requires_coverage_factor() -> None:
    """Expanded uncertainty must state its coverage factor."""
    with pytest.raises(ValidationError):
        Uncertainty(
            value=0.06,
            uncertainty_type=UncertaintyType.EXPANDED_UNCERTAINTY,
        )


def test_expanded_uncertainty_accepts_coverage_factor() -> None:
    """Expanded uncertainty should accept a positive coverage factor."""
    uncertainty = Uncertainty(
        value=0.06,
        uncertainty_type=UncertaintyType.EXPANDED_UNCERTAINTY,
        coverage_factor=2.0,
    )

    assert uncertainty.coverage_factor == 2.0
    