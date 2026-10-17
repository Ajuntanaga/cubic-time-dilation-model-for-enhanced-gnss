# Cubic Time Dilation Model for Enhanced GNSS

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23436712.svg)](https://doi.org/10.5281/zenodo.23436712)
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

## Status

Both this module's own gravitational-clock measurement (Module XI) and an independent atomic
measurement (*Cubic Time Dimensions in Quantum Mechanics*, 2nd edition revised, §7.1 —
[github.com/Ajuntanaga/cubic-time-dimensions-in-quantum-mechanics](https://github.com/Ajuntanaga/cubic-time-dimensions-in-quantum-mechanics))
have since excluded the cube-root exponent as a literal clock law, in both the kinematic and
gravitational channels. This repository preserves the original 2024 proposal and its module
unchanged; the correction is documented on the live page itself (the status callout at the top of
Module VI) and in the companion manual, not retrofitted into the proposal text.

## Provenance

Module VI was extracted from a larger single-file compendium (17 modules in one HTML artifact) by
tracing which interactive elements and JavaScript the module actually depends on, since the source
file's script isn't organized per module. Verified via a headless Node.js harness: the extracted
script parses cleanly and every element ID referenced resolves.

## Citation

See [CITATION.cff](CITATION.cff) (also used by GitHub's "Cite this repository" button).

## License

MIT, see [LICENSE](LICENSE).
