# raw: Calibration OB Name Check

## Overview

This check verifies that required calibration OB names appear in the
configured MJD spans. It scans all raw-file headers, enables each rule
only inside its configured MJD range, and then checks that matching OB
names occur at least once while the rule is active.

## Requirements

- [BLANK](checks/blank.md)
- [HAS_OBSDIR](checks/has_obsdir.md)

## What to do

No instructions provided.

## Contact

No contacts.
