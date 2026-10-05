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

Alongside recipes, APERO ships user and developer tools for setup, inspection, processing, and maintenance. Use the reference table below to open the topic and instrument section directly, without an intermediate instrument landing page.

This section is generated from APERO 0.8.XXX's recipe and file definitions; it is always in sync with the running code.

| Instrument | Reference | What you will find |
| --- | --- | --- |
| All instruments | [User tools](/docs/apero/user_tools) | Commands for setting up, inspecting, and processing APERO reductions. |
| All instruments | [Developer tools](/docs/apero/dev_tools) | Commands for maintaining APERO configurations, definitions, and language resources. |
| SPIROU | [Sequences](/docs/apero/instruments/spirou/sequences) | Ordered workflows that processing runs for this instrument. |
| SPIROU | [Recipes](/docs/apero/instruments/spirou/recipes) | Instrument-specific processing steps and their arguments, outputs, and plots. |
| SPIROU | [File definitions](/docs/apero/instruments/spirou/file_definitions) | One searchable table of the instrument's raw, intermediate, and output files. |
| NIRPS-HA | [Sequences](/docs/apero/instruments/nirps_ha/sequences) | Ordered workflows that processing runs for this instrument. |
| NIRPS-HA | [Recipes](/docs/apero/instruments/nirps_ha/recipes) | Instrument-specific processing steps and their arguments, outputs, and plots. |
| NIRPS-HA | [File definitions](/docs/apero/instruments/nirps_ha/file_definitions) | One searchable table of the instrument's raw, intermediate, and output files. |
| NIRPS-HE | [Sequences](/docs/apero/instruments/nirps_he/sequences) | Ordered workflows that processing runs for this instrument. |
| NIRPS-HE | [Recipes](/docs/apero/instruments/nirps_he/recipes) | Instrument-specific processing steps and their arguments, outputs, and plots. |
| NIRPS-HE | [File definitions](/docs/apero/instruments/nirps_he/file_definitions) | One searchable table of the instrument's raw, intermediate, and output files. |
