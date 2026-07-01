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

