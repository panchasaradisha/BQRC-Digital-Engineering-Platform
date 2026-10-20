
"""Reproducible NV magnetometry Monte Carlo performance experiment.

Compare empirical field-estimation errors with theoretical Poisson
Cramer-Rao lower bounds across several photon budgets.

Run from the project root:
    .\\.venv\\Scripts\\python.exe experiments/magnetic/nv_monte_carlo_performance.py
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from bqrc.algorithms.odmr.monte_carlo import run_nv_field_monte_carlo


def main() -> None:
    """Run a fixed-field photon-budget trade study and save CSV results."""

    true_field_nt = 50_000.0
    photon_budgets = (10_000.0, 100_000.0, 1_000_000.0)
    trial_count = 30
    seed = 73

    frequencies_mhz = tuple(
        float(value) for value in np.linspace(2867.0, 2873.0, 121)
    )

    output_dir = Path("experiments/magnetic/results")
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_path = output_dir / "nv_monte_carlo_summary.csv"
    trials_path = output_dir / "nv_monte_carlo_trials.csv"

    summary_rows: list[dict[str, float | int | bool]] = []
    trial_rows: list[dict[str, float | int]] = []

    print("=" * 78)
    print("BQRC NV MAGNETOMETRY — MONTE CARLO PERFORMANCE EXPERIMENT")
    print("=" * 78)
    print(f"True magnetic-field magnitude : {true_field_nt:.3f} nT")
    print(f"Monte Carlo trials per budget : {trial_count}")
    print(f"Frequency samples             : {len(frequencies_mhz)}")
    print(f"Random seed                   : {seed}")
    print()

    for photon_count in photon_budgets:
        result = run_nv_field_monte_carlo(
            frequencies_mhz=frequencies_mhz,
            true_field_magnitude_nt=true_field_nt,
            reference_photon_count=photon_count,
            trial_count=trial_count,
            seed=seed,
        )

        summary_rows.append(
            {
                "reference_photon_count": photon_count,
                "trial_count": result.trial_count,
                "true_field_nt": true_field_nt,
                "bias_nt": result.bias_nt,
                "empirical_std_nt": result.empirical_std_nt,
                "rmse_nt": result.rmse_nt,
                "theoretical_crlb_nt": result.theoretical_crlb_nt,
                "std_to_crlb_ratio": result.std_to_crlb_ratio,
                "all_fits_successful": result.all_fits_successful,
            }
        )

        for trial_index, estimated_field_nt in enumerate(
            result.estimated_fields_nt,
            start=1,
        ):
            trial_rows.append(
                {
                    "reference_photon_count": photon_count,
                    "trial_index": trial_index,
                    "true_field_nt": true_field_nt,
                    "estimated_field_nt": estimated_field_nt,
                    "error_nt": estimated_field_nt - true_field_nt,
                }
            )

        print(f"Reference photons per frequency : {photon_count:,.0f}")
        print(f"  Bias                         : {result.bias_nt:.6f} nT")
        print(
            f"  Empirical standard deviation : "
            f"{result.empirical_std_nt:.6f} nT"
        )
        print(f"  RMSE                         : {result.rmse_nt:.6f} nT")
        print(
            f"  Theoretical CRLB             : "
            f"{result.theoretical_crlb_nt:.6f} nT"
        )
        print(
            f"  Std / CRLB ratio             : "
            f"{result.std_to_crlb_ratio:.6f}"
        )
        print(
            f"  All fits successful          : "
            f"{result.all_fits_successful}"
        )
        print()

    with summary_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(summary_rows[0]),
        )
        writer.writeheader()
        writer.writerows(summary_rows)

    with trials_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(trial_rows[0]),
        )
        writer.writeheader()
        writer.writerows(trial_rows)

    print("=" * 78)
    print("EXPERIMENT COMPLETE")
    print(f"Summary CSV : {summary_path}")
    print(f"Trials CSV  : {trials_path}")
    print("=" * 78)


if __name__ == "__main__":
    main()
