"""Static layering rules from SYSTEM_ARCHITECTURE section 68 and the truth rule."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[2] / "src" / "bqrc"


def imports_of(path: Path) -> set[str]:
    found: set[str] = set()

    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            found.add(node.module)
            found.update(f"{node.module}.{alias.name}" for alias in node.names)

    return {name for name in found if name.startswith("bqrc")}


def package_files(package: str) -> list[Path]:
    return sorted((SRC / package).rglob("*.py"))


FORBIDDEN = {
    "core": ["environment", "frames", "sensors", "algorithms", "simulation", "verification", "api"],
    "environment": ["sensors", "algorithms", "simulation", "verification", "api"],
    "sensors": ["algorithms", "simulation", "verification", "api"],
    "algorithms": ["simulation", "verification", "api"],
    "simulation": ["api"],
    "verification": ["api"],
}


@pytest.mark.parametrize("package", sorted(FORBIDDEN))
def test_dependencies_flow_downward(package: str) -> None:
    banned = tuple(f"bqrc.{name}" for name in FORBIDDEN[package])
    violations = [
        f"{path.relative_to(SRC)} imports {name}"
        for path in package_files(package)
        for name in imports_of(path)
        if any(name == b or name.startswith(f"{b}.") for b in banned)
    ]

    assert not violations, violations


def test_truth_is_imported_only_by_simulation_and_verification() -> None:
    violations = []

    for path in sorted(SRC.rglob("*.py")):
        top = path.relative_to(SRC).parts[0]

        if top in {"simulation", "verification"}:
            continue

        if any(n.startswith("bqrc.simulation.truth") for n in imports_of(path)):
            violations.append(str(path.relative_to(SRC)))

    assert not violations, violations


def test_import_scanner_detects_violations(tmp_path: Path) -> None:
    probe = tmp_path / "probe.py"
    probe.write_text("import bqrc.algorithms.odmr\nfrom bqrc.simulation.truth import TruthState\n")

    names = imports_of(probe)

    assert "bqrc.algorithms.odmr" in names
    assert "bqrc.simulation.truth" in names
