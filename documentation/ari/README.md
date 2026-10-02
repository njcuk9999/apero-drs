# Maintaining APERO documentation

This directory is the source tree for documentation served by apero-ri. The
same versioned Markdown content is intended to be reusable by a future
Read-the-Docs build. Do not edit compiled pages or the legacy Sphinx output.

## Where to edit

| Content | Edit here | Generated or served result |
| --- | --- | --- |
| Hand-written recipe and tool descriptions | `documentation/descriptions/<instrument>/<kind>/<entry-point>.md` | Included in generated APERO recipe/tool pages. |
| Hand-written sequence descriptions | `documentation/descriptions/<instrument>/sequences/<sequence>.md` | Included in generated sequence pages. |
| Hand-written file-definition explanation | `documentation/descriptions/<instrument>/files/index.md` | Included above the consolidated instrument file-definition table. |
| Developer guides and reference material | `documentation/ari/<version>/home/docs/developer/` and `reference/` | Served as authored pages; not regenerated from recipe definitions. |
| Scientific algorithm explanations | `documentation/ari/<version>/home/docs/algorithms/` | Served as authored pages; recipes can link to them. |
| Version-independent pages | `documentation/ari/all/home/docs/` | Shared across versions unless overridden by a version-specific page. |
| Version list and labels | `documentation/ari/versions.yaml` | Controls the versions available in ARI; first version is the default. |
| Images used in ARI docs | `documentation/ari/static/images/` | Referenced by Markdown pages. |

The `<instrument>` folder is `default`, `spirou`, `nirps_ha`, or `nirps_he`.
Descriptions use these kinds:

- `recipes`: instrument recipe definitions.
- `user_tools`: general or instrument-specific user tools.
- `dev_tools`: developer/admin tools.
- `sequences`: instrument recipe sequences.
- `files`: the consolidated file catalogue for an instrument. Optional
  explanatory prose belongs in `files/index.md`; the generated table includes
  every non-empty category and labels rows by processing `Stage`.

For a recipe or tool, name the Markdown file after its Python entry point,
without `.py`, for example:

```text
documentation/descriptions/spirou/recipes/apero_loc_spirou.md
documentation/descriptions/nirps_ha/recipes/apero_loc_nirps_ha.md
documentation/descriptions/default/user_tools/apero_astrometrics.md
```

A description fragment can begin with YAML frontmatter for algorithm links
and citations:

```yaml
---
algorithms:
  - order_localisation
references:
  - '[Cook et al. (2022)](https://arxiv.org/abs/2211.01358)'
---
```

Write the science-facing explanation and a hand-authored Mermaid flow diagram
in the fragment. Keep startup, logging, parser setup, and other wrapper details
out of the flow. The generator uses the current Python definitions for the
command, arguments, outputs, plots, sequence contents, and file tables.

If a fragment exists under the instrument folder, it is used for that
instrument. Otherwise, the generator checks the matching `default` fragment.
A missing fragment is created as an `Undocumented` stub with a placeholder
flow diagram. Replace the stub with real content. Existing non-stub prose is
not overwritten by generation.

## Refresh generated APERO pages

Activate an environment matching the checked-out APERO version and set
`DRS_UCONFIG` to a usable profile. Generate all instrument reference pages
with:

```bash
apero_documentation.py --ari --instruments=ALL
```

To be explicit about the output folder:

```bash
apero_documentation.py --ari --instruments=ALL --docversion=0.8.XXX
```

The version must have the same major/minor release as the running APERO
checkout. For a v0.7 checkout, use `--docversion=0.7.XXX`; the generator will
not label v0.8 definitions as v0.7 docs or vice versa.

APERO installs recipe scripts as copied command files in the environment's
`bin/` directory. If a command is still running old source after a code
update, refresh the editable install from the repository root:

```bash
python -m pip install --no-deps --force-reinstall --editable ./apero-drs
```

`--ari` rebuilds only
`documentation/ari/<version>/home/docs/apero/`. It removes that generated
subtree first, so stale pages for removed recipes do not linger. Hand-written
description fragments and authored pages under `developer/`, `reference/`,
and `algorithms/` are outside that subtree and are preserved.

When updating just one instrument, use its name explicitly, for example
`--instruments=NIRPS_HA`. Note that generated reference pages and description
stubs are only created for instruments selected by this argument.

## Migrate legacy RST once

The optional migration converts the old
`documentation/working/resources/<instrument>/descriptions/*.rst` files into
Markdown fragments. It is a one-time aid; inspect and clean the result because
RST constructs beyond the converter's supported subset may remain unchanged.

```bash
apero_documentation.py --migrate_desc --instruments=ALL
```

Migration only finds files inside a `descriptions/` directory. In this
checkout, legacy recipe/tool/sequence description prose exists for `default`
and SPIROU; NIRPS has raw-file explanatory RST files at the resource root,
not under `descriptions/`. Therefore migration alone does not create NIRPS
recipe or sequence fragments. Run `--ari --instruments=ALL` to generate the
NIRPS reference pages and editable description stubs from their live
`recipe_definitions.py` and `file_definitions.py`.

Do not remove `documentation/working/`, `documentation/unused/`, or
`documentation/output/` as part of routine documentation updates. They are
legacy content and are intended to be removed only after any required material
has been migrated and checked.

## Version-specific edits

`documentation/ari/0.7.XXX/` and `documentation/ari/0.8.XXX/` describe their
respective major/minor release families. Put a change that applies to every
version under `all/`; put a behavior or workflow that differs by release in
the matching version tree. Keep differences between patch releases explicit
in the corresponding major/minor page, or add a more specific version entry
when a separate published snapshot is needed.
