---
card_label: APERO Astrometrics
card_icon: fa-solid fa-circle-question
---

# How to run APERO astrometrics

Add an object:

```bash
apero_astrometrics.py {objname}
```

Tips:

- include all common aliases
- check transformed APERO naming variants
- verify SIMBAD/catalog matches before saving

If name resolution fails, use file-assisted mode:

```bash
apero_astrometrics.py Unknown --fileoption={ABSOLUTE_PATH}
```

This uses RA/Dec from a file and proposes nearby candidates.
