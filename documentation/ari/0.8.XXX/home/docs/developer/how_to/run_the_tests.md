---
card_label: Run APERO tests
card_icon: fa-solid fa-vial
---

# How to run APERO tests

Use the project test helpers for unit and response tests. The APERO `dev`
fixtures provide default parameters and load `DRS_UCONFIG` without requiring
an APERO profile.

## Focused tests

From the repository root, run a specific test file or test node first:

```bash
PYTHONPATH="apero-core:apero-drs" python -m pytest -q \
    apero-drs/tests/path/to/test_module.py
```

For a single test:

```bash
PYTHONPATH="apero-core:apero-drs" python -m pytest -q \
    apero-drs/tests/path/to/test_module.py::test_behavior
```

## Package suites

```bash
PYTHONPATH="apero-core" python -m pytest -q apero-core/tests
PYTHONPATH="apero-core:apero-drs" python -m pytest -q apero-drs/tests
PYTHONPATH="apero-ri" python -m pytest -q apero-ri/tests
```

Run in the matching Conda environment. For a new scientific algorithm, put
deterministic coverage in `apero-core/tests` where possible. DRS wrappers and
instrument integrations belong in `apero-drs/tests`; interface behavior
belongs in `apero-ri/tests`.

## Test boundaries

Unit tests should not require network access, live databases, large data
assets, or a full APERO profile. Keep such checks in explicit integration
tests. A useful test exercises one behavior, controls its inputs, and checks
numerical outputs and edge cases rather than only checking that a function
returns.
