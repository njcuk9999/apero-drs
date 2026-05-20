---
card_label: Install
card_icon: fa-solid fa-download
---

# Installation 0.7.296 and earlier 0.7.XXX


## General use

```bash
git clone git@github.com:njcuk9999/apero-drs.git
conda create --name apero-env-07 python=3.9
conda activate apero-env-07
cd apero-drs
pip install -r requirements_current.txt
python setup/install.py --name={PROFILE}
```

Where `{PROFILE}` is a custom name for the reduction you are going to do.

## Developer

```bash
git clone git@github.com:njcuk9999/apero-drs.git -b developer
git clone git@github.com:njcuk9999/lbl.git -b developer
conda create --name apero-env-07 python=3.9
conda activate apero-env-07
pip install -r apero-drs/requirements_developer.txt
pip install -U -e ./lbl
python apero-drs/setup/install.py --name={PROFILE}
```

Where `{PROFILE}` is a custom name for the reduction you are going to do.