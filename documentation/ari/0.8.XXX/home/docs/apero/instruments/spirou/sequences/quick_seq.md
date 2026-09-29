---
card_label: quick_seq
card_icon: fa-solid fa-diagram-project
---

# quick_seq

**Instrument:** SPIROU

Run all science targets extractions but in "quick" mode (i.e. no BERV calculation,
no flat or thermal correction, no 1D files, no processing of A,B or C fibers)
therefore only good for getting extracted SNR in the AB fiber only.

These files cannot be used in the telluric or RV process.
These files will have suffix "q2ds" not "e2ds".

## Recipes in this sequence

| ORDER | RECIPE | SHORTNAME | RECIPE KIND | REF RECIPE | FILTERS | ARGS |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | apero_extract_spirou.py | EXTQUICK | extract-quick | No | KW_OBJNAME: SCIENCE_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, POLAR_DARK, POLAR_FP | {files}=[OBJ_DARK, OBJ_FP, POLAR_DARK, POLAR_FP] |
