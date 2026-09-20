"""Basic package-level tests for the BQRC Digital Engineering Platform."""

import bqrc


def test_bqrc_package_import() -> None:
    """Verify that the BQRC package can be imported."""
    assert bqrc is not None