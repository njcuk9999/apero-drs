---
card_label: Data Portal
card_icon: fa-solid fa-table-columns
---

# Data Portal

The Data Portal is the user-facing view of APERO profiles and products.

## Intended workflows

- select an accessible instrument/profile;
- browse objects and observations;
- inspect headers and reduced products;
- open plots and quality-control results;
- download permitted products.

## Data source

The Data Portal reads data paths from the linked APERO profile. Those paths
must exist as seen by the ARI server. If the reduction is on another host,
configure SSHFS first and point the profile at the mounted local path.

More detail about product tables, file presets, filtering, and downloads will
be added here.
