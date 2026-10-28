# Markdown Description Sources

Hand-written prose and Mermaid diagrams for ARI reference pages live at:

```text
documentation/descriptions/<instrument>/<kind>/<source_name>.md
```

Instrument directories are lowercase: `default`, `spirou`, `nirps_ha`, and
`nirps_he`. For recipes and tools, `source_name` is the Python script filename
without `.py`, not its short command name. For example, `apero_extract_spirou.py`
uses `spirou/recipes/apero_extract_spirou.md`; the generated page uses the lowercase
recipe short name. No `description_file` metadata is required.

Categories map as follows:

| Kind | Definition |
| --- | --- |
| `recipes` | `recipe_type == 'recipe'` |
| `user_tools` | Type `tool` or `nolog-tool`, kind `user` or `processing` |
| `dev_tools` | Type `tool` or `nolog-tool`, kind `admin` |
| `sequences` | Sequence name, such as `full_seq.md` |
| `files` | File catalogue description, `index.md` |

The description reader prefers the instrument-specific Markdown file, then
falls back to `default/<kind>/<source_name>.md`. Missing files return empty
metadata and prose. Recipe and sequence page generation creates missing
instrument-specific stubs before reading; an existing stub therefore takes
precedence over the default. Existing authored fragments are never overwritten.

Optional YAML front matter supplies algorithm links and literature references:

```yaml
---
algorithms:
  - extraction
references:
  - "Author et al. (2026), journal reference"
---
```

Algorithm values are page references under `algorithms/`; references become
the page's literature list. The Markdown body, including Mermaid fences, is
included verbatim. Usage, arguments, outputs, plots, and recipe identity come
from the recipe summary metadata, not from these fragments. Edit these source
fragments rather than generated pages under `documentation/ari/`.

Legacy RST description sources and their migration converter are retired.
Write and maintain descriptions directly in Markdown; there is no RST lookup
or `--migrate_desc` conversion workflow.