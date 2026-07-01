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
PYTHONPATH="/scratch2/spirou/drs-bin/apero-drs-spirou-08XXX/apero-ri" \
python -m pytest -q apero-ri/tests
```

## Notes

- Tests should use temporary directories (`tmp_path`) for file-backed state.
- Avoid network/remote-provider calls in unit tests.

