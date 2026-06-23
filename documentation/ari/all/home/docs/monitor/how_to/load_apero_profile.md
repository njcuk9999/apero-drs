---
card_label: APERO Profile
card_icon: fa-solid fa-circle-question
---

# How to load an apero profile

1. Log in.
2. Activate conda environment.
3. Load profile:

```bash
nirps_he_online
# or
nirps_ha_online
```

Expected splash:

![APERO splash](/doc-images/apero_splash.png)

Check profile:

```bash
echo $DRS_UCONFIG
```

Prompt should include profile prefix (for example `nirps_he_online`).
