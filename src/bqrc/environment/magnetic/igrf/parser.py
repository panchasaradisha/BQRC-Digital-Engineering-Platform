"""Parser for official IGRF coefficient text datasets."""

from __future__ import annotations

from pathlib import Path

from bqrc.environment.magnetic.igrf.coefficients import (
    CoefficientKind,
    IGRFCoefficient,
    IGRFCoefficientSet,
)


class IGRFParseError(ValueError):
    """Raised when an IGRF coefficient dataset cannot be parsed safely."""


def load_igrf14_2025(
    path: str | Path,
) -> IGRFCoefficientSet:
    """Load the IGRF-14 2025 main-field coefficient set.

    The official IGRF-14 coefficient table contains historical model epochs,
    the 2025.0 main-field coefficients, and 2025-2030 predictive secular
    variation.

    This loader intentionally extracts only the 2025.0 main-field model and
    attaches the corresponding secular-variation value where it is defined.

    Parameters
    ----------
    path:
        Path to the official ``igrf14coeffs.txt`` dataset.

    Returns
    -------
    IGRFCoefficientSet
        Parsed IGRF-14 coefficient set for epoch 2025.0.

    Raises
    ------
    FileNotFoundError
        If the coefficient dataset does not exist.
    IGRFParseError
        If the expected IGRF-14 table structure is missing or malformed.
    """

    dataset_path = Path(path)

    if not dataset_path.is_file():
        raise FileNotFoundError(
            f"IGRF coefficient dataset not found: {dataset_path}"
        )

    lines = dataset_path.read_text(
        encoding="utf-8",
    ).splitlines()

    header_tokens: list[str] | None = None
    data_rows: list[list[str]] = []

    for raw_line in lines:
        line = raw_line.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        tokens = line.split()

        if tokens[0].lower() == "g/h":
            header_tokens = tokens
            continue

        if tokens[0].lower() in {"g", "h"}:
            data_rows.append(tokens)

    if header_tokens is None:
        raise IGRFParseError(
            "IGRF coefficient header row was not found"
        )

    if not data_rows:
        raise IGRFParseError(
            "IGRF coefficient dataset contains no coefficient rows"
        )

    try:
        epoch_2025_index = header_tokens.index("2025.0")
    except ValueError as exc:
        raise IGRFParseError(
            "IGRF dataset does not contain the 2025.0 epoch"
        ) from exc

    try:
        secular_variation_index = header_tokens.index("2025-30")
    except ValueError as exc:
        raise IGRFParseError(
            "IGRF dataset does not contain the 2025-30 secular variation"
        ) from exc

    coefficients: list[IGRFCoefficient] = []

    for tokens in data_rows:
        required_columns = max(
            epoch_2025_index,
            secular_variation_index,
        )

        if len(tokens) <= required_columns:
            raise IGRFParseError(
                "IGRF coefficient row has fewer columns than expected: "
                + " ".join(tokens)
            )

        try:
            kind = CoefficientKind(tokens[0].lower())
            degree = int(tokens[1])
            order = int(tokens[2])
            value_nt = float(tokens[epoch_2025_index])

            if degree <= 8:
                secular_variation_token = tokens[
                    secular_variation_index
                ]

                secular_variation = float(
                    secular_variation_token
                )
            else:
                secular_variation = None
            

        except (ValueError, IndexError) as exc:
            raise IGRFParseError(
                "Unable to parse IGRF coefficient row: "
                + " ".join(tokens)
            ) from exc

        coefficients.append(
            IGRFCoefficient(
                kind=kind,
                degree=degree,
                order=order,
                epoch=2025.0,
                value_nt=value_nt,
                secular_variation_nt_per_year=secular_variation,
            )
        )

    maximum_degree = max(
        coefficient.degree
        for coefficient in coefficients
    )

    return IGRFCoefficientSet(
        model="IGRF-14",
        epoch=2025.0,
        maximum_degree=maximum_degree,
        coefficients=tuple(coefficients),
    )