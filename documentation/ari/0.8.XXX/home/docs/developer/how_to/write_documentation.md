---
card_label: Write APERO documentation
card_icon: fa-solid fa-book-open
---

# How to write APERO documentation

The source of truth for user-facing APERO documentation is the versioned
Markdown tree in `documentation/ari/`. The ARI interface serves it directly;
Read the Docs can build from the same source tree in a future Sphinx wrapper.

## What is generated and what is authored

- Generated reference pages are under
  `documentation/ari/<major-version>/home/docs/apero/`.
- Hand-written descriptions live in
  `documentation/descriptions/<instrument>/<kind>/`.
- Developer guides, reference pages, and algorithm narratives are hand-written
  under `documentation/ari/<major-version>/home/docs/`.
- Version-independent pages can live under `documentation/ari/all/`; version
  pages override them. Do not copy shared pages into every version folder.

For now, `0.7.XXX` and `0.8.XXX` are major-version groups. Differences between
sub-versions are maintained as explicit versioned documentation changes.

## Describe a recipe or tool

Create a Markdown fragment named after the Python entry point, without
`.py`, in the appropriate descriptions directory:

```text
documentation/descriptions/spirou/recipes/apero_loc_spirou.md
documentation/descriptions/default/user_tools/apero_get.md
```

Use YAML frontmatter for algorithm slugs and references. Write prose for the
science user, then add a hand-authored Mermaid flow diagram of the meaningful
steps and data products. Keep startup, logging, parameter parsing, and other
wrapper details out of that diagram.

The generator fills in command syntax, arguments, outputs, plots, sequence
membership, and file-definition tables from the current Python definitions.
It creates a missing description stub but never overwrites an existing one.

## Generate pages

Set `DRS_UCONFIG` to a valid profile for the selected instrument and activate
the matching APERO environment, then run:

```bash
apero_documentation.py --ari --instruments=ALL
```

Run the generator from the checkout whose definitions match the docs you are
building. `--instruments=ALL` works only when the active configuration can
load every selected instrument; otherwise run once per instrument with its
matching profile. `--docversion` selects the output folder; it does not adapt
v0.8 definitions to describe v0.7:

```bash
apero_documentation.py --ari --instruments=ALL --docversion=0.8.XXX
```

Generation owns only the `home/docs/apero/` subtree for that version; authored
guides outside that subtree are left alone. Run a local ARI test or serve the
app to verify page cards, links, Mermaid diagrams, and KaTeX equations.

## Keep citations useful

Cite the original method or instrument paper where it supports a scientific
claim. Link to stable journal/DOI/arXiv sources. Use Wikipedia only for
background concepts where a primary source is not needed; it is not evidence
for APERO's implementation details.
