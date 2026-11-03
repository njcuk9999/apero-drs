# apero-ri tests

This directory contains unit tests for authentication, permissions, and
utility modules used by APERO RI.

## Scope

- auth and permissions logic
- fail-report grouping/token helpers
- download-tracker settings and counters
- backup/query utility helper functions

## Run

```bash
cd /scratch2/spirou/drs-bin/apero-drs-spirou-08XXX
PYTHONPATH="apero-core:apero-drs:apero-ri" \
python -m pytest -q apero-ri/tests
```

## Notes

- Tests should use temporary directories (`tmp_path`) for file-backed state.
- Avoid network/remote-provider calls in unit tests.
- Use the RI environment for web dependencies; APERO source paths are needed
	by tests using `apero.dev` for profile-free setup.

## Static correctness audit

From the repository root, run the same focused Ruff audit used for the other
packages (Ruff is available in the `apero-drs` development extra):

```bash
python -m ruff check --isolated --no-respect-gitignore \
		--config 'include = ["*.py"]' --select F63,F7,F82,F901,E9 \
		apero-core apero-drs apero-ri
```

This checks undefined names, syntax, and invalid control flow without applying
formatting or style rewrites. Runtime API mismatches still need behavior tests.

