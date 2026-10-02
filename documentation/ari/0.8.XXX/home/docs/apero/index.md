---
card_label: APERO
card_icon: fa-solid fa-microscope
related:
  - developer
  - reference
  - algorithms
  - glossary
---

# APERO

APERO is the data-reduction pipeline for SPIRou and NIRPS: it turns raw exposures into calibrated, science-ready spectra.

Most reductions are run as a single YAML-driven batch: `apero_processing` (and `apero_queue` in APERO 0.8) reads a **sequence** - an ordered list of recipes for one instrument - and runs every recipe it names, in order, for a whole night or object. You can also call any **recipe** directly for a single step, which is useful for reprocessing one file or debugging a stage in isolation.

Alongside recipes, APERO ships a wide range of **tools** for setup, inspection, and maintenance - see Tools below.

This section is generated from APERO 0.8.XXX's recipe and file definitions; it is always in sync with the running code.

| Name | Description |
| --- | --- |
| [Recipes](recipes/) | Individual reduction steps. Compare availability by instrument, then open the instrument-specific recipe page for arguments, outputs, and plots. |
| [Tools](tools/) | User and developer commands for setup, inspection, processing, and maintenance. |
| [Instruments](instruments/) | Instrument-specific sequences, recipes, tools, and the complete file-definition tables. |
