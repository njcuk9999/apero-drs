# APERO - A PipelinE to Reduce Observations

Last updated: 2023-07-12

Please see the documentation:
- [ONLINE] https://www.astro.umontreal.ca/~cook/apero-drs/index.html
- [LOCAL HTML] documentation/output/index.html
- [LOCAL PDF] documentation/output/apero-docs.pdf 


## Contents

1) [Latest version](#1-latest-version)
2) [Pre-Installation](#2-pre-installation)
3) [Installation](#3-installation)
4) [To Do and Known Issues](#4-todo-and-currently-known-issues)
5) [Using APERO](#5-using-apero)


## APERO module code diagram

Using the Github Action [Repo Visualizer](https://github.com/githubocto/repo-visualizer)

![Visualization of the codebase](./documentation/working/_static/diagram.svg)

##  1 Latest version
[Back to top](#apero---a-pipeline-to-reduce-observations)

- main (long term stable) V0.7.288 (2024-01-30)
    ```
    This is the version currently recommended for all general use. It may not
    contain the most up-to-date features until long term support and stability can
    be verified.
    ```
- developer (tested) V0.7.288 (2024-01-30)
    ```
    Note the developer version should have been tested and semi-stable but not
    ready for full sets of processing and defintely not for release for
    non-developers or for data put on archives. Some changes may not be
    in this version that are in the working version.
    ```
- stable-test (tested) V0.7.288 (2024-01-30)
    ```
    Notrmally up-to-date with the live version has been or is currently
    being tested for stability
    ```
- live (untested) V0.8.001 (2024-02-12) V0.7.289 (2024-01-30)
    ```
    Note the live version will be the most up-to-date version but has not been
    tested for stability - use at own risk.
    ```

---

## 2 Pre-Installation
[Back to top](#apero---a-pipeline-to-reduce-observations)

Please see the documentation:
- [ONLINE] https://www.astro.umontreal.ca/~cook/apero-drs/main/general/installation.html#download-from-github
- [LOCAL HTML] documentation/output/main/general/installation.html
- [LOCAL PDF] documentation/output/apero-docs.pdf 

---

## 3 Installation
[Back to top](#apero---a-pipeline-to-reduce-observations)

New instructions:

#### Step 1: Download the GitHub repository

```bash
git clone git@github.com:njcuk9999/apero-drs.git
```

or if this doesn't work try:

```bash
git clone https://github.com/njcuk9999/apero-drs.git
```

#### Step 2: Make a new environment (recommended)

Using conda, create a new environment and activate it.

Note one can also use venv (instead of conda) or use a current environment but
we recommend a new clean environment to avoid module conflicts.


```bash
conda create --name apero-env python=3.10
```

```bash
conda activate apero-env
```

Note you need to activate `apero-env` each time before running any SOSSISSE command.

#### Step 3: Install apero with pip 

##### Full mode

Make sure you are in `apero-env` conda environment (or equivalent) and then run:

```
cd {APERO_ROOT}

pip install -U -e ./apero-drs[full]
```

Note `{APERO_ROOT}` is the path to the cloned GitHub repository (i.e. `/path/to/apero`)
if you are in the directory where you did your `git clone` then you need to 
change directory into the `apero` directory (You are in the right place if there 
are directories: apero-core, apero-data, apero-drs, apero-test)


##### Dev mode

If you are developing apero-core you will want to do the following to have
both apero-drs and apero-core in editable mode:

```bash

pip install -U -e ./apero-core
pip install -U -e ./apero-drs[dev]
``` 

#### Step 4: Run apero_setup

```bash

apero_setup.py --name {apero profile name}
```


Please see the documentation:
- [ONLINE] https://www.astro.umontreal.ca/~cook/apero-drs/main/general/installation.html#setup
- [LOCAL HTML] documentation/output/main/general/installation.html
- [LOCAL PDF] documentation/output/apero-docs.pdf 


---


## 4 TODO and Currently known issues
[Back to top](#apero---a-pipeline-to-reduce-observations)

Please see the documentation:
- [ONLINE] https://www.astro.umontreal.ca/~cook/apero-drs/main/general/todo.html
- [LOCAL HTML] documentation/output/main/general/todo.html
- [LOCAL PDF] documentation/output/apero-docs.pdf 


---

## 5 Using APERO
[Back to top](#apero---a-pipeline-to-reduce-observations)


You must always activate two things before starting:

1. The conda environment you installed apero into (e.g. `apero-env`)
2. The apero profile you want to use (e.g. `SPIROU`)

---

In Linux/Mac this is done as follows:

```bash
source apero_profile.sh {apero profile name}
```


Where `{apero profile name}` is the name of the profile you want to
use (e.g. `spirou_offline`, `spirou_xxs`, `nirps_he_online`)

---

In Windows this is done as follows:

```
apero_profile.bat {apero profile name}
```

Where `{apero profile name}` is the name of the profile you want to
use (e.g. `spirou_offline`, `spirou_xxs`, `nirps_he_online`)


---

Please see the documentation:
- [ONLINE] https://www.astro.umontreal.ca/~cook/apero-drs/main/default/using_apero.html
- [LOCAL HTML] documentation/output/auto/tool_definitions/default/tools.html
- [LOCAL PDF] documentation/output/apero-docs.pdf 
- [APERO requirements (dev)] https://www.overleaf.com/project/681502d99cb7fde13a598227

## 6 Dev mode
[Back to top](#apero---a-pipeline-to-reduce-observations)

For dev mode (editable install of both apero-core and sossisse please run the following:

```bash

git clone git@github.com:njcuk9999/apero-drs.git -b v0.8.003
git clone git@github.com:njcuk9999/lbl.git

pip install -U -e ./apero-drs/apero-core -e ./lbl -e ./apero-drs/apero-drs[dev]

```