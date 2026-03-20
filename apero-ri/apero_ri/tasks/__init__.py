#!/usr/bin/env python
# -*- coding: utf-8 -*-
from apero_ri.tasks import apero_backup
from apero_ri.tasks import apero_object_table
from apero_ri.tasks import apero_observation_table

# =============================================================================
# TASK LIST
# =============================================================================
# This is a list of tasks (apero_async.AperoAsyncTask children) 
# that are available in APERO RI. 
# The key is the name of the task and the value is the class of the task.
TASK_LIST = dict()
TASK_LIST['ARI_LOCAL_DATA_BACKUP'] = apero_backup.AperoLocalDataBackupTask
TASK_LIST['APERO_OBJECT_TABLE'] = apero_object_table.AperoObjectTableTask
TASK_LIST['APERO_OBS_TABLE'] = apero_observation_table.AperoObservationTableTask

# =============================================================================
# TASK PARAMETER LIST
# =============================================================================
# This is a list of parameters that are required for each task.
# This keys should match TASK_LIST (None means no parameters required)
P_LIST = dict()
P_LIST['ARI_LOCAL_DATA_BACKUP'] = apero_backup.PARAM_LIST
P_LIST['APERO_OBJECT_TABLE'] = apero_object_table.PARAM_LIST
P_LIST['APERO_OBS_TABLE'] = apero_observation_table.PARAM_LIST

# =============================================================================
# TASK APERO_PROFILE PARAMETER LIST
# =============================================================================
# This is a list of parameters that are required for each apero profile.
# If this is not None there needs to be APERO_PROFILES 
# and APERO_PROFILE_NAMES defined in P_LIST
# This keys should match TASK_LIST (None means no parameters required)
AP_LIST = dict()
AP_LIST['ARI_LOCAL_DATA_BACKUP'] = apero_backup.APERO_PROFILE_PARAM_LIST
AP_LIST['APERO_OBJECT_TABLE'] = apero_object_table.APERO_PROFILE_PARAM_LIST
AP_LIST['APERO_OBS_TABLE'] = apero_observation_table.APERO_PROFILE_PARAM_LIST

# =============================================================================
# TASK DEFAULT FREQUENCY
# =============================================================================
# This is the default frequency (in hours) for each task. This is used in the admin portal to set the default frequency for each task.
# This keys should match TASK_LIST (None means no default frequency)
FREQ = dict()
FREQ['ARI_LOCAL_DATA_BACKUP'] = apero_backup.DEFAULT_FREQUENCY
FREQ['APERO_OBJECT_TABLE'] = apero_object_table.DEFAULT_FREQUENCY
FREQ['APERO_OBS_TABLE'] = apero_observation_table.DEFAULT_FREQUENCY

# =============================================================================
# TASK DEFAULT ENABLED
# =============================================================================
# This is whether the task is enabled by default in the admin portal. This is used in the admin portal to set the default enabled status for each task.
# This keys should match TASK_LIST (None means no default enabled status)
ENABLED = dict()
ENABLED['ARI_LOCAL_DATA_BACKUP'] = apero_backup.DEFAULT_ENABLED
ENABLED['APERO_OBJECT_TABLE'] = apero_object_table.DEFAULT_ENABLED
ENABLED['APERO_OBS_TABLE'] = apero_observation_table.DEFAULT_ENABLED

# =============================================================================
# TASK TYPE
# =============================================================================
# This is the type of task (INSTRUMENT, GLOBAL). This is used in the admin portal to group tasks by type.
# This keys should match TASK_LIST (None means no task type)
TYPE = dict()
TYPE['ARI_LOCAL_DATA_BACKUP'] = apero_backup.TASK_TYPE
TYPE['APERO_OBJECT_TABLE'] = apero_object_table.TASK_TYPE
TYPE['APERO_OBS_TABLE'] = apero_observation_table.TASK_TYPE