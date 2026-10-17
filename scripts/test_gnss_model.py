"""
Verification tests for the GNSS backend, grounded against published, citable numbers
rather than internal consistency alone. Every assertion here traces to a real source:
Ashby 2003 for the textbook GPS relativity figures, the ICD-GPS-200 periodic-correction
formula, and the satellite orbital elements already published in Module VI's own
database. If these fail, nothing downstream in the v2 paper can be trusted.
"""
import csv
import math
import os
import pytest

from gnss_model import (
    C, MU_EARTH, R_EARTH, Orbit,
    traditional_dilation_factor, cubic_dilation_factor, taylor_expand,
    gr_periodic_eccentricity_correction_s, eccentricity_correction_split_s,
    rate_offset_per_day, net_weak_field_rate_offset_s_per_day, load_satdb,
    binary_inspiral_strain_amplitude, solar_mass_kg,
)

DATA = os.path.join(os.path.dirname(__file__), "..", "data", "satdb.csv")


def gps_orbit():
    """A representative GPS (NAVSTAR) orbit from the real database: period ~11h58m,
    near-circular, inclination ~55 deg -- the Block IIR/IIF design values."""
    orbits = load_satdb(DATA)
    navstars = [o for o in orbits if o.name.startswith("NAVSTAR")]
    assert navstars, "GPS satellites missing from satdb.csv"
    return navstars[0]


def test_satdb_loads_145_satellites():
    """Sanity check on the data pipeline itself: Module VI's own HTML documents a
    145-satellite array; the extracted CSV must match."""
    orbits = load_satdb(DATA)
    assert len(orbits) == 145


def test_kepler_third_law_gps_semi_major_axis():
    """GPS semi-major axis is a well-known, oft-quoted figure: ~26,560 km (not to be
    confused with altitude ~20,180 km, which excludes Earth's radius)."""
    o = gps_orbit()
    a_km = o.semi_major_axis_m / 1000.0
    assert 26_500 < a_km < 26_650, f"got {a_km:.1f} km, textbook value is ~26,560 km"


def test_gps_circular_speed_matches_known_value():
    """GPS orbital speed is commonly quoted as ~3.87 km/s (e.g. Module VI's own UI
    chip: 'GPS BIIA-10 . 3.874 km/s')."""
    o = gps_orbit()
    v_km_s = o.circular_speed_m_s() / 1000.0
    assert 3.85 < v_km_s < 3.90, f"got {v_km_s:.3f} km/s, expected ~3.87 km/s"


def test_sr_only_slowdown_matches_textbook_minus_7_microseconds_per_day():
    """The special-relativistic (velocity) part alone is the textbook '-7 microseconds
    per day' figure quoted in essentially every popular account of GPS relativity
    (e.g. Ashby 2003 section 1; Pogge, Ohio State, 'Real-World Relativity')."""
    o = gps_orbit()
    v = o.circular_speed_m_s()
    f = traditional_dilation_factor(v)
    offset_us_per_day = rate_offset_per_day(f) * 1e6
    assert -7.3 < offset_us_per_day < -7.0, f"got {offset_us_per_day:.2f} us/day, textbook is -7.2 us/day"


def test_net_weak_field_offset_matches_ashby_38_point_6_microseconds_per_day():
    """The combined SR+GR net offset is Ashby's (2003) headline number: GPS satellite
    clocks run fast by about 38.6 microseconds/day relative to the ground, which is why
    GPS satellite clocks are built with their frequency offset by -4.465e-10 before
    launch. This is the single most load-bearing real-world check in this whole paper."""
    o = gps_orbit()
    offset_us_per_day = net_weak_field_rate_offset_s_per_day(o) * 1e6
    assert 38.0 < offset_us_per_day < 39.2, f"got {offset_us_per_day:.2f} us/day, Ashby quotes 38.6 us/day"


def test_cubic_model_gives_a_different_sr_only_slowdown():
    """Sanity check that the two models under comparison actually differ at GPS speeds
    -- otherwise there would be nothing to validate in the first place."""
    o = gps_orbit()
    v = o.circular_speed_m_s()
    trad = rate_offset_per_day(traditional_dilation_factor(v))
    cubic = rate_offset_per_day(cubic_dilation_factor(v))
    assert trad != pytest.approx(cubic, rel=1e-6)
    # cubic's -1/3 exponent makes |offset| smaller in magnitude than -1/2's, since the
    # cube root of (1-x) is closer to 1 than the square root is, for small x > 0.
    assert abs(cubic) < abs(trad)


def test_taylor_expansion_matches_closed_form_at_second_order():
    """The module's own second-order expansion arithmetic, done once here and checked
    against the exact closed form, rather than re-derived by hand per satellite as the
    original paper does ten times over."""
    beta2 = 1.5e-10
    exact = (1 - beta2) ** 0.5
    approx2 = taylor_expand(beta2, 0.5, order=2)
    # at this tiny beta^2, 2nd order should already match the exact value to >12 digits
    assert approx2 == pytest.approx(exact, rel=1e-10)


def test_taylor_expansion_converges_with_order():
    """Higher order should get closer to the exact value, not just differ from it --
    guards against a sign error in the binomial recursion."""
    beta2 = 1e-4  # deliberately large to make truncation error visible
    exact = (1 - beta2) ** (1 / 3)
    err2 = abs(taylor_expand(beta2, 1 / 3, order=2) - exact)
    err4 = abs(taylor_expand(beta2, 1 / 3, order=4) - exact)
    assert err4 < err2


def test_periodic_eccentricity_correction_sign_and_scale_qzs7():
    """QZS-7's extreme eccentricity (e=0.721, a transfer orbit, per Module VI's own
    documented caveat) should give an eccentricity correction many times larger than a
    near-circular GPS satellite's -- same formula, real published eccentricities."""
    orbits = load_satdb(DATA)
    qzs7 = next(o for o in orbits if "QZS-7" in o.name)
    gps = gps_orbit()
    dt_qzs7 = gr_periodic_eccentricity_correction_s(qzs7, eccentric_anomaly_rad=math.pi / 2)
    dt_gps = gr_periodic_eccentricity_correction_s(gps, eccentric_anomaly_rad=math.pi / 2)
    assert abs(dt_qzs7) > 5 * abs(dt_gps)


def test_eccentricity_split_reproduces_module_vi_qzs7_and_qzs2():
    """Module VI documents the GR-vs-cubic eccentricity correction split as 263 ns for QZS-7
    (e=0.721) and 36 ns for QZS-2 (e=0.075). This is a DIFFERENT quantity from the absolute
    GR correction (gr_periodic_eccentricity_correction_s) -- it's the discriminating split
    between the two competing models' coefficients, 1 vs 5/6. Reproducing both published
    numbers, at the eccentric anomaly that maximizes sin(E), confirms the split formula is
    right, not just internally self-consistent."""
    orbits = load_satdb(DATA)
    qzs7 = next(o for o in orbits if "QZS-7" in o.name)
    qzs2 = next(o for o in orbits if "QZS-2" in o.name)
    split_qzs7_ns = abs(eccentricity_correction_split_s(qzs7, math.pi / 2)) * 1e9
    split_qzs2_ns = abs(eccentricity_correction_split_s(qzs2, math.pi / 2)) * 1e9
    assert split_qzs7_ns == pytest.approx(263, rel=0.03), f"got {split_qzs7_ns:.1f} ns"
    assert split_qzs2_ns == pytest.approx(36, rel=0.05), f"got {split_qzs2_ns:.1f} ns"


def test_eccentricity_split_scales_as_e_sqrt_a():
    """The eccentricity-correction split formula is proportional to e*sqrt(a), not to e alone.
    QZS-2 and NAVSTAR 43 have very different altitudes (a), so this ratio check only passes if
    the sqrt(a) dependence is actually right, not just the e dependence."""
    orbits = load_satdb(DATA)
    navstar = next(o for o in orbits if o.name == "NAVSTAR 43 (USA 132)")
    qzs2 = next(o for o in orbits if "QZS-2" in o.name)
    s_n = abs(eccentricity_correction_split_s(navstar, math.pi / 2))
    s_2 = abs(eccentricity_correction_split_s(qzs2, math.pi / 2))
    predicted_ratio = (qzs2.eccentricity / navstar.eccentricity) * math.sqrt(
        qzs2.semi_major_axis_m / navstar.semi_major_axis_m
    )
    assert s_2 / s_n == pytest.approx(predicted_ratio, rel=1e-6)
    assert s_2 / s_n == pytest.approx(9.08, rel=0.01)


def test_beta2_phi_degeneracy_reproduces_module_vi_independently():
    """Reproduces Module VI's own documented r(beta^2, Phi) = 0.968 across the 145-satellite
    array, via a different computational path (perigee vis-viva speed and potential, rather
    than whatever Module VI's own JS uses) -- an independent check, not a copy."""
    orbits = load_satdb(DATA)
    beta2s, phis = [], []
    for o in orbits:
        v = o.speed_at_true_anomaly(0.0)  # perigee
        r_perigee = o.semi_major_axis_m * (1 - o.eccentricity)
        beta2s.append(v**2 / C**2)
        phis.append(o.gravitational_potential_at_r(r_perigee))
    n = len(beta2s)
    mx, my = sum(beta2s) / n, sum(phis) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(beta2s, phis))
    sx = math.sqrt(sum((x - mx) ** 2 for x in beta2s))
    sy = math.sqrt(sum((y - my) ** 2 for y in phis))
    r = cov / (sx * sy)
    assert abs(r) == pytest.approx(0.968, abs=0.01)


def test_original_papers_toy_example_was_off_by_a_factor_of_three():
    """Regression test locking in a finding from the v2 revision: the first edition's own
    worked example at v=3000 m/s (Theoretical Foundation, 'Mathematical Derivation and
    Justification') reports gamma-1 ~ 1.5e-10 (traditional) and ~1e-10 (cubic). Recomputed
    directly, both figures are too large by very nearly a factor of 3. This test exists so
    that fact can't silently drift if the model functions are ever refactored."""
    v = 3000.0
    beta2 = (v / C) ** 2
    trad = taylor_expand(beta2, -1 / 2, order=1) - 1.0
    cubic = taylor_expand(beta2, -1 / 3, order=2) - 1.0
    assert trad == pytest.approx(5.007e-11, rel=1e-3)
    assert cubic == pytest.approx(3.338e-11, rel=1e-3)
    original_trad_claim = 1.5e-10
    original_cubic_claim = 1e-10
    assert original_trad_claim / trad == pytest.approx(3.0, abs=0.01)
    assert original_cubic_claim / cubic == pytest.approx(3.0, abs=0.01)


def test_quadrupole_strain_matches_gw150914_order_of_magnitude():
    """GW150914 (LIGO's first detection, Abbott et al. 2016, Phys. Rev. Lett. 116, 061102):
    two black holes of ~36 and ~29 solar masses, merging at ~410 Mpc, with a peak strain
    around 1.0e-21 near 150 Hz (the frequency rising toward merger from ~35 Hz). The leading
    Newtonian quadrupole formula is not expected to be precise this close to merger (that
    regime needs full numerical relativity), but should land within an order of magnitude --
    a basic sanity check that 'where the real physics attaches' is at least roughly located
    before using this formula for anything in the paper."""
    Mpc_to_m = 3.0857e22
    h = binary_inspiral_strain_amplitude(
        m1_kg=solar_mass_kg(36), m2_kg=solar_mass_kg(29),
        f_gw_hz=150.0, distance_m=410 * Mpc_to_m,
    )
    assert 1e-22 < h < 1e-20, f"got {h:.3e}, expected order 1e-21 (GW150914 peak ~1.0e-21)"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
