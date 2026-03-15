#!/usr/bin/env python
# -*- coding: utf-8 -*-
from apero_ri.tasks import apero_backup, apero_obj_table

# =============================================================================
# TASK LIST
# =============================================================================
# This is a list of tasks (apero_async.AperoAsyncTask children) 
# that are available in APERO RI. 
# The key is the name of the task and the value is the class of the task.
TASK_LIST = dict()
TASK_LIST['APERO_OBJECT_TABLE'] = apero_obj_table.AperoObjectTableTask
TASK_LIST['ARI_LOCAL_DATA_BACKUP'] = apero_backup.AperoLocalDataBackupTask
# =============================================================================
# TASK PARAMETER LIST
# =============================================================================
# This is a list of parameters that are required for each task.
# This keys should match TASK_LIST (None means no parameters required)
P_LIST = dict()
P_LIST['APERO_OBJECT_TABLE'] = apero_obj_table.PARAM_LIST
P_LIST['ARI_LOCAL_DATA_BACKUP'] = apero_backup.PARAM_LIST

# =============================================================================
# TASK APERO_PROFILE PARAMETER LIST
# =============================================================================
# This is a list of parameters that are required for each apero profile.
# If this is not None there needs to be APERO_PROFILES 
# and APERO_PROFILE_NAMES defined in P_LIST
# This keys should match TASK_LIST (None means no parameters required)
AP_LIST = dict()
AP_LIST['APERO_OBJECT_TABLE'] = apero_obj_table.APERO_PROFILE_PARAM_LIST
AP_LIST['ARI_LOCAL_DATA_BACKUP'] = apero_backup.APERO_PROFILE_PARAM_LIST