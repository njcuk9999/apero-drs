# APERO documentation

## Current source of truth

The current user and developer documentation lives in `documentation/ari/`.
ARI serves these Markdown pages directly. Documentation versions are selected
in `documentation/ari/versions.yaml`; the major-version trees are
`0.7.XXX/` and `0.8.XXX/`, while shared pages can live under `all/`.

Generated APERO reference pages live at:

```text
documentation/ari/<version>/home/docs/apero/
```

Hand-written descriptions for generated tools, recipes, sequences, and file
definitions live at:

```text
documentation/descriptions/<instrument>/<kind>/<name>.md
```

Edit description fragments and authored guides, not generated pages under
`home/docs/apero/`. The generator preserves existing description files and
only refreshes the derived reference pages.

## Generate the reference pages

Use a profile and environment that match the APERO checkout and instruments
being documented. For example:

```bash
apero_documentation.py --ari --instruments=SPIROU
```

The output version defaults to the running APERO major version. Use
`--docversion=0.8.XXX` when an explicit matching version is useful. The
generator rejects a version from a different APERO major release; it does not
translate one release's definitions into another release's documentation.

Use `--migrate_desc` only for the one-time conversion of legacy RST prose from
`documentation/working/resources/` into `documentation/descriptions/`. Review
the converted Markdown before relying on it; the converter handles common
RST headings, links, admonitions, code blocks, and math, but complex RST may
need manual cleanup.

## Legacy directories

`documentation/working/`, `documentation/unused/`, and
`documentation/output/` belong to the previous Sphinx workflow. Do not add
new documentation there. They remain temporarily for the one-time description
migration and historical reference; the intended end state is to remove them
after any required content has been migrated and checked.

## Longer-term publishing

The Markdown tree is organized so ARI can serve it now and a Read the Docs
build can consume the same versioned content later. Generated scientific
figures and mini-dataset runs are not part of the current generator yet; they
need instrument-specific, reproducible test data and configuration before
they can be added safely.