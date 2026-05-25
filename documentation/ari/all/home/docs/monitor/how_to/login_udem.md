---
card_label: UdeM Login
card_icon: fa-solid fa-circle-question
---

# How to log into a UdeM machine

1. SSH to `venus.astro.umontreal` with your user account.
2. SSH from there to `nirps-client@rali`.

```bash
ssh -XY -oport=5822 <user>@venus.astro.umontreal
ssh nirps-client@rali
```

Use these hosts only for babysitter activities while on shift.
