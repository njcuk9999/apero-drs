---
card_label: Install
card_icon: fa-solid fa-download
---

# Installation 0.8.XXX

## General use

```bash
conda create --name apero-env-08 python=3.12
conda activate apero-env-08

git clone git@github.com:njcuk9999/apero-drs.git -b v0.8.running
git clone git@github.com:njcuk9999/lbl.git

pip install -U -e ./apero-drs/apero-core -e ./lbl -e ./apero-drs/apero-drs[dev]

apero_setup.py --name={PROFILE}
```

Where `{PROFILE}` is a custom name for the reduction you are going to do.

### Re-running setup

Setup saves an executable `install_script.sh` inside the profile's config
directory (`DRS_UCONFIG`). It records the resolved setup choices, including
individual data paths, database settings, external raw links, and cleanup
options. Run it from any working directory:

```bash
"$DRS_UCONFIG/install_script.sh"
```

The script uses the Python interpreter and setup location that generated it.
Additional setup arguments can be appended to override recorded values.
Re-running setup retains the recorded cleanup behavior, including its
confirmation prompt. The file is owner-only because it can contain database
credentials.

To generate or replace only the script for the activated profile:

```bash
apero_setup.py --install_sh
```

Alternatively, select a profile explicitly:

```bash
apero_setup.py --install_sh --name={PROFILE} --config=/path/to/config
```

This mode reads the profile configuration without installing, cleaning,
downloading assets, or offering demo data. For profiles created before setup
started saving replay choices, settings not present in the profile (such as
cleanup preferences) use setup defaults.

## Developer

```bash
conda create --name apero-env-08 python=3.12
conda activate apero-env-08

git clone git@github.com:njcuk9999/apero-drs.git -b v0.8.121
git clone git@github.com:njcuk9999/lbl.git -b developer

pip install -U -e ./apero-drs/apero-core -e ./lbl -e ./apero-drs/apero-drs[dev]

apero_setup.py --name={PROFILE}
```

Where `{PROFILE}` is a custom name for the reduction you are going to do.