# The APERO reduction interface module


## Installation

Normally just install this after apero-drs 
with:
```bash
pip install -U -e ./apero-ri
```

However for developers you can install this separately

```bash
conda create --name apero-ri python=3.12
conda activate apero-ri

git clone git@github.com:njcuk9999/apero-drs.git
git clone git@github.com:njcuk9999/lbl.git

pip install -U -e ./apero-drs/apero-core -e ./lbl -e ./apero-drs/apero-drs[dev]
pip install -U -e ./apero-ri[dev]
```

## How to run

First time you must run `apero_ri_setup`  to setup the page

After that you just run `apero_ri_run --port=1234`

Then you just need to forward the port you select, and it should work.

The web-server will only work while `apero_ri_run` is running.


## Python use

### Use:

```python
import apero_ri
```


### import rules

can import any thing from:

aperocore
apero

