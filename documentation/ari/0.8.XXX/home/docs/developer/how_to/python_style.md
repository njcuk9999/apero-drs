---
card_label: Python style and architecture
card_icon: fa-solid fa-code
---

# Python style and architecture

These rules keep the DRS usable across instruments and keep `apero-core`
independent from the APERO profile and pipeline.

## Package boundaries

- `apero-core/aperocore` must not import APERO recipes, profiles, or
  `apero-drs` objects.
- In `apero-drs`, keep imports flowing from lower-level modules to higher-level
  modules. `apero.base` has no APERO imports; `apero.lang` depends only on
  base; core modules depend only on lower layers.
- Put ARI-only behavior in `apero-ri/apero_ri`.

## Function design

- Type parameters and return values; document each parameter and return value.
- Keep pure algorithms in `_core.py` modules and pass plain data, not
  framework objects or fixed-key parameter bags.
- Prefer explicit named parameters over positional conventions or opaque
  dictionaries. Natural open-ended mappings remain appropriate.
- Avoid trailing backslash line continuations. For long delegated calls, use
  contextual `*_args` and `*_kwargs` temporaries.
- Keep Python lines within 80 characters.

## Recipes

Recipe `__main__` functions should be short, top-level orchestration. Use
`# ----` section headings, make each phase obvious, and call science functions
rather than embedding reusable algorithms in the recipe. Matching workflows
for multiple instruments should keep matching recipe structure.

## NumPy and APERO math

Prefer `np.array(x)` over `np.asarray(x)` unless a view has been explicitly
profiled and is safe. Import `aperocore.math` as `mp` and use its nan-aware
wrappers when available; retain raw NumPy calls for tuple axes and inside
`aperocore.math` itself.

## Comments

Write a comment when it captures a non-obvious assumption, data-flow role, or
reason a branch exists. Do not narrate what the next line already says.
