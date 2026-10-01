---
card_label: Developer environments
card_icon: fa-solid fa-terminal
---

# APERO developer environments

This guide describes a reproducible local workflow for developing v0.8. Use
an isolated environment for each APERO major version; do not install APERO's
scientific stack into Conda `base`.

## Conda environment

```bash
conda create --name apero-env-08 python=3.12
conda activate apero-env-08
```

Keep using the same environment for installation, tests, and generation. In
VS Code, select that environment as the Python interpreter as well.

## Clone the code

For a development checkout, clone the APERO monorepo and LBL. Choose the
branch/tag deliberately; do not assume `main` is the release you are targeting.

```bash
git clone git@github.com:njcuk9999/apero-drs.git
cd apero-drs
git switch --create my-feature

git clone git@github.com:njcuk9999/lbl.git ../lbl
```

Use `git status` before editing and before committing. Keep unrelated local
changes intact; use small topic branches and review the staged diff.

## Editable installs

From the directory containing the repositories:

```bash
python -m pip install --upgrade pip
python -m pip install --editable ./apero-drs/apero-core
python -m pip install --editable ./lbl
python -m pip install --editable './apero-drs/apero-drs[dev]'
```

Editable installs make code changes visible without reinstalling. The
`[dev]` extra installs developer/test dependencies. If a shell reports a
stale or conflicting import, check `python -c "import apero; print(apero.__file__)"`
and confirm the selected interpreter is the intended one.

## Virtual environments

A standard Python venv is also possible when all required system libraries
and dependencies are available:

```bash
python3.12 -m venv .venv-apero-08
source .venv-apero-08/bin/activate
python -m pip install --upgrade pip
```

On Windows, activate with `.venv-apero-08\\Scripts\\activate`. Conda is
usually more convenient for astronomy/scientific dependencies and shared
cluster environments.

## Profile setup

Create a local profile using the setup tool:

```bash
apero_setup.py --name=MY_PROFILE
```

Set `DRS_UCONFIG` to the profile's configuration directory using the generated
profile activation script. Do not commit site credentials or personal
configuration files.

## Common checks

```bash
python -c "import apero, aperocore; print(apero.__file__); print(aperocore.__file__)"
apero_setup.py --help
apero_validate.py
```

When switching branches or major releases, review dependencies and profile
compatibility before running recipes. APERO profiles are reset/rebuilt between
versions; do not rely on reading products made by an older code layout.
