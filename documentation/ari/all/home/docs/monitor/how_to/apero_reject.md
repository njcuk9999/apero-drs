---
card_label: APERO Reject
card_icon: fa-solid fa-circle-question
---

# How to run APERO reject

Reject by object:

```bash
apero_reject.py --objname={objname}
```

Reject by file identifiers:

```bash
apero_reject.py --identifier=file1,file2,file3
```

Reject by night:

```bash
apero_reject.py --obsdir=NIGHT1
```

Autofill prompts when needed:

```bash
--autofill="1,1,1,my comment"
```

Use descriptive comments. Reject only non-astrophysical objects or clearly
invalid data.
