"""Persist a run so it can be reproduced and audited.

Layout of a run directory::

    config.json         full ScenarioConfig
    manifest.json       configuration_id, versions, git commit, counts
    acquisitions.npz    raw L1 arrays (timestamps, frequencies, counts, reference)
    measurements.jsonl  one L4 Measurement per line
    errors.jsonl        one verification ErrorRecord per line

All files except ``manifest.json`` (which records the wall-clock write
time) are deterministic functions of the configuration.
"""

from __future__ import annotations

import dataclasses
import json
import platform
import subprocess
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path
from typing import Any

import numpy as np

from bqrc.simulation.runner import RunResult


def _git_state() -> dict[str, Any]:
    here = Path(__file__).resolve().parent

    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=here, capture_output=True, text=True, check=True,
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=here, capture_output=True, text=True, check=True,
            ).stdout.strip()
        )
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty": None}

    return {"commit": commit, "dirty": dirty}


def _version(package: str) -> str | None:
    try:
        return metadata.version(package)
    except metadata.PackageNotFoundError:
        return None


def _json_default(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()

    raise TypeError(f"not JSON serializable: {type(value)}")


def write_run(result: RunResult, directory: Path | str) -> Path:
    """Write ``result`` to ``directory`` (created if needed) and return it."""

    out = Path(directory)
    out.mkdir(parents=True, exist_ok=True)

    (out / "config.json").write_text(
        result.config.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )

    acq = result.acquisitions
    np.savez_compressed(
        out / "acquisitions.npz",
        timestamps=np.array([a.timestamp.isoformat() for a in acq]),
        frequencies_mhz=np.array([a.frequencies_mhz for a in acq], dtype=np.float64),
        photon_counts=np.array([a.photon_counts for a in acq], dtype=np.int64),
        reference_photon_count=np.array(
            [a.reference_photon_count for a in acq], dtype=np.float64
        ),
    )

    with (out / "measurements.jsonl").open("w", encoding="utf-8") as handle:
        for measurement in result.measurements:
            handle.write(measurement.model_dump_json() + "\n")

    with (out / "errors.jsonl").open("w", encoding="utf-8") as handle:
        for error in result.errors:
            handle.write(json.dumps(dataclasses.asdict(error), default=_json_default) + "\n")

    manifest = {
        "configuration_id": result.configuration_id,
        "scenario_id": result.config.scenario_id,
        "n_acquisitions": len(acq),
        "summary": result.summary(),
        "git": _git_state(),
        "python": platform.python_version(),
        "packages": {p: _version(p) for p in ("numpy", "scipy", "pydantic")},
        "written_utc": datetime.now(UTC).isoformat(),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    return out
