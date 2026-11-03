# apero-drs tests

This directory starts with fast unit tests for pure helper functions in
`apero.core`.

## Scope

- object-name normalization and safe filename helpers
- coordinate formatting/math helper functions in astrometrics
- null-value and parsing utility functions

## Run

```bash
cd /scratch2/spirou/drs-bin/apero-drs-spirou-08XXX
PYTHONPATH="/scratch2/spirou/drs-bin/apero-drs-spirou-08XXX/apero-core:/scratch2/spirou/drs-bin/apero-drs-spirou-08XXX/apero-drs" \
python -m pytest -q apero-drs/tests
```

## Notes

- Tests in this folder should prefer pure helper functions first.
- Add integration tests separately when external assets/services are required.

## Static correctness audit

Ruff is included in the package's `dev` extra. From the repository root,
install it in the same interpreter used to run APERO, then scan all Python
files without importing recipes or accessing a profile database:

```bash
python -m pip install 'ruff>=0.17,<0.18'
python -m ruff check --isolated --no-respect-gitignore \
	--config 'include = ["*.py"]' --select F63,F7,F82,F901,E9 \
	apero-core apero-drs apero-ri
```

The selected rules cover undefined names, invalid `__all__` entries,
local-variable misuse, malformed conditions, invalid control flow, and syntax
errors. This deliberately does not apply formatting or unused-import fixes.
Static checks do not prove that runtime branches initialize every value, or
that calls use the correct API; keep behavioral tests alongside this scan.

Known outstanding findings: the unregistered TODO scaffold
[apero_skycorr_nirps_he.py](../apero/recipes/nirps_he/apero_skycorr_nirps_he.py)
contains seven undefined references to `infiles`, `infile`, and `fiber`.
It has no implemented sky-correction algorithm. These diagnostics remain
visible rather than being suppressed or filled with invented inputs.

The error-path regressions can be run independently:

```bash
PYTHONPATH="apero-core:apero-drs" python -m pytest -q \
	apero-drs/tests/test_undefined_name_error_paths.py
```

