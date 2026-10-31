"""Verification tools comparing estimates against simulation truth."""

from bqrc.verification.error import (
    ErrorRecord,
    compute_error_record,
    true_axis_field_magnitude_nt,
)

__all__ = ["ErrorRecord", "compute_error_record", "true_axis_field_magnitude_nt"]
