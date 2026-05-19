#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Raw APERO check for obsdir existence."""

from typing import Tuple

import apero_ri.apero_monitoring.core.raw_common as raw_common
from apero_ri.apero_monitoring.core.core import AperoCheck

from apero_ri.apero_monitoring.core import contacts
from apero_ri.apero_monitoring.core import links

# =============================================================================
# Define variables
# =============================================================================
CHECK_NAME = 'HAS_OBSDIR'
CHECK_HUMAN_NAME = 'Observation Directory Check'
CHECK_TYPE = 'raw'
INSTRUMENTS = ['SPIROU', 'NIRPS_HE', 'NIRPS_HA']

CHECK = AperoCheck(CHECK_NAME, CHECK_HUMAN_NAME, CHECK_TYPE, INSTRUMENTS)
CHECK.dependencies = ['BLANK']

# Define the description of this check (for displaying in documentation)
CHECK.description = """
This test checks whether an observation night directory exists in the 
raw directory.
"""

# Define the what to do text for this check (for displaying in documentation)
CHECK.what_to_do = f"""
If FALSE please [re-run the check]({links.RUN_CHECK}) with --test=HAS_OBSDIR.

If still FALSE then the directory for that day/night has not been 
created on our machine.

Please check [here for when you should expect files on 
our machines])[{links.OBS_TIMELINE}].

Then you need to [check the ESO archives for data]({links.ESO_ARCHIVES}).

### If there is no data on the ESO archive for that night

This means that either:
- No data was taken
- No data was transferred from La Silla to the ESO Archive

If there is no data on the ESO archive either no data was taken or no data was 
transferred from La Silla to the ESO archive.

Check the observation log if there is a good reason for no data you can report 
this FALSE and ignore it - you can always email <CONTACT:C1> to ask if the
reason is good enough to ignore there being no data.

If you are ignoring the data please update the monitoring comment on ARI 
monitoring.

If there was no good reason please contact <CONTACT:C2> the following
people stating there was no data on the ESO archive.

Note that even if confirmed that there is expected to be no data please still 
run the manual trigger. In the APERO processing step you will be prompted to 
continue you can say “No” (this will just skip the processing step) but all 
the other manual trigger steps should still run.


### If there is data on the ESO archive

This means that we have a problem downloading the data from the ESO archive.

Please contact the <CONTACT:C3> stating that there was no data on our 
machines but was data on the ESO archive.

"""

# Define contact information for this check (for displaying in documentation)
clist1 = contacts.AperoCheckContactList()
clist1.add(contacts.NJC, starred=True)
clist1.add(contacts.LM)
clist1.add(contacts.FB)
clist1.add(contacts.EA)

clist2 = contacts.AperoCheckContactList()
clist2.add(contacts.CL_SERVICE_DESK, starred=True)
clist2.add(contacts.CURRENT_OBSERVER)
clist2.add(contacts.TELESCOPE_3P6)
clist2.add(contacts.TELESCOPE_DNOS)
clist2.add(contacts.GLC)
clist2.add(contacts.NJC)
clist2.add(contacts.LM)
clist2.add(contacts.FB)
clist2.add(contacts.EA)
clist2.add(contacts.XD)

clist3 = contacts.AperoCheckContactList()
clist3.add(contacts.TV, starred=True)
clist3.add(contacts.LM)
clist3.add(contacts.NJC)

CHECK.contact_list['C1'] = clist1
CHECK.contact_list['C2'] = clist2 
CHECK.contact_list['C3'] = clist3


# =============================================================================
# Define check function
# =============================================================================
def check_function(instrument: str, obs_dir: str,
                   aparams: dict, dbparams: dict) -> Tuple[bool, str]:
    """Check that the requested obsdir exists and contains FITS files."""
    _ = instrument, dbparams
    obs_path, files = raw_common.list_obsdir_files(aparams, obs_dir)

    if not obs_path.exists():
        message = (
            f'Observation directory {obs_dir} does not exist in '
            f'{obs_path.parent}'
        )
        return False, message

    if len(files) == 0:
        return False, f'No FITS files found in {obs_path}'

    message = (
        f'Observation directory {obs_dir} exists with {len(files)} '
        'FITS files.'
    )
    return True, message


# =============================================================================
# Must put the function to run for this check
# =============================================================================
CHECK.func = check_function


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    _instrument = 'NIRPS_HA'
    _obs_dir = '2021-01-01'
    _aparams = raw_common.load_example_aparams(_instrument)
    _dbparams = dict()
    CHECK(_instrument, _obs_dir, _aparams, _dbparams, check_dict={})
    print(CHECK.report())


# =============================================================================
# End of code
# =============================================================================