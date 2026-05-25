---
card_label: APERO Remove
card_icon: fa-solid fa-circle-question
---

# How to run APERO remove

`apero_remove.py` deletes processed data and database entries so data can be
reduced again cleanly.

```bash
apero_remove.py {args}
```

Always test first:

```bash
apero_remove.py {args} --test=True
```

Common arguments:

- `--obsdir`
- `--blocks=tmp,red,out,calib,tellu`
- `--file_prefix`
- `--file_suffix`
- `--objnames`
- `--rawdb`

Raw source files are not removed.
