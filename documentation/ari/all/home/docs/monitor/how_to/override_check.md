---
card_label: Override Check
card_icon: fa-solid fa-circle-question
---

# How to override a check

Use overrides only when a FALSE is expected and explicitly approved.

```bash
python apero_check_override.py {yaml_name} --test={TEST_NAME} --obsdir=XXXX
```

Notes:

- Provide your full name.
- Add a clear reason (not just `no data`).
- Re-run checks afterward if status does not update.
