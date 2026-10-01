---
card_label: Install APERO v0.7
card_icon: fa-solid fa-download
---

# Installation: APERO v0.7

APERO v0.7 has different runtime requirements across its patch releases. Pick
the instructions matching the release you are installing; do not use this
page as an installation recipe for v0.8.

## v0.7.297 and later

```bash
git clone git@github.com:njcuk9999/apero-drs.git
conda create --name apero-env-07 python=3.12
conda activate apero-env-07
cd apero-drs
pip install -r requirements_current.txt
python setup/install.py --name=MY_PROFILE
```

For development, clone LBL and install the developer requirements in the
matching checkout:

```bash
git clone git@github.com:njcuk9999/apero-drs.git -b developer
git clone git@github.com:njcuk9999/lbl.git -b developer
conda create --name apero-env-07 python=3.12
conda activate apero-env-07
pip install -r apero-drs/requirements_developer.txt
pip install --editable ./lbl
python apero-drs/setup/install.py --name=MY_PROFILE
```

## v0.7.296 and earlier

These releases used Python 3.9 in the documented install path. Use a checkout
and dependency set from the exact release you need:

```bash
git clone git@github.com:njcuk9999/apero-drs.git
conda create --name apero-env-07-old python=3.9
conda activate apero-env-07-old
cd apero-drs
pip install -r requirements_current.txt
python setup/install.py --name=MY_PROFILE
```

## Profile and environment

`MY_PROFILE` is the profile name for the reduction. Use the profile activation
script produced by installation so `DRS_UCONFIG` points to that profile.
Keep each APERO major release in a separate environment and profile. Do not
reuse a v0.7 profile as a v0.8 profile.

For current v0.8 instructions, see [Installation v0.8](/docs/install?v=0.8.XXX).
