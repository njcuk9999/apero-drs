---
card_label: Core algorithms
card_icon: fa-solid fa-square-root-variable
related:
  - apero/recipes/
  - developer/how_to/add_a_recipe
  - reference/
---

# APERO core algorithms

Scientific algorithm pages explain the inputs, assumptions, mathematical
operations, quality checks, and outputs of APERO's scientific code. They link
to the implementation and are versioned with the reduction release.

The APERO paper is a useful overview, but it describes an earlier pipeline
state. For v0.8 behavior, the current source code and tests are authoritative.

Each page explains a scientific method rather than recipe usage. It identifies
inputs and assumptions, follows the mathematics, and connects the method to
the current implementation and its quality checks.

| Algorithm | Scope |
| --- | --- |
| [Order localisation and profile fitting](order_localisation) | Detects illuminated order regions and fits smooth order-center and width models across the detector. |

As algorithms are added, distinguish implemented behavior from scientific
motivation, identify constants that affect the method, and cite primary
literature where it supports the explanation.
