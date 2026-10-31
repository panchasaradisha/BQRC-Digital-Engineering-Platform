"""Physical constants shared by sensor models and estimation algorithms.

These live in ``core`` so that forward models (``sensors``) and
estimators (``algorithms``) can both depend on them without depending
on each other.
"""

ZERO_FIELD_SPLITTING_MHZ = 2870.0
"""NV-center ground-state zero-field splitting D (room temperature), MHz."""

ELECTRON_GYROMAGNETIC_RATIO_MHZ_PER_T = 28_024.95
"""Electron gyromagnetic ratio, MHz per tesla."""

NANOTESLA_PER_TESLA = 1_000_000_000.0
