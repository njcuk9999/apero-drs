---
card_label: Sequences
card_icon: fa-solid fa-diagram-project
related:
  - apero/instruments/spirou/recipes/
  - apero/instruments/spirou/file_definitions/
  - glossary
---

# Sequences (SPIROU)

`apero_processing` (and `apero_queue` in APERO 0.8) reads a sequence and runs its recipes, for this instrument, in the order listed below - that ordering, not anything implicit in the recipe code, is what defines a reduction run. Use these pages to see what APERO actually does to your data, and in what order.

| Name | Description |
| --- | --- |
| [pp_seq](pp_seq) | Run apero_preprocess on every raw fits file. |
| [pp_seq_opt](pp_seq_opt) | Run apero_preprocess on specific files (based on DPRTYPE). |
| [full_seq](full_seq) | Run the full set of files through the full process. |
| [limited_seq](limited_seq) | Run a limited set of files through the full process. |
| [ref_seq](ref_seq) | Run all reference calibration steps. |
| [calib_seq](calib_seq) | Run all nightly calibration steps. |
| [tellu_seq](tellu_seq) | Run all nightly hot star telluric calibrations steps. |
| [science_seq](science_seq) | Run all nightly science target steps. |
| [quick_seq](quick_seq) | Run all science targets extractions but in "quick" mode (i.e. |
| [blank_seq](blank_seq) | Ordered recipe sequence for this instrument. |
| [eng_seq](eng_seq) | Run apero_extract on specific files (based on DPRTYPE). |
| [lbl_seq](lbl_seq) | Run the lbl recipes inside apero. |
