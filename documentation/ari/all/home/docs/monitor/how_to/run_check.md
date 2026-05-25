---
card_label: APERO Check
card_icon: fa-solid fa-circle-question
---

# How to re-run an apero check

## Step 1

Log into the UdeM machine and load the right profile context.

## Step 2

Activate the APERO conda environment.

## Step 3

Go to the check directory:

```bash
apero_checks
```

## Step 4

Choose:

- raw or reduced checks
- yaml profile
- observation date(s)
- full run, filtered run, or single test mode

## Commands

Raw checks:

```bash
apero_raw_check.py {yaml_name} --obsdir={obsdir}
apero_raw_check.py {yaml_name} --obsdir={obsdir} \
	--testfilter={TEST1},{TEST2}
apero_raw_check.py {yaml_name} --obsdir={obsdir} --test={TEST1}
```

Reduced checks:

```bash
apero_red_check.py {yaml_name} --obsdir={obsdir}
apero_red_check.py {yaml_name} --obsdir={obsdir} \
	--testfilter={TEST1},{TEST2}
apero_red_check.py {yaml_name} --obsdir={obsdir} --test={TEST1}
```

## YAML names

- `nirps_he_online_udem`
- `nirps_he_offline_udem`
- `nirps_ha_online_udem`
- `nirps_ha_offline_udem`

## Observation date options

```bash
--obsdir=YYYY-MM-DD
--obsdir=YYYY-MM-DD,YYYY-MM-DD
--today
--yesterday
```