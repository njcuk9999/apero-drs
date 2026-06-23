---
card_label: Custom Run File
card_icon: fa-solid fa-circle-question
---

# How to re-run APERO with a custom run file

Use this when you must reprocess selected objects or steps.

## Prepare run file

1. Duplicate a default run file (do not edit defaults directly).
2. Edit key parameters (`RUN_OBS_DIR`, `INCLUDE_OBS_DIRS`, `CORES`,
   `TEST_RUN`, `RUN_*`, `SKIP_*`, `SCIENCE_TARGETS`).

## Test and run

```bash
apero_processing.py {run_file} --test=True
apero_processing.py {run_file}
```

## Refresh links and ARI after processing

```bash
manual_trigger
python manual_trigger.py {yaml_file} --links=False \
    --apero_process=False --get=True --ari=True
```
