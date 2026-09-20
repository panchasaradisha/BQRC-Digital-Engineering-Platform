"""Diagnostic reproduction of the Geomag 7.0 shval3 recurrence.

This experiment is intentionally independent of the production BQRC
Legendre/normalization implementation. Its purpose is to determine whether
the historical Geomag recurrence reproduces the official IGRF-14 reference
value for a controlled test point.

Reference test:
    epoch     = 2025.0
    latitude  = 0 deg geodetic
    longitude = 0 deg
    altitude  = 0 km

Official Geomag 7.0 / IGRF-14 result:
    X = 27456.6 nT
    Y = -1926.5 nT
    Z = -15997.4 nT
"""

from __future__ import annotations

from math import cos, pi, sin, sqrt
from pathlib import Path

from bqrc.environment.magnetic.igrf.coefficients import CoefficientKind
from bqrc.environment.magnetic.igrf.parser import load_igrf14_2025

DATASET = Path(
    "data/reference/geomagnetic/igrf14/raw/igrf14coeffs.txt"
)

REFERENCE_RADIUS_KM = 6371.2

# WGS84 constants used by historical Geomag shval3.
A2 = 40680631.59
B2 = 40408299.98


def coefficient_value(
    coefficient_set,
    kind: CoefficientKind,
    degree: int,
    order: int,
) -> float:
    """Return one Gauss coefficient."""

    if kind is CoefficientKind.H and order == 0:
        return 0.0

    return coefficient_set.get(
        kind,
        degree,
        order,
    ).value_nt


def build_gh_array(coefficient_set) -> list[float]:
    """Build the 1-based coefficient ordering used by Geomag shval3."""

    gh = [0.0]

    for degree in range(
        1,
        coefficient_set.maximum_degree + 1,
    ):
        for order in range(
            0,
            degree + 1,
        ):
            gh.append(
                coefficient_value(
                    coefficient_set,
                    CoefficientKind.G,
                    degree,
                    order,
                )
            )

            if order != 0:
                gh.append(
                    coefficient_value(
                        coefficient_set,
                        CoefficientKind.H,
                        degree,
                        order,
                    )
                )

    return gh


def shval3_equivalent(
    latitude_deg: float,
    longitude_deg: float,
    altitude_km: float,
    nmax: int,
    gh: list[float],
) -> tuple[float, float, float]:
    """Python transcription of the relevant Geomag 7.0 shval3 algorithm."""

    dtr = pi / 180.0

    slat = sin(latitude_deg * dtr)

    if (90.0 - latitude_deg) < 0.001:
        clat = 0.0
    else:
        clat = cos(latitude_deg * dtr)

    sl = [0.0] * 14
    cl = [0.0] * 14

    sl[1] = sin(longitude_deg * dtr)
    cl[1] = cos(longitude_deg * dtr)

    # Geodetic -> geocentric conversion used by Geomag.
    aa = A2 * clat * clat
    bb = B2 * slat * slat
    cc = aa + bb
    dd = sqrt(cc)

    r = sqrt(
        altitude_km
        * (
            altitude_km
            + 2.0
            * (
                A2 * clat * clat
                + B2 * slat * slat
            )
            / dd
        )
        + (
            A2 * A2 * clat * clat
            + B2 * B2 * slat * slat
        )
        / cc
    )

    cd = (
        altitude_km
        + dd
    ) / r

    sd = (
        A2 - B2
    ) / dd * slat * clat / r

    old_slat = slat

    slat = (
        slat * cd
        - clat * sd
    )

    clat = (
        clat * cd
        + old_slat * sd
    )

    ratio = REFERENCE_RADIUS_KM / r

    aa = sqrt(3.0)

    p = [0.0] * 119
    q = [0.0] * 119

    p[1] = 2.0 * slat
    p[2] = 2.0 * clat

    p[3] = (
        4.5 * slat * slat
        - 1.5
    )

    p[4] = (
        3.0
        * aa
        * clat
        * slat
    )

    q[1] = -clat
    q[2] = slat

    q[3] = (
        -3.0
        * clat
        * slat
    )

    q[4] = (
        aa
        * (
            slat * slat
            - clat * clat
        )
    )

    for order in range(2, nmax + 1):
        sl[order] = (
            sl[1] * cl[order - 1]
            + cl[1] * sl[order - 1]
        )

        cl[order] = (
            cl[1] * cl[order - 1]
            - sl[1] * sl[order - 1]
        )

    coefficient_index = 1
    n = 0
    m = 1

    npq = (
        nmax * (nmax + 3)
    ) // 2

    x = 0.0
    y = 0.0
    z = 0.0

    rr = 0.0
    fn = 0.0

    for k in range(1, npq + 1):
        if n < m:
            m = 0
            n += 1

            rr = ratio ** (n + 2)

            fn = float(n)

        fm = float(m)

        if k >= 5:
            if m == n:
                aa = sqrt(
                    1.0
                    - 0.5 / fm
                )

                j = (
                    k
                    - n
                    - 1
                )

                p[k] = (
                    (1.0 + 1.0 / fm)
                    * aa
                    * clat
                    * p[j]
                )

                q[k] = aa * (
                    clat * q[j]
                    + slat / fm * p[j]
                )

                sl[m] = (
                    sl[m - 1] * cl[1]
                    + cl[m - 1] * sl[1]
                )

                cl[m] = (
                    cl[m - 1] * cl[1]
                    - sl[m - 1] * sl[1]
                )

            else:
                aa = sqrt(
                    fn * fn
                    - fm * fm
                )

                bb = (
                    sqrt(
                        (fn - 1.0) ** 2
                        - fm * fm
                    )
                    / aa
                )

                cc = (
                    (2.0 * fn - 1.0)
                    / aa
                )

                ii = (
                    k
                    - n
                )

                j = (
                    k
                    - 2 * n
                    + 1
                )

                p[k] = (
                    (fn + 1.0)
                    * (
                        cc
                        * slat
                        / fn
                        * p[ii]
                        - bb
                        / (fn - 1.0)
                        * p[j]
                    )
                )

                q[k] = (
                    cc
                    * (
                        slat * q[ii]
                        - clat / fn * p[ii]
                    )
                    - bb * q[j]
                )

        aa = rr * gh[coefficient_index]

        if m == 0:
            x += aa * q[k]
            z -= aa * p[k]

            coefficient_index += 1

        else:
            bb = rr * gh[coefficient_index + 1]

            cc = (
                aa * cl[m]
                + bb * sl[m]
            )

            x += cc * q[k]

            z -= cc * p[k]

            if clat > 0.0:
                y += (
                    (
                        aa * sl[m]
                        - bb * cl[m]
                    )
                    * fm
                    * p[k]
                    / (
                        (fn + 1.0)
                        * clat
                    )
                )

            else:
                y += (
                    (
                        aa * sl[m]
                        - bb * cl[m]
                    )
                    * q[k]
                    * slat
                )

            coefficient_index += 2

        m += 1

    # Rotate geocentric field back into geodetic coordinates.
    aa = x

    x = (
        x * cd
        + z * sd
    )

    z = (
        z * cd
        - aa * sd
    )

    return x, y, z


def main() -> None:
    """Run the controlled IGRF-14 diagnostic."""

    coefficients = load_igrf14_2025(
        DATASET
    )

    gh = build_gh_array(
        coefficients
    )


    x, y, z = shval3_equivalent(
        latitude_deg=0.0,
        longitude_deg=0.0,
        altitude_km=0.0,
        nmax=coefficients.maximum_degree,
        gh=gh,
    )

    horizontal = sqrt(
        x * x
        + y * y
    )

    total = sqrt(
        horizontal * horizontal
        + z * z
    )

    print(
        "BQRC OFFICIAL-RECURRENCE DIAGNOSTIC"
    )

    print(
        "==================================="
    )

    print()

    print("Point")
    print("-----")
    print("Epoch     : 2025.0")
    print("Latitude  : 0.0 deg")
    print("Longitude : 0.0 deg")
    print("Altitude  : 0.0 km")

    print()

    print("PYTHON TRANSCRIPTION")
    print("--------------------")

    print(
        f"X / North : {x:.6f} nT"
    )

    print(
        f"Y / East  : {y:.6f} nT"
    )

    print(
        f"Z / Down  : {z:.6f} nT"
    )

    print(
        f"H          : {horizontal:.6f} nT"
    )

    print(
        f"F          : {total:.6f} nT"
    )

    print()

    print("OFFICIAL GEOMAG 7.0 TARGET")
    print("--------------------------")
    print("X / North : 27456.6 nT")
    print("Y / East  : -1926.5 nT")
    print("Z / Down  : -15997.4 nT")
    print("H          : 27524.1 nT")
    print("F          : 31835.4 nT")

    print()

    print("DIFFERENCE")
    print("----------")

    print(
        f"dX : {x - 27456.6:+.6f} nT"
    )

    print(
        f"dY : {y - (-1926.5):+.6f} nT"
    )

    print(
        f"dZ : {z - (-15997.4):+.6f} nT"
    )

    print(
        f"dH : {horizontal - 27524.1:+.6f} nT"
    )

    print(
        f"dF : {total - 31835.4:+.6f} nT"
    )


if __name__ == "__main__":
    main()