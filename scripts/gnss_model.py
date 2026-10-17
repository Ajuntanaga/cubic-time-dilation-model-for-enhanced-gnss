"""
GNSS orbital mechanics and relativistic time-dilation backend.

This is the computational backend for Module VI ("Cubic time dilation"), used here to
verify every worked-example number in the v2 revision of the GNSS paper, and intended
to eventually sit behind the live module in place of the inline JS re-derivation.

All functions operate in SI units unless noted. Orbital elements (period, eccentricity,
inclination) are the same ones already published in Module VI's own satellite database
(data/satdb.csv), extracted from the live HTML so this backend and the module agree on
inputs by construction.

Physical model:
  - mu: Earth's standard gravitational parameter (GM), CODATA/IERS value.
  - Semi-major axis from period via Kepler's third law: a = (mu * T^2 / (4 pi^2))^(1/3).
  - Circular-orbit speed (v = sqrt(mu/a)) used as the characteristic orbital speed; for
    eccentric orbits this is supplemented by vis-viva at perigee/apogee where noted.
  - Traditional (GR) combined relativistic rate offset, as actually used operationally
    (ICD-GPS-200, Galileo OS SIS ICD): a constant term from speed + gravitational
    potential, plus a periodic term from eccentricity, Delta_t_r = -2 sqrt(mu a) e sin(E) / c^2.
  - The "cubic" model under test: the same construction with the Lorentz-type exponent
    changed from -1/2 to -1/3, per the 2024 proposal.
"""
from __future__ import annotations
import math
from dataclasses import dataclass

# CODATA 2022 / IERS conventions
C = 299_792_458.0          # m/s, exact
MU_EARTH = 3.986004418e14  # m^3/s^2, WGS-84 / IERS value
R_EARTH = 6_378_137.0      # m, WGS-84 equatorial radius


@dataclass
class Orbit:
    name: str
    constellation: str
    semi_major_axis_m: float   # NOTE: Module VI's own SATDB publishes semi-major axis
                                # directly (km), not orbital period as its column name
                                # might suggest -- confirmed against known values (GPS
                                # ~26,560 km, GLONASS ~25,508 km, Galileo ~29,600 km,
                                # BeiDou MEO ~27,906 km all match on the nose) and by the
                                # period-derived-from-it round-tripping to the textbook
                                # ~11h58m GPS period below.
    eccentricity: float
    inclination_deg: float

    @property
    def period_s(self) -> float:
        """Kepler's third law, inverted: T = 2 pi sqrt(a^3 / mu)."""
        return 2 * math.pi * math.sqrt(self.semi_major_axis_m**3 / MU_EARTH)

    @property
    def mean_motion_rad_s(self) -> float:
        return 2 * math.pi / self.period_s

    def circular_speed_m_s(self) -> float:
        """Speed of an equivalent circular orbit at the same semi-major axis: v = sqrt(mu/a)."""
        return math.sqrt(MU_EARTH / self.semi_major_axis_m)

    def speed_at_true_anomaly(self, nu_rad: float) -> float:
        """Vis-viva speed at a given true anomaly nu for this orbit's (a, e)."""
        a = self.semi_major_axis_m
        e = self.eccentricity
        r = a * (1 - e**2) / (1 + e * math.cos(nu_rad))
        return math.sqrt(MU_EARTH * (2 / r - 1 / a))

    def gravitational_potential_at_r(self, r_m: float) -> float:
        return -MU_EARTH / r_m


def traditional_dilation_factor(v_m_s: float) -> float:
    """dtau/dt = sqrt(1 - v^2/c^2), the standard (k=1/2) special-relativistic factor."""
    beta2 = (v_m_s / C) ** 2
    return math.sqrt(1 - beta2)


def cubic_dilation_factor(v_m_s: float) -> float:
    """dtau/dt = (1 - v^2/c^2)^(1/3), the proposal's cube-root (k=1/3) factor."""
    beta2 = (v_m_s / C) ** 2
    return (1 - beta2) ** (1 / 3)


def taylor_expand(beta2: float, k: float, order: int) -> float:
    """
    (1 - beta^2)^k expanded to the given order in beta^2, via the binomial series:
      (1+x)^k = 1 + k x + k(k-1)/2! x^2 + k(k-1)(k-2)/3! x^3 + ...
    with x = -beta^2. Used to reproduce the paper's own "second-order" and
    "fourth-order" expansion sections with a single, checked implementation instead
    of hand algebra repeated per satellite.
    """
    x = -beta2
    total = 1.0
    coeff = 1.0
    for n in range(1, order + 1):
        coeff *= (k - (n - 1)) / n
        total += coeff * x**n
    return total


def eccentricity_correction_coefficient(k: float) -> float:
    """The (1+2k)/2 coefficient in front of the periodic eccentricity term, generalized to an
    arbitrary dilation exponent k (k=1/2 for GR, matching the standard ICD coefficient of
    exactly 1; k=1/3 for the cubic proposal, giving 5/6). Module VI documents this exact
    generalization and its 5/6-vs-1 split as the module's sharpest non-arbitrary discriminator."""
    return (1 + 2 * k) / 2


def eccentricity_correction_split_s(orbit: Orbit, eccentric_anomaly_rad: float) -> float:
    """The DIFFERENCE between the GR (k=1/2) and cubic (k=1/3) periodic eccentricity
    corrections -- the discriminating observable Module VI's own 'eccentricity clock
    correction' panel reports (its documented 263 ns for QZS-7, 36 ns for QZS-2), as distinct
    from the absolute GR correction itself (see gr_periodic_eccentricity_correction_s)."""
    a = orbit.semi_major_axis_m
    e = orbit.eccentricity
    base = 2 * math.sqrt(MU_EARTH * a) * e * math.sin(eccentric_anomaly_rad) / C**2
    coeff_gr = eccentricity_correction_coefficient(0.5)
    coeff_cubic = eccentricity_correction_coefficient(1 / 3)
    return -(coeff_gr - coeff_cubic) * base


def gr_periodic_eccentricity_correction_s(orbit: Orbit, eccentric_anomaly_rad: float) -> float:
    """
    The real, operationally-applied periodic relativistic correction (ICD-GPS-200 §20.3.3.3.3.1;
    Galileo OS SIS ICD §5.1.4; equivalent forms in GLONASS and BeiDou ICDs):
        Delta_t_r = -2 sqrt(mu a) e sin(E) / c^2
    This is the correction every GNSS receiver actually applies; it is independent of, and
    exists regardless of, whatever constant-exponent model (traditional or cubic) is used for
    the mean rate offset.
    """
    a = orbit.semi_major_axis_m
    e = orbit.eccentricity
    return -2 * math.sqrt(MU_EARTH * a) * e * math.sin(eccentric_anomaly_rad) / C**2


def rate_offset_per_day(dilation_factor: float) -> float:
    """Seconds of proper-time offset accumulated per day of coordinate time, from a
    constant dilation factor (ignores the periodic eccentricity term, which averages to
    zero over an orbit)."""
    return (dilation_factor - 1.0) * 86400.0


def net_weak_field_rate_offset_s_per_day(orbit: Orbit, ground_r_m: float = R_EARTH) -> float:
    """
    The standard weak-field combined (SR + GR) fractional frequency offset of a satellite
    clock relative to a non-rotating clock on the ground (Ashby, "Relativity in the Global
    Positioning System", Living Reviews in Relativity 6, 1 (2003), eq. 2 region):

        Delta_f / f = GM/c^2 (1/r_ground - 1/r_sat) - v_sat^2/(2 c^2)

    Positive means the satellite clock runs FAST relative to the ground clock (weaker
    gravity dominates over its orbital-speed slowdown for GNSS altitudes). For GPS
    (r_sat ~ 26,560 km circular-equivalent), this reproduces Ashby's quoted ~38.6
    microseconds/day -- the textbook number this whole paper is really about getting
    right.
    """
    r_sat = orbit.semi_major_axis_m
    v_sat = orbit.circular_speed_m_s()
    frac = MU_EARTH / C**2 * (1 / ground_r_m - 1 / r_sat) - v_sat**2 / (2 * C**2)
    return frac * 86400.0


def binary_inspiral_strain_amplitude(m1_kg: float, m2_kg: float, f_gw_hz: float,
                                      distance_m: float) -> float:
    """
    Leading-order (Newtonian quadrupole) gravitational-wave strain amplitude from a
    circular-orbit compact binary, as actually used to characterize LIGO/Virgo detections:
        h = (4/d) * (G Mc / c^2)^(5/3) * (pi f_gw / c)^(2/3)
    where Mc is the chirp mass, f_gw is the gravitational-wave frequency (twice the orbital
    frequency), and d is the distance. This is the real physical model for exactly the
    "binary systems and gravitational waves" topic the paper's own appendix gestures at with
    undefined "coherence/decoherence of time signatures" language -- the actual physics is a
    phase-coherent post-Newtonian waveform tracked via matched filtering, not a property of a
    cubed time coordinate.
    """
    G = 6.674e-11
    mc = (m1_kg * m2_kg) ** (3 / 5) / (m1_kg + m2_kg) ** (1 / 5)  # chirp mass
    return (4 / distance_m) * (G * mc / C**2) ** (5 / 3) * (math.pi * f_gw_hz / C) ** (2 / 3)


def solar_mass_kg(n: float = 1.0) -> float:
    return n * 1.98892e30


def load_satdb(csv_path: str) -> list[Orbit]:
    import csv
    orbits = []
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            orbits.append(Orbit(
                name=row["name"],
                constellation=row["constellation"],
                semi_major_axis_m=float(row["sma_km"]) * 1000.0,
                eccentricity=float(row["eccentricity"]),
                inclination_deg=float(row["inclination_deg"]),
            ))
    return orbits
