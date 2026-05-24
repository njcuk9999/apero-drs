---
card_label: Find Logs
card_icon: fa-solid fa-circle-question
---

# How to find and read log files

Main APERO logs:

- NIRPS-HE: `/cosmos99/nirps/apero-data/nirps_he_online/msg`
- NIRPS-HA: `/cosmos99/nirps/apero-data/nirps_ha_online/msg`

APERO checks log:

```bash
tail -n 200 HOMEDIR/apero_check.log
```

Manual trigger logs:

- Directory: `HOMEDIR/.apero/manual_trigger/`
- One log per yaml file
- CSV format: `timestamp, profile, step, obsdir, comment`
