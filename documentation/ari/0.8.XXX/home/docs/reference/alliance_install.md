---
card_label: Alliance installation
card_icon: fa-solid fa-server
---

# Installing APERO on Alliance clusters

Alliance systems are managed HPC environments. The exact login node, storage
paths, Slurm partition, modules, and account allocations vary by site and
change over time. Treat your institution's current Alliance documentation
and group instructions as authoritative; this page describes the APERO
workflow, not a universal set of cluster commands.

## Before installing

- Confirm your Alliance account and allocation can access the required
  project/scratch filesystem and compute resources.
- Read the current cluster rules for login-node work, interactive jobs,
  software modules, network access, and data retention.
- Ask the APERO site administrator for the supported Python/Conda stack,
  profile directory, database access, and branch/tag to use.
- Keep credentials and database passwords out of shell scripts committed to
  Git.

## Recommended workflow

1. Connect to the cluster using the institution's approved SSH method.
2. Load the supported environment module or activate the supported Conda
   distribution, following current Alliance instructions.
3. Create an isolated environment for the APERO major version.
4. Clone APERO and LBL into persistent project storage, not an ephemeral
   compute-node filesystem.
5. Install `apero-core`, `lbl`, and `apero-drs` in editable mode from the
   chosen checkout.
6. Create or configure a profile using the site's approved APERO settings.
7. Test imports and run `apero_validate.py` on a login or interactive node as
   permitted by local policy.
8. Submit data processing through the site's scheduler workflow; do not run
   long reductions on login nodes.

## Paths and data

Store source checkouts, configuration, raw data, and generated products in the
locations assigned by the site administrators. Confirm quotas and backup
policies before copying large datasets. Keep scratch cleanup and data-retention
rules in mind; a successful APERO run does not guarantee that scratch output
will persist indefinitely.

## Scheduler integration

APERO can be integrated with scheduler tools such as Slurm, but job templates
must match the site's current queue, memory, time, and core policies. Start
with an administrator-approved submission wrapper and a small test reduction.
Record the code version, profile, inputs, and scheduler job ID for each
production run.

## Troubleshooting checklist

- `DRS_UCONFIG` points to the intended profile and is readable on compute
  nodes.
- The selected Conda environment is activated by the job script, not only by
  the interactive shell.
- APERO and LBL imports resolve to the intended source checkouts.
- Profile, database, and data paths are mounted identically on compute nodes.
- Memory, wall time, and thread counts match the scheduler request.

For site-specific commands, consult your Alliance institution's current
support documentation and the local APERO administrator.
