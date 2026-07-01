# APERO Core (`aperocore`)

`apero-core` contains reusable core functionality shared by APERO packages.

## Install (editable)

```bash
pip install -U -e ./apero-core
```

## Package use

```python
import aperocore
```

## Testing

Unit tests live in `apero-core/tests`.

```bash
cd /scratch2/spirou/drs-bin/apero-drs-spirou-08XXX
PYTHONPATH="/scratch2/spirou/drs-bin/apero-drs-spirou-08XXX/apero-core" \
python -m pytest -q apero-core/tests
```

See `apero-core/tests/README.md` for scope and conventions.

