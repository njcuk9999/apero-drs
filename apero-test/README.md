# APERO Test: Example module using APERO-core
---

## Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Setup](#setup)
- [Usage](#usage)
- [Dev mode](#dev-mode)

[Back to top](#contents)

---

## Introduction

Insert text here

## Installation

#### Step 1: Clone the repository

```bash
git clone git@github.com:njcuk9999/{module}.git
```

#### Step 2: Install python 3.10 

Create a conda or python environment

e.g.

```bash 
conda create --name {module}-env python=3.10
conda activate {module}-env
```

#### Step 3: Install {module}

```bash
cd {{module}_ROOT}
pip install -U -e .
```

Note on can also use venv (instead of conda)

Note `{{module}_ROOT}` is the path to the cloned github repository (i.e. /path/to/{module})

[Back to top](#contents)

---

## Setup

First [install module](#installation).
Once you've done this activate the environment you installed {module} in.
(e.g. `conda activate {module}-env`)

To setup {module}, you need to run the following command:

```bash
test_setup {yaml_file}
```

where `yaml_file` is the yaml file you wish to create (if left blank you 
will be asked for one).


[Back to top](#contents)

---

## Usage


### Command line

To run {module}, you need activate the environemnt you installed {module} in.
(e.g. `conda activate {module}-env`)

Then you need to run the following command:

```bash
test_run {yaml_file}
```

[Back to top](#contents)

---

## Dev mode
[Back to top](#contents)

For dev mode (editable install of both apero-core and apero-test please run the following:

```bash

git clone git@github.com:njcuk9999/apero-drs.git

pip install -U -e ./apero-drs/apero-core
pip install -U -e ./apero-drs/apero-test[dev]
```