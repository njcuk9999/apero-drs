#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-08-06 at 10:42

@author: cook
"""
import copy
import textwrap
from typing import Dict, Union

from apero.base import base

# =============================================================================
# Define variables
# =============================================================================
# Define script name
__NAME__ = 'run_functions.py'
__PACKAGE__ = base.__PACKAGE__
__INSTRUMENT__ = 'None'
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# define the run keys
RUN_KEYS: Dict[str, 'RunParam'] = dict()
# define keys which should not be found as recipe RUN_ keys
EXCLUDE_RUN_KEYS = ['RUN_NAME', 'RUN_OBS_DIR', 'RUN_RECIPES']
# Max width of comments
MAX_WIDTH = 77
# run yaml title text
RUN_YAML_TITLE = """
# Note this is a example file
#   Please copy this before making changes
# FOR USE WITH VERSION {0} ({1})
"""

# =============================================================================
# Define functions
# =============================================================================
class RunParam:
    def __init__(self, name: str, value=None, dtype=None, comment=None,
                 dtypei=None, section: str = None, after: str = None):
        self.name = name
        self.value = value
        self.dtype = dtype
        self.dtypei = dtypei
        self.comment = comment
        self.section = section
        self.after = after

    def add(self):
        """
        Add to the global RUN_KEYS dictionary
        """
        global RUN_KEYS
        RUN_KEYS[self.name] = self

    def create_comment(self, current_section_title: str,
                       no_header: bool = False) -> Union[str, None]:
        # storage for commented text returned
        comment_text = ''
        # deal with needing a new section (assume this will change)
        if self.section != current_section_title:
            if not no_header:
                comment_text += '\n' + '-'*MAX_WIDTH + '\n'
            comment_text += self.section
            if not no_header:
                comment_text += '\n' + '-'*MAX_WIDTH + '\n'
        # add the current comment
        if self.comment is not None:
            comment_text += '\n'.join(textwrap.wrap(self.comment, MAX_WIDTH))
            # add a new line
            comment_text += '\n'
        # return this text
        if len(comment_text) == 0:
            return None
        else:
            return comment_text

    def copy(self) -> 'RunParam':
        # deep copy all parameters
        name = copy.deepcopy(self.name)
        value = copy.deepcopy(self.value)
        dtype = copy.deepcopy(self.dtype)
        comment = copy.deepcopy(self.comment)
        dtypei = copy.deepcopy(self.dtypei)
        section = copy.deepcopy(self.section)
        after = copy.deepcopy(self.after)
        # create new run parameter
        return RunParam(name, value, dtype, comment,
                        dtypei, section, after)


# -----------------------------------------------------------------------------
# Define run name
# -----------------------------------------------------------------------------
section = 'Core variables'
ritem = RunParam(name='RUN_NAME',
                 value='Run Unknown',
                 dtype=str,
                 comment='Define run name',
                 section=section)
ritem.add()
# -----------------------------------------------------------------------------
# Define whether to send email (required yagmal)
#   to install yagmail: pip install yagmail
# -----------------------------------------------------------------------------
ritem = RunParam(name='SEND_EMAIL',
                 value=False,
                 dtype=bool,
                 comment='Define whether to send email (required yagmail)'
                         'to install yagmail: pip install yagmail',
                 section=section)
ritem.add()
# -----------------------------------------------------------------------------
# Define email address to send/recieve (send to self)
# -----------------------------------------------------------------------------
ritem = RunParam(name='EMAIL_ADDRESS',
                value=None,
                dtype=str,
                comment='Define email address to send/recieve (send to self)',
                 section=section)
ritem.add()
# -----------------------------------------------------------------------------
# Define single observation directory (for all nights to "All")
ritem = RunParam(name='RUN_OBS_DIR',
                 value='All',
                 dtype=str,
                 comment='Define single observation directory '
                         '(for all nights to "All")',
                 section=section)
ritem.add()
# -----------------------------------------------------------------------------
# Define observation directories to exclude ("None" means no filter)
# -----------------------------------------------------------------------------
ritem = RunParam(name='EXCLUDE_OBS_DIRS',
                 value='All',
                 dtype=list, dtypei=str,
                 comment='Define observation directories to exclude '
                         '("None" means no filter) e.g. 2018-07-31',
                 section=section)
ritem.add()
# -----------------------------------------------------------------------------
# Define observation directories to include ("All" means no filter)
# -----------------------------------------------------------------------------
ritem = RunParam(name='INCLUDE_OBS_DIRS',
                 value='All',
                 dtype=list, dtypei=str,
                 comment='Define observation directories to include '
                         '("All" means no filter) e.g. 2018-07-31',
                 section=section)
ritem.add()
# -----------------------------------------------------------------------------
# Define a pi name list for filtering by ("All" means no filter)
# -----------------------------------------------------------------------------
ritem = RunParam(name='PI_NAMES',
                value='All',
                dtype=list, dtypei=str,
                comment='Define a pi name list for filtering by ("All" means '
                        'no filter)',
                 section=section)
ritem.add()
# -----------------------------------------------------------------------------
# define reference observation directory
# -----------------------------------------------------------------------------
ritem = RunParam(name='REF_OBS_DIR',
                 value=None,
                 dtype=str,
                 comment='Define reference observation directory',
                 section=section)
ritem.add()
# -----------------------------------------------------------------------------
# Number of cores (if negative uses N-ABS(CORES), if zero uses N-1 cores)
# -----------------------------------------------------------------------------
ritem = RunParam(name='CORES',
                 value=5,
                 dtype=int,
                 comment='Number of cores (if negative uses N-ABS(CORES), '
                         'if zero uses N-1 cores)',
                 section=section)
ritem.add()
# -----------------------------------------------------------------------------
# Stop on exception
ritem = RunParam(name='STOP_AT_EXCEPTION',
                 value=False,
                 dtype=bool,
                 comment='Stop on exception',
                 section=section)
ritem.add()
# -----------------------------------------------------------------------------
# Run in test mode (does not run codes)
ritem = RunParam(name='TEST_RUN',
                 value=False,
                 dtype=bool,
                 comment='Run in test mode (does not run codes)',
                 section=section)
ritem.add()
# -----------------------------------------------------------------------------
# Whether to process engineering data
# -----------------------------------------------------------------------------
ritem = RunParam(name='USE_ENGINEERING',
                 value=False,
                 dtype=bool,
                 comment='Whether to process engineering data',
                 section=section)
ritem.add()
# -----------------------------------------------------------------------------
# Whether this is a trigger run
ritem = RunParam(name='TRIGGER_RUN',
                    value=False,
                    dtype=bool,
                    comment='Whether this is a trigger run',
                 section=section)
ritem.add()
# -----------------------------------------------------------------------------
# Use odometer reject list
# -----------------------------------------------------------------------------
ritem = RunParam(name='USE_REJECTLIST',
                 value=True,
                 dtype=bool,
                 comment='Use odometer reject list',
                 section=section)
ritem.add()
# -----------------------------------------------------------------------------
# Recalculate templates if template already exists
# -----------------------------------------------------------------------------
ritem = RunParam(name='RECAL_TEMPLATES',
                 value=True,
                 dtype=bool,
                 comment='Recalculate templates if template already exists',
                 section=section)
ritem.add()
# -----------------------------------------------------------------------------
# Update object database from googlesheet - only recommended if doing a
#    full reprocess with all data (will cause inconsistencies if googlesheet
#    has been updated and you are not reprocessing all new data)
# -----------------------------------------------------------------------------
ritem = RunParam(name='UPDATE_OBJ_DATABASE',
                 value=False,
                 dtype=bool,
                 comment='Update object database from googlesheet - only '
                         'recommended if doing a full reprocess with all data '
                         '(will cause inconsistencies if googlesheet has been '
                         'updated and you are not reprocessing all new data)',
                 section=section)
ritem.add()
# -----------------------------------------------------------------------------
# Update reject database from googlesheet
# -----------------------------------------------------------------------------
ritem = RunParam(name='UPDATE_REJECT_DATABASE',
                 value=True,
                 dtype=bool,
                 comment='Update reject database from googlesheet',
                 section=section)
ritem.add()
# -----------------------------------------------------------------------------
# Update the index database. WARNING only do this if precheck or a previous
#   apero_processing has been run. This will result in bad things if the
#   index database is not update to date.
# -----------------------------------------------------------------------------
ritem = RunParam(name='UPDATE_FILEINDEX_DATABASE',
                 value=True,
                 dtype=bool,
                 comment='Update the index database. WARNING only do this if '
                         'precheck or a previous apero_processing has been run. '
                         'This will result in bad things if the index database '
                         'is not update to date.',
                 section=section)
ritem.add()
# -----------------------------------------------------------------------------
# Select which databases to update. WARNING. You must be 100% sure that
#   databases left out of this list are up to date, otherwise APERO will
#   fail in bad ways. Options are "All", or any combination of the following:
#   "raw", "tmp', "red", "out"
# -----------------------------------------------------------------------------
ritem = RunParam(name='UPDATE_IDATABASE_NAMES',
                 value='All',
                 dtype=str,
                 comment='Select which databases to update. WARNING. You must '
                         'be 100% sure that databases left out of this list are'
                         ' up to date, otherwise APERO will fail in bad ways. '
                         'Options are "All", or any combination of the '
                         'following:'
                         ' "raw", "tmp", "red", "out"',
                 section=section)
ritem.add()
# -----------------------------------------------------------------------------
# Define what to run
# -----------------------------------------------------------------------------
section = """
Define what to run

Note not all of these are used by specific sequences so check the sequences
    to know which ones are used by your sequence
"""
ritem = RunParam(name='RUN_RECIPES',
                 value=dict(),
                 dtype=dict, dtypei=bool,
                 comment=None,
                 section=section)
ritem.add()

# -----------------------------------------------------------------------------
# Define what to skip (if files found)
# -----------------------------------------------------------------------------
section = """
Define what to skip (if files found)
"""
ritem = RunParam(name='SKIP_RECIPES',
                 value=dict(),
                 dtype=dict, dtypei=bool,
                 comment=None,
                 section=section)
ritem.add()

# -----------------------------------------------------------------------------
# Define what to filters to have
# -----------------------------------------------------------------------------
section = """
Define what to filters to have
"""
# set which telluric targets to use (For all tellluric stars All)
#    in make telluric process (MKTELLU*)
ritem = RunParam(name='TELLURIC_TARGETS',
                 value='All',
                 dtype=list, dtypei=str,
                 comment='set which telluric targets to use (For all tellluric '
                         'stars All) in hot star recipes',
                 section=section)
ritem.add()

# set which science targets to use in EXTRACT_ALL and FIT_TELLU
ritem = RunParam(name='SCIENCE_TARGETS',
                 value='All',
                 dtype=list, dtypei=str,
                 comment='set which science targets to use in sciece recipes',
                 section=section)
ritem.add()

# -----------------------------------------------------------------------------
# Run order
# -----------------------------------------------------------------------------
section = """
Run information

  Format:

  id##### = command

  Must start with "id" followed by a number
    The number identifies the order to process in

  If command is a sequence will process all in defined sequence
     valid sequences are:
          pp_seq, pp_seq_opt, full_seq,
          limited_seq, ref_seq, calib_seq,
          tellu_seq, science_seq, eng_seq
"""
ritem = RunParam(name='IDS',
                 value=[],
                 dtype=list, dtypei=str,
                 comment=None,
                 section=section)
ritem.add()


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
