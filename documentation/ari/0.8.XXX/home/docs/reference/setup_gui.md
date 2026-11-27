---
card_label: APERO setup GUI
card_icon: fa-solid fa-sliders
related:
  - install
  - apero/user_tools/valid
  - reference/
---

# APERO setup GUI

`apero_setup.py --gui` opens a browser interface for setting up APERO and
checking a profile straight after setup. It runs the normal APERO scripts
(`apero_setup.py`, `apero_setup.py --update`, `apero_validate.py`) and shows
their output in a console on each page. Any question a script still asks
(for example the reset confirmation) is answered in that console. Every page
shows the **CLI equivalent** of what it runs, so you can repeat anything from
a terminal.

The GUI covers setup and the state of APERO after setup. It does not edit
database entries or run reductions (the only way it changes the databases
is a reset in the Data manager).

## Starting the GUI

```bash
apero_setup.py --gui
```

| Option | Use |
| --- | --- |
| `--gui` | Open the setup GUI instead of asking questions in the terminal. |
| `--gui_port=PORT` | First port to try (default 8099). The next free port is used if it is busy. |
| `--gui_host=HOST` | Address to listen on (default `127.0.0.1`, this machine only). |
| `--gui_headless` | Do not open a browser; only print the address. |

Other setup options given with `--gui` (for example `--name`, `--config` or
`--instrument`) pre-fill the Setup form.

On a remote machine, start the GUI with `--gui_headless` and open an ssh
tunnel from your computer, for example
`ssh -N -L 8099:localhost:8099 user@host`, then browse to
`http://localhost:8099/`. The exact command is printed at start up.

The GUI keeps its own files (process logs, backups of edited files and saved
reports) in `~/.apero/setup_gui/`.

## Tabs

- **Info**: this page.
- **Setup**: create a profile with `apero_setup.py`. The sections follow the
  terminal questions: profile name, config directory and language;
  instrument; data directories (one data directory, or each directory
  separately); an optional external raw directory (linked into the raw
  directory, never written to); database connection and table names; plot
  mode and clean start. **Start from an existing profile** fills the form
  from a profile in `~/.apero/profiles.ini`. **Validate and save** lists
  anything that is missing; otherwise it runs setup with every answer on the
  command line.
- **Edit**: open the files setup wrote to the profile's `DRS_UCONFIG`
  directory (`install.yaml`, `database.yaml`, `user_config.yaml`,
  `user_constants.yaml`, `user_keywords.yaml`; `setup.sh`, `setup.bat` and
  `install_script.sh` are read only). Edit them as a form, where each
  constant links to its Docs entry and shows the instrument default, or as
  raw text. **+ Add parameters** (in `user_config.yaml`,
  `user_constants.yaml` and `user_keywords.yaml`) lists every config
  value, constant or header keyword that is not yet in the file, with its
  default for the profile's instrument and its description. Filter the list
  and click **+** to add one: it is added to the file with its default
  value as an unsaved change (highlighted in the form), so you can change
  its value and then save. **Usual settings only** limits the list to
  the settings setup writes by default. The **✕** next to a parameter
  removes it from the file (with its comment) after a confirmation that
  shows the default it falls back to; this is also an unsaved change. **Review changes** before saving; a
  backup is kept every time you save. **Re-run setup** runs `apero_setup.py --update` with the values
  in the files. **Only regenerate install_script.sh** runs
  `apero_setup.py --install_sh`.
- **Validate**: **Check profile** shows the state of a profile: config
  files, data directories and disk space, databases (tables, number of
  rows, a breakdown by key), python modules (installed against required
  versions, git state of APERO) and the machine (cpus, memory, load).
  **Download report** saves the same information as one text file.
  **Run apero_validate.py** runs the validation recipe in the console.
- **Processes**: every process started from the GUI, with its log.
- **Data manager**: browse the data directories of a profile once
  `apero_setup.py` has been run for it. Choose the profile (its
  `DRS_UCONFIG` directory), then a directory: raw, tmp, red, calib,
  tellu, out, lbl, assets, log, plot, run, other, the external raw
  directory (if set) or the profile directory itself. Each shows its number
  of files and size. View files, FITS headers and images, download, compare
  two files or delete files. The raw and external raw directories are read
  only: raw data is never deleted from the GUI. Deleting files does not
  update the APERO databases, so use **Reset** to clean a whole part
  consistently. **Reset** runs `apero_reset.py` for everything or for one
  part (`--only_red`, `--only_calib`, ...). By default it asks you to
  confirm each part in the console; untick **Ask before each part** to add
  `--nowarn` (you then type the profile name to confirm).
- **Docs**: **Constants** lists every APERO constant, config value and header
  keyword. Each entry shows its description, its value for each instrument
  and the user file it can be set in, filtered by kind and instrument.
  **Guides** shows APERO documentation pages, the same pages apero-ri
  serves.

Hover over a setup field or a parameter to see its description. Click a
parameter name to open its full description.

## Re-running setup after editing

`apero_setup.py --update` reads these values from the profile:

- the name, instrument and language from `install.yaml`;
- the data paths and plot mode from `user_config.yaml`;
- the database settings from `database.yaml`;
- the clean start choices from `SETUP_ARGUMENTS` in `install.yaml`.

It then writes every file again, creates any missing directories and, if
`CLEAN_START` is true, cleans the profile with `apero_reset`.

The user yamls are rebuilt from the APERO defaults plus these setup values.
Any other values you changed in `user_config.yaml`, `user_constants.yaml` or
`user_keywords.yaml` go back to their defaults. The GUI keeps a copy of the
files before the re-run; **Show what changed** compares each changed file
before and after, and the backups from earlier saves are under **Compare
with backup**.

## The database password

The GUI never puts the database password on a command line or in a log. It
passes the password to `apero_setup.py` in the `APERO_SETUP_DATABASE_PASS`
environment variable, which setup reads when `--database-pass` is not
given. You can use the same variable in scripts:

```bash
APERO_SETUP_DATABASE_PASS='...' apero_setup.py --name=... --config=...
```

When the form was filled from an existing profile, a blank password keeps
that profile's password.

## State reports

The Validate tab and `apero_validate.py --report` write the same report:
one plain text file with numbered sections and one `key: value` per line.
It is meant to be easy to read and to give to an AI assistant when asking
for help:

- `0. SUMMARY`: the overall status (`ok`, `warn` or `bad`) and every
  problem found, worst first;
- `1. PROFILE`: name, `DRS_UCONFIG`, instrument, language, setup choices;
- `2. CONFIG FILES`: each file, whether it parses, and which APERO version
  wrote it;
- `3. DATA PATHS`: each directory (exists, writable, number of entries)
  and free disk space;
- `4. DATABASE`: connection settings (the password is never written) and
  each table or store with its number of rows;
- `5. PYTHON MODULES`: python, APERO and apero-core versions and git
  state, and each requirement as installed against required;
- `6. MACHINE`: host, operating system, cpus, memory and load.

```bash
apero_validate.py --report
apero_validate.py --reportfile=/path/to/report.txt
```

Without `--reportfile` the report is written to
`apero_report_{profile}_{time}.txt` in the current directory. Check a
report before sharing it: it contains host names, user names and paths.
