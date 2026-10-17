# Cubic Time Dilation — Module VI Manual

A plain-text companion to `Module_VI_Cubic_Time_Dilation.html`, the standalone extract of Module VI
from the Chronowave Dynamics Temporal Engine. This is the module behind the 2024 proposal *Cubic
Time Dilation Model for Enhanced GNSS*: the cube-root exponent (1−β²)^(−1/3) proposed in place of
the standard Lorentz factor, tested against the full operational GNSS constellation.

**Status.** Both this module's own gravitational-clock measurement (Module XI) and an independent
atomic measurement (*Cubic Time Dimensions in Quantum Mechanics*, 2nd ed. revised, §7.1) have since
excluded the cube-root exponent as a literal clock law, in both the kinematic and gravitational
channels. The module's physics claims and conclusions are unchanged from the original compendium
module; the status callout on the live page states the exclusion directly, and the exponent's one
remaining theoretical (not yet experimentally confirmed) recurrence — in an untested quantum limit
of strong-field radiated power, not a clock rate — is documented in the compendium's *Where Cubic
Time Lives* note. The module has since received formatting and bug fixes (layout, a live-updating
header equation, a corrected satellite speed, and a fixed pseudorandom generator in the noise
demonstration) that do not change any of its numbers or claims.

Generated 2026-10-17 from the Compendium fork, ported from the full compendium's `Manual.md`.
Equation names below are pointers back to the live page; the LaTeX itself renders only there.

---

## Cubic time dilation

> The Lorentz factor, *taken to the cube root*

The GNSS proposal replaced the traditional exponent −1/2 with −1/3, originally claimed on the strength of 1,000 simulations against live constellation data — a claim excluded by independent measurement elsewhere in this project (status above). At satellite speeds the models differ by parts in 10^11 — exactly the regime where nanoseconds become meters of position error. Push the slider relativistic and watch the two models tear apart.

The array is **every operational GNSS satellite**: 145 birds across GPS (G), GLONASS (R), Galileo (E), BeiDou (C), QZSS (J) and NavIC (I), RINEX letters and all, from the live SATCAT (OPS status "+"; snapshot epoch stamped in the source line; geometry a, e, i MEASURED from apsides and period). Orbital phases are ASSUMED until *Fetch live almanac* succeeds, when CelesTrak epochs and mean anomalies make them MEASURED; propagation is two-body Kepler (ASSUMED — honest for r, v, β; not for sky position). The five regression forms now interrogate the real array; BeiDou's GEO/IGSO/MEO spread plus ground stations breaks the β²/Φ degeneracy inside the data itself. The per-satellite card carries the framework's sharpest non-arbitrary discriminator: the **eccentricity clock correction**, Δt = −(1+2k)/2 · 2√(μa) e sin E / c² — the periodic term every receiver measures and applies. Its coefficient is *derived*: GR's k = ½ gives 1; the cubic k = ⅓ gives 5/6 — a 17% amplitude split, 36 ns on QZS-2's e = 0.075 orbit. The module can say no, satellite by satellite. The array's strongest lever is larger still and needs its caveat stated: **QZS-7** is catalogued at e = 0.721, which puts the split at **263 ns** — seven times QZS-2's. That is a *transfer* orbit, not an operational one, so the figure is real but temporary; it shrinks to the QZS-2 value once the bird is on station. Worth knowing in both directions: while it is climbing it is the sharpest discriminator in the constellation, and any fit that leans on it is leaning on a number with an expiry date.

**The live almanac, and why losing it costs nothing.** The fetch is this module's most fragile part and the first thing to break. A page opened from a file:// path has a null origin and browsers refuse cross-origin requests from it before CORS is consulted; served over http it still depends on the endpoint's headers; and an egress policy can refuse the host outright. The panel now names *which* of those happened instead of printing one sentence for all of them, and offers two paths that need no network at all: paste the GP JSON or 3-line TLE, or open a downloaded file (an ordinary file read — no origin, no CORS, no policy). Downloading from CelesTrak in the browser is a normal navigation and always works. **But the more useful answer is that live data would not improve the measurement, and that is provable rather than hopeful.** Vis-viva gives v² = GM(2/r − 1/a), so β² = 2Φ − GM/ac²: at fixed semi-major axis the two regressors are *affinely dependent with slope exactly 2*, and phase moves r and nothing else. A sample therefore slides along that line, and a bi-linear model containing both regressors absorbs the slide exactly. Checked across all 145 orbits the slope is 2 to 3×10^−12, and rotating every phase in the array through a full turn moves k̂ by at most **1.8×10^−7** — 10^−4 percent of the 0.1667 split under test. What separates β² from Φ is the GM/ac² offset: different shells, and the ground stations at an *a* no satellite has. That is the same fact the collinearity number reports from the other end.

Live phases therefore change exactly one thing, and the card now says so in different ink. The eccentricity correction's *amplitude* is real (a and e are MEASURED), but its *"now"* value goes as sin E, and with phases seeded from the catalogue number that figure swings the full ±amplitude as the seed is re-rolled: on QZS-1R it spans −218 to +218 ns. Printing a prediction and an arbitrary number in the same ink was the real defect here; the fetch failing was only what made it visible.

**The degeneracy, measured rather than asserted.** Among the 145 birds the two predictors are nearly one column: r(β², Φ) = 0.968, variance inflation 15.9, because every operational orbit is near-circular and so β² and Φ are locked together by the vis-viva relation. Adding 40 ground stations — Φ at the geoid, β² three decades below the MEO shell — takes r to −0.780 and the VIF to 2.55. OLS then predicts the satellite-only fit should be worse on k by √(VIF ratio × n ratio) ≈ 2.6×, and the table's satellites-only row collects it: about 2.8× the error at every noise level. And past σ ≈ 20 ps it returns k̂ = 0.393 and picks *cubic* from data generated by GR, while the full fit is still right. Two independent numbers — a correlation and an error ratio — describing the same geometry, which is the check that they are both measuring something real.

**Equations on this page** (rendered live in the HTML, `#gnss`):
- Two dilation models
