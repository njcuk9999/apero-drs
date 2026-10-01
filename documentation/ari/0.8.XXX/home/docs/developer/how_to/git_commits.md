---
card_label: Best practices for Git commits
card_icon: fa-solid fa-code-commit
---

# Best practices for APERO Git commits

APERO commit messages are tagged by package and project so history is searchable
and release work can be grouped reliably. Apply this convention to every
commit, whether it is made by a developer or an agent.

## Required subject format

```text
[PACKAGE.PROJECT] Imperative summary of the change
```

Examples:

```text
[APERO.EXTRACT] Vectorize background-map percentile filtering
[APEROCORE.CORE] Route nan-aware stats through math wrapper
[APERO.LOC+SHAPE] Move order-profile straightening into apero_shape
[APERO+APEROCORE.EXTRACT] Add flat-response calibDB round trip
[ARI.RI] Clarify API token renewal errors
```

synonyms or abbreviations for an existing project.
The subject starts with one bracketed tag, followed by a short imperative
summary. Use the exact project spelling from the list below; do not invent
near-synonyms or abbreviations for an existing project.

## Choose the package tag

| Code changed | Package tag |
| --- | --- |
| `apero-drs/` | `APERO` |
| `apero-core/` | `APEROCORE` |
| Both `apero-drs/` and `apero-core/` in one change | `APERO+APEROCORE` |
| `apero-ri/` | `ARI` |

## Choose the project tag

Use the most relevant project tag from this current, non-exhaustive list. The
names and meanings are the shared APERO project vocabulary:

| Tag | Scope |
| --- | --- |
| `CORE` | Shared/base functionality in `aperocore` not tied to one project. |
| `SETUP` | Installation, environment, packaging, `pip`, and `setup.py`. |
| `DEV` | `apero.dev`, developer-only tooling, and test scaffolding. |
| `PREPROCESS` | `apero_preprocess`. |
| `LOC` | Localisation (`apero_loc`). |
| `SHAPE` | Shape calibration (`apero_shape`). |
| `EXTRACT` | Extraction (`apero_extract`, `apero_flat`, `apero_thermal`). |
| `WAVE` | Wavelength solution (`apero_wave_ref`, `apero_wave_night`). |
| `TELLURIC` | Telluric correction (`apero_mk_tellu`, `apero_fit_tellu`). |
| `TEMPLATE` | Template creation (`apero_mk_template`). |
| `CCF` | Cross-correlation function (`apero_ccf`). |
| `LBL` | Line-by-line integration. |
| `POL` | Polarimetry. |
| `TOOLS` | `apero.tools` scripts and utilities. |
| `ASTROMETRICS` | Astrometric database and Gaia cross-match. |
| `RESET` | `apero_reset` and profile reset logic. |
| `DATABASE` | Calibration/telluric/index database code. |
| `PROCESSING` | `apero_processing` and recipe sequencing. |
| `STARTUP` | `drs_startup`, recipe/module initialization, and import speed. |
| `CHECKS` | `apero_checks` and data-quality checks. |
| `REJECT` | Manual/automatic rejection of files. |
| `QUEUE` | Job queue management. |
| `VISU` | Visualisation tools (`apero.tools.module.visulisation`). |
| `KEYWORDS` | FITS header keyword definitions. |
| `PSEUDO_CONST` | Instrument pseudo-constants. |
| `VERSION` | Version bumps and release metadata. |
| `ARI` | For `apero-ri/` changes, (i.e. apero reduction interface changes) |

When one change genuinely spans multiple projects, join the tags with `+`,
for example `[APERO.LOC+SHAPE]`. Do not list unrelated project tags merely
because a commit happens to touch several files. If a change does not fit any
existing project, add and document a new tag in this list and the repository
contributor guidance in the same change.

## Keep commits reviewable

- Make each commit one coherent, reviewable change. Separate unrelated fixes,
  formatting churn, generated files, and feature work.
- Include tests and required call-site updates with the code change they
  validate. When a public signature or return shape changes, search all
  packages and update every caller in the same change.
- Review `git diff --check` and `git diff --staged` before committing. Confirm
  generated files and local configuration are intentional; never commit
  credentials, profile secrets, or data products.
- Use an imperative subject (`Add`, `Fix`, `Route`, `Document`), keep it
  specific, and do not end it with a period.
- Add a body only when context, tradeoffs, compatibility notes, or validation
  commands are not clear from the diff. Put those details below the tagged
  subject, not in place of it.

## Before committing

```bash
git status --short
git diff --check
git diff --staged
```

Stage only the files for this change. Do not use destructive Git commands to
remove changes you did not make.
