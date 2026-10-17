# Cubic Time Dilation Model for Enhanced GNSS

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23436711.svg)](https://doi.org/10.5281/zenodo.23436711)
[![DOI badge check](https://github.com/Ajuntanaga/cubic-time-dilation-model-for-enhanced-gnss/actions/workflows/doi-badge-check.yml/badge.svg)](https://github.com/Ajuntanaga/cubic-time-dilation-model-for-enhanced-gnss/actions/workflows/doi-badge-check.yml)

This repository tracks the GNSS proposal and the Chronowave Dynamics compendium module most
directly connected to it, so the two can be versioned together.

## Contents

- `Cubic_Time_Dilation_Model_for_Enhanced_GNSS.pdf` — "Cubic Time Dilation Model for Enhanced GNSS
  Accuracy and Security," a proposal by A. M. Vargas (September 2024). Replaces the traditional
  Lorentz exponent −1/2 with a cube-root exponent −1/3, validated across 1,000 simulations against
  live GNSS constellation data.
- `Module_VI_Cubic_Time_Dilation.html` — Module VI, "Cubic time dilation," extracted standalone
  from the full Chronowave Dynamics Temporal Engine compendium. This is the module the proposal's
  cube-root exponent and satellite-constellation validation are built on. Self-contained: open
  directly in a browser, no build step.
- `Module_VI_Manual.md` — a plain-text companion to the HTML above, covering the same material as
  prose for reading without a browser.
- `Cubic_Time_Dilation_Model_for_Enhanced_GNSS_2nd_edition_revised.pdf` — the 2nd edition. Twelve
  editorial passes over the original, each checked against a small Python backend
  (`scripts/gnss_model.py`) rather than against internal consistency alone: GPS orbital elements
  via Kepler's third law, the standard SR+GR weak-field rate offset (reproducing Ashby 2003's
  38.6 μs/day), the ICD-GPS-200 periodic eccentricity correction, and the GR-vs-cubic correction
  split that reproduces Module VI's own published 263 ns (QZS-7) and 36 ns (QZS-2) figures. The
  revision keeps the original's structure and findings where they hold and documents, in place,
  what it corrects: a factor-of-3 arithmetic error in the original's own worked example, an
  unverifiable "1,000 simulations" claim replaced with a reproducible degeneracy analysis, and the
  same cube-root-exponent exclusion already established for Module XI and the QM paper. A follow-up
  independent review (v1.1.0) found and fixed further issues in the revision itself: a claimed
  derivation that wasn't actually in the text it pointed to, exclusion evidence misdated as newer
  than the original proposal, and a degeneracy argument that overstated its own conclusion.
- `scripts/gnss_model.py`, `scripts/test_gnss_model.py` — the verification backend and its test
  suite (14 tests), each one checked against a real, citable published number rather than only
  against the paper's own internal arithmetic. Run with `pytest scripts/test_gnss_model.py -q`
  from the repo root.
- `data/satdb.csv` — the 145-satellite orbital-element database (semi-major axis, eccentricity,
  inclination) extracted from Module VI's own embedded HTML/JS, used as the backend's real input
  data.

## Status

Both this module's own gravitational-clock measurement (Module XI) and an independent atomic
measurement (*Cubic Time Dimensions in Quantum Mechanics*, 2nd edition revised, §7.1 —
[github.com/Ajuntanaga/cubic-time-dimensions-in-quantum-mechanics](https://github.com/Ajuntanaga/cubic-time-dimensions-in-quantum-mechanics))
have since excluded the cube-root exponent as a literal clock law, in both the kinematic and
gravitational channels. This repository preserves the original 2024 proposal's claims unchanged;
the correction is documented on the live page itself (the status callout at the top of Module VI)
and in the companion manual, not retrofitted into the proposal text. Module VI has since received
formatting and bug fixes (layout, a live-updating header equation, a corrected satellite speed, and
a fixed pseudorandom generator in the noise demonstration) that do not change any of its physics
claims or published numbers.

## Provenance

Module VI was extracted from a larger single-file compendium (17 modules in one HTML artifact) by
tracing which interactive elements and JavaScript the module actually depends on, since the source
file's script isn't organized per module. Verified via a headless Node.js harness: the extracted
script parses cleanly and every element ID referenced resolves.

## Citation

See [CITATION.cff](CITATION.cff) (also used by GitHub's "Cite this repository" button).

## License

MIT, see [LICENSE](LICENSE).
