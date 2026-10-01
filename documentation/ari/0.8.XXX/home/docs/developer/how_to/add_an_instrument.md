---
card_label: Add an instrument
card_icon: fa-solid fa-satellite-dish
---

# How to add an instrument

An instrument is not a single plugin file: it is a coordinated set of
constants, keywords, file and recipe definitions, science behavior, and tests.
The existing SPIROU and NIRPS instrument packages are the reference.

## Main components

| Component | Location | Responsibility |
| --- | --- | --- |
| Instrument package | `apero-drs/apero/instruments/<instrument>/` | Instrument-specific config, constants, keywords, recipes, and file definitions. |
| Instrument selection | `apero-drs/apero/instruments/select.py` and package setup | Makes the instrument discoverable to configuration and startup code. |
| Recipe entry points | `apero-drs/apero/recipes/<instrument>/` | Recipe execution wrappers for this instrument. |
| Science differences | `apero-drs/apero/science/` or `apero-core/aperocore/science/` | Instrument-independent algorithms stay in core; APERO-specific adaptation stays in DRS. |
| Tests | `apero-drs/tests/` and `apero-core/tests/` | Deterministic behavior and instrument contract checks. |

## Build in dependency order

1. Add the instrument package and register its configuration module.
2. Define constants in `default/constants.py`, then override every constant
   for every instrument, including the new one.
3. Define internal header keywords in `default/keywords.py` and map each card
   name for every instrument.
4. Add file definitions and FITS data models; validate raw header matching
   and output extension schemas.
5. Add recipe definitions, recipe entry points, and instrument sequences.
6. Reuse shared science functions where behavior matches. Put only genuine
   instrument differences in instrument-specific code or constants.
7. Add tests, update installation/profile metadata, and document each recipe,
   tool, sequence, and file family.

Keep matching workflows aligned across instruments. If two instruments do
the same processing steps, their recipe structure should be the same; encode
instrument differences in the lower-level behavior.

## Validate

Run the package tests from the repository root:

```bash
PYTHONPATH="apero-core:apero-drs" python -m pytest -q apero-drs/tests
```

Then run `apero_validate.py` with a clean profile for the new instrument and
run the documentation generator. Check that constants and keywords have no
missing overrides and that every sequence resolves to defined recipes.
