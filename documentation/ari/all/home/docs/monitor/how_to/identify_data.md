---
card_label: Identify Data
card_icon: fa-solid fa-circle-question
---

# How to identify data types

Use FITS headers to classify data quickly:

```bash
dfits {pattern} | fitsort OBJECT dpr.type obs.targ.name
```

Useful keys:

- `OBJECT`
- `obs.targ.name`
- `dpr.type` (ESO)
- `DPRTYPE` (APERO)
- `dpr.catg`

Typical categories:

- Calibrations: DARK, LED, LAMP, FP, UN1, UN2 patterns
- Science: `OBJECT,SKY` or `OBJECT,FP`
- Telluric: `TELLURIC,SKY`
