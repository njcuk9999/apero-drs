# apero-core tests

This directory contains fast unit tests for pure or low-dependency helpers in
`aperocore`.

## Scope

- hash/text helpers in `aperocore.base.drs_base`
- gaussian and NaN-safe math helpers in `aperocore.math`
- general numerical helpers in `aperocore.math.gen_math`

## Run

```bash
cd /scratch2/spirou/drs-bin/apero-drs-spirou-08XXX
PYTHONPATH="/scratch2/spirou/drs-bin/apero-drs-spirou-08XXX/apero-core" \
python -m pytest -q apero-core/tests
```

## Notes

- Tests are designed to avoid network, database, and large data dependencies.
- Keep new tests deterministic and focused on one function behavior each.

