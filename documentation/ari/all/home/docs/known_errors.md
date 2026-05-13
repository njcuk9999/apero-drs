---
card_label: Known errors
card_icon: fa-solid fa-bug
---

# Known APERO Errors

The known-errors table is maintained in the monitor portal.

- Open the live table: [/monitor_portal/known_errors](/monitor_portal/known_errors)

## What This Table Is

The table tracks recurring APERO failures and expected warnings, with
recommended actions for operators.

Each row generally includes:

- Date reported
- Instrument / mode
- Recipe
- Action (Ignore, Check, Report)
- Type (Expected, Unexpected, Fixed)
- Error code / GitHub issue
- Generic error text
- Comments and full example error text

## Permissions

- Anyone with page access can view the table.
- Editing rows (create, update, delete) is restricted to monitor-level
  users and higher.

## Data Source

Known-error rows are stored as YAML files in:

- `apero-ri/apero_ri/resources/monitor/known_errors/`
