# APERO - A PipelinE to Reduce Observations

##  Latest version

- master (long term stable) V0.5.000
- developer (tested) V0.6.001
- working (untested) V0.6.001

---
---

## Pre-Installation

#### 1. clone this repository

```bash
git clone https://github.com/njcuk9999/apero
```

This may take some time (in future most of the data required will be a separate download),
and we still have many (now redundant) files from the spirou_py3 repository

Note if you have a git from the spirou_py3 you need to redirect it:
```bash
cd ./spirou_py3
git remote set-url origin https://github.com/njcuk9999/apero-drs
```

---

#### 2. change to the repository directory
```bash
cd ./apero-drs
```

---

#### 3. checkout the correct branch

- For Master version: 
```
git checkout master
```
- For Developer version:
```
git checkout developer
```
- For Working version:
```
git checkout working
```

---
---

## Installation (Currently only for `developer` and `working` versions)

Make sure pre-installation is done first!

---

#### 1. run the installation script
```bash
python setup/install.py
```

---

#### 2. Follow the step-by-step guide:

A. `User config path`: This is the path where your configuration will be saved.
If it doesn't exist you will be prompted to create it. 
(This will be referred to as `DRS_UCONFIG` from now on)

B. `Settings for {INSTRUMENT}`: Install {INSTRUMENT}. If yes it will install the 
instrument if not then it will not install the instrument. Currently only 
SPIRou is supported.

C. `Set up paths individually`. If [Y]es it will allow you to set each path separately
(i.e. for raw, tmp, reduced, calibDB etc). If no you will just set one path and
all folders (raw, tmp, reduced, calibDB etc)) will be created under this directory.

D. `Setting the directories` (either one directory or each of the sub-directories
required - i.e. raw, tmp, reduced, calibDB etc)

E. `Clean install?` __WARNING__: If you type [Y]es you will be prompted (later) to reset
the directories this means any previous data in these directories will be removed.
Note you can always say later to individual cases.


F. This process will then repeat for all instruments. __NOTE: Currently only SPIRou is supported__

G. In the `Copying files` step if you asked for a clean install if directories 
are not empty you will be prompted to reset them one-by-one 
(__NOTE: THIS WILL REMOVE ALL DATA FROM THIS SPECIFIC DIRECTORY)__

---

#### 3. Installation is then complete

---

#### 4. Running apero

To run apero you need to do __one__ of the following

__NOTE__: these three are equivalent only do __one__

##### i) source environmental variables directly

 `source {DRS_UCONFIG}/apero.{SYSTEM}.setup`

where: 
 - `{DRS_UCONFIG}` is the config path set up in step __A__
 - `{SYSTEM}` is either `bash` or `sh` depending on your shell

##### ii) alias to environmental variables

`alias apero "source {DRS_UCONFIG}/apero.{SYSTEM}.setup"`  (tcsh/csh)
`alias apero=""source {DRS_UCONFIG}/apero.{SYSTEM}.setup"`  (bash)

##### iii) add the contents of `{DRS_UCONFIG}/apero.{SYSTEM}.setup` to your startup script

i.e. one of the following `~/.bashrc`, `~/.bash_profile`, `~/.tcshrc`, `~/.profile`

For example adding to `~/.bashrc`:
```bash
# setup paths
export PATH="/scratch/apero_dev/apero/tools/bin":$PATH
export PATH="/scratch/apero_dev/bin":$PATH
export PATH="/scratch/apero_dev/":$PATH

# setup up python path
export PYTHONPATH="/scratch/apero_dev/apero/tools/bin":$PYTHONPATH
export PYTHONPATH="/scratch/apero_dev/bin":$PYTHONPATH
export PYTHONPATH="/scratch/apero_dev/":$PYTHONPATH

# setup drs config path
export DRS_UCONFIG="/home/user/apero/config/"

# force numpy  to only use 1 core max
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1

# run the validation script for SPIROU
python /scratch/apero_dev/apero/tools/bin/validate.py SPIROU
```


---


## TODO

- finish `obj_spec_spirou` and `obj_pol_spirou` [Do not use them now]
- output files like CFHT (e.fits, p.fits, v.fits etc)
- data separate download from DRS
- setup instrument
- move `object_query_list.fits` to `calibDB`
- write documentation and paper
- go through all summary plots and decide which plots, write figure captions,
improve plots, write quality control description, decide which header keys to print
- add `plot== 3` (all debug plots shown) and `plot==4` (all debug plots saved) modes
- display func for all functions
- add raw (via run) to file explorer
- Windows compatibility
- add doc strings to all functions, descriptions to all constants, review all 
constant min/max/dtypes
- add more debug printouts
- deal with all python warnings
- add EA mask generation from templates
- add EA template matching 


## Currently known issues

- wave solution sometimes using HC wave solution sometimes FP wave solution - WHY?
- telluric correction is slightly worse than before (due to wavelength solution?)
- CCF still showing problems with noise (maybe same problem as telluric correction?)
- BERV file gets locked (Ctrl+C to unlock) - WHY?
- index.fits not found - during parallel writes to index.fits - locking system is flawed - is this fixed?
- file explorer is broken (needs updating)
- 