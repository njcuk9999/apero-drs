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