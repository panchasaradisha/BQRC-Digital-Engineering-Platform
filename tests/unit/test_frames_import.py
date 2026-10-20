
"""Regression tests for BQRC reference-frame package imports."""

import subprocess
import sys


def test_attitude_import_in_fresh_python_process() -> None:
    """Importing attitude must not trigger a circular package import."""

    script = (
        "from bqrc.frames.attitude import Quaternion; "
        "from bqrc.frames import ReferenceFrame, Vector3, eci_to_ecef; "
        "assert Quaternion(1.0, 0.0, 0.0, 0.0).w == 1.0; "
        "assert ReferenceFrame.BQRC_BODY.value == 'bqrc_body'; "
        "assert Vector3 is not None; "
        "assert callable(eci_to_ecef)"
    )

    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
    )

    assert result.returncode == 0, (
        f"Fresh-process import failed:\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
