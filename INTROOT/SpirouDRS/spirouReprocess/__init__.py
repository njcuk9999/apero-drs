#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-06-10 at 10:48

@author: cook
"""

from . import spirouRfiles
from . import spirouRgen
from . import spirouRprocess

# =============================================================================
# Define functions
# =============================================================================
FindRawFiles = spirouRfiles.find_raw_files

FindTmpFiles = spirouRfiles.find_tmp_files

FindRedFiles = spirouRfiles.find_reduced_files

GenerateRunList = spirouRgen.generate

ProcessRunList = spirouRprocess.process_run_list

ResetFiles = spirouRfiles.reset

RunFile = spirouRfiles.read_run_file

SendEmail = spirouRfiles.send_email

# =============================================================================
# End of code
# =============================================================================
