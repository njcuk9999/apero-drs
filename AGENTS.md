# APERO Agent Guidelines

## Package layout

- `apero-core/aperocore` contains reusable, DRS-independent functionality.
  Do not add imports from `apero` or APERO recipe/configuration code here.
- `apero-drs/apero` is the data-reduction pipeline. Keep dependencies layered:
  `apero.base` has no APERO imports; `apero.lang` may depend only on `base`;
  core modules must depend only on lower-level core, language, and base modules.
  Higher-level `io`, `plotting`, `recipes`, `science`, and `tools` modules may
  depend on the layers below them.
- `apero-ri/apero_ri` is the Flask reduction interface. It may use `aperocore`
  and `apero`, but interface-specific code belongs in the RI package.

## Python code

@.github/instructions/python-apero.instructions.md

## APERO recipe structure

- Main APERO recipe scripts should generally define only `main` and
  `__main__`. Put reusable helpers in an appropriate module under
  `apero.tools.module`, `apero.core`, `apero.io`, or another shared package
  location.
- Do not write fallback/dual-path code to support an old file, database, or
  calibration layout alongside the new one (e.g. `if is_combined: ... else:
  <old behaviour>`). APERO profiles are reset/rebuilt from a clean state
  between versions, so the pipeline never needs to read data produced by a
  previous code version. Change the code and its callers to the new
  behaviour outright; do not keep the old path "just in case".

## APERO v0.8 tests

- Use `apero.dev` for every unit test and response test. It provides the
  default parameters and loads `DRS_UCONFIG` without accessing an APERO
  profile.
- Keep unit tests deterministic and focused on one behavior. Do not require
  network access, databases, or large data assets; place such coverage in
  separate integration tests.
- Run the narrow package suite from the repository root:

  ```bash
  PYTHONPATH="apero-core" python -m pytest -q apero-core/tests
  PYTHONPATH="apero-core:apero-drs" python -m pytest -q apero-drs/tests
  PYTHONPATH="apero-ri" python -m pytest -q apero-ri/tests
  ```

## APERO RI

- Apply the instructions in `apero-ri/.github/instructions/` for every RI
  change. Read `ari-new-page.instructions.md` and
  `ari-tables.instructions.md` before adding a page or table.
- Keep permissions in `apero_ri/resources/pages.yaml` and `groups.yaml`.
  Enforce access in the Python route or view helper, never only in a template.
- Put instrument-specific settings in
  `apero_ri/resources/aprofile_instruments/*.yaml`, not hard-coded Python.
  Keep the v7/v8 SPIROU and NIRPS configuration key sets aligned.
- Use `apero_ri/ari_api/` helpers for internal ARI API calls rather than raw
  `requests` calls. Register async tasks in `apero_ri/tasks/__init__.py`.