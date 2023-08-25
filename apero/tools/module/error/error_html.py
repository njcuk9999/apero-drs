#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on {DATE}

@author: cook
"""

import json
import os
from typing import Dict, List, Union

from astropy.time import Time
from astropy.table import Table
from tqdm import tqdm

from apero.base import base
from apero.core import constants

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'error_html.py'
__INSTRUMENT__ = base.IPARAMS['INSTRUMENT']
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get the parameter dictionary
ParamDict = constants.ParamDict


# =============================================================================
# Define general functions
# =============================================================================
def apero_group_to_date(apero_group: str) -> str:
    """
    Take an apero group string and convert to a date string

    apero group has form APERO-{UNIXTIME * 1e7}-XXXX_{recipe name}

    where unixtime is the time the recipe name was run
    XXXX is 4 random characters

    e.g.

    apero group = APERO-00016406414334182270-Q163_apero_processing

    :param apero_group: str, the apero group string

    :return: str, the "day" (YYYY-mm-dd) the apero_group was run
    """
    try:
        # get the unix string
        raw_unix_str = apero_group.split('-')[2]
        # convert to float
        raw_unix_float = float(raw_unix_str)
        # convert to a time
        unix_time = Time(raw_unix_float / 1e7, format='unix')
        # get obs-dir in our standard format
        obs_dir = unix_time.strftime('%Y-%m-%d')
        # return obs-dir
        return obs_dir
    except Exception as _:
        raise ValueError(f'apero group = {apero_group} invalid')


def pid_to_time(pid: str) -> str:
    """
    Take a pid string and convert to a date string

    pid has form PID-{UNIXTIME * 1e7}-XXXX
    XXXX is 4 random characters

    :param pid: str, the pid string

    :return: str, the time YYYY-mm-dd HH:MM:SS.SSS the pid was run
    """
    try:
        # get the unix string
        raw_unix_str = pid.split('-')[1]
        # convert to float
        raw_unix_float = float(raw_unix_str)
        # convert to a time
        unix_time = Time(raw_unix_float / 1e7, format='unix')
        # get obs-dir in our standard format
        time = unix_time.iso
        # return obs-dir
        return time
    except Exception as _:
        raise ValueError(f'pid = {pid} invalid')


def to_yaml_dict(save_path, save_name, group_date, yaml_dict):
    # ---------------------------------------------------------------------
    # construct path to yaml file
    yaml_file = '{0}.yaml'.format(save_name)
    yaml_path = os.path.join(save_path, group_date)
    # make directory if it does not exist
    if not os.path.exists(yaml_path):
        os.makedirs(yaml_path)
    # save to yaml file
    base.write_yaml(yaml_dict, os.path.join(yaml_path, yaml_file))


def from_outlist(save_path: str, outlist: dict):
    for item in tqdm(outlist):

        # create dictionary for saving to yaml
        yaml_dict = dict()

        # get recipe name
        yaml_dict['RECIPE'] = item['RECIPE']
        # ---------------------------------------------------------------------
        # get shortname
        shortname = ''
        if 'SHORTNAME' in item:
            shortname = item['SHORTNAME']
        elif 'ARGS' in item:
            if 'shortname' in item['ARGS']:
                shortname = item['ARGS']['shortname']
        yaml_dict['SHORTNAME'] = shortname
        # ---------------------------------------------------------------------
        # get runstring
        yaml_dict['RUNSTRING'] = item['RUNSTRING']
        # ---------------------------------------------------------------------
        # get pid
        yaml_dict['PID'] = item['PID']
        # ---------------------------------------------------------------------
        # get time
        yaml_dict['TIME'] = pid_to_time(item['PID'])
        # ---------------------------------------------------------------------
        # get group
        apero_group = ''
        if 'ARGS' in item:
            if 'DRS_GROUP' in item['ARGS']:
                apero_group = item['ARGS']['DRS_GROUP']
        yaml_dict['GROUP'] = apero_group
        # ---------------------------------------------------------------------
        # get group date
        try:
            group_date = apero_group_to_date(apero_group)
            yaml_dict['GROUP_DATE'] = group_date
        except ValueError:
            # get from the PID
            group_date = Time(yaml_dict['TIME']).strftime('%Y-%m-%d')
            yaml_dict['GROUP_DATE'] = group_date
        # ---------------------------------------------------------------------
        # get errors
        errors = []
        if 'ERRORS' in item:
            errors = item['ERRORS']
        yaml_dict['ERRORS'] = errors
        # ---------------------------------------------------------------------
        # get warnings
        warnings = []
        if 'WARNINGS' in item:
            warnings = item['WARNINGS']
        yaml_dict['WARNINGS'] = warnings
        # ---------------------------------------------------------------------
        # save to yaml dict
        to_yaml_dict(save_path, item['PID'], group_date, yaml_dict)


def from_processing_log_file(save_path: str, log_filename: str):
    # load file
    with open(log_filename, 'r') as rfile:
        lines = rfile.readlines()

    # find lines containing "Error found for ID="
    error_lines_start = []
    for row, line in enumerate(lines):
        if 'Error found for ID=' in line:
            error_lines_start.append(row)

    # find the end of the error line
    error_lines_end = error_lines_start[1:] + [len(lines) - 1]

    # now we to make a yaml for each of these
    for it, row in tqdm(enumerate(error_lines_start)):
        # get the recipe
        runstring = lines[row + 1].split('@!|PROC|')[-1]
        # the recipe is the first part of the runstring
        recipe = runstring.split(' ')[0]
        # the short name may be in the runstring after --shortname
        shortname = ''
        if '--shortname=' in runstring:
            shortname = runstring.split('--shortname=')[-1].split(' ')[0]
        elif '--shortname ' in runstring:
            shortname = runstring.split('--shortname ')[-1].split(' ')[0]
        # get the apero log pid
        proc_id = os.path.basename(log_filename).split('.log')[0]
        # the pid cannot be found we have to create one from the filename
        #   and the ID
        idnumber = int(lines[row].split('ID=')[-1].split('\'')[1])
        pid = f'{proc_id}-{idnumber:07d}'
        # get the group from the log_filename
        group = proc_id
        group_date = apero_group_to_date(group)
        # get the time from the group
        time = group_date
        # get the errors
        errors = []
        # errors start from row + 4 and end when we reach another |PROC|
        for row2 in range(row + 4, error_lines_end[it]):
            # get line
            line = lines[row2]
            # if we reach another |PROC| then we are done
            if '|PROC|' in line:
                break
            # append to errors
            errors.append(line)
        # we cannot get the warnings
        warnings = []
        # ---------------------------------------------------------------------
        # create dictionary for saving to yaml
        yaml_dict = dict()
        # get recipe name
        yaml_dict['RECIPE'] = recipe
        # ---------------------------------------------------------------------
        # get shortname
        yaml_dict['SHORTNAME'] = shortname
        # ---------------------------------------------------------------------
        # get runstring
        yaml_dict['RUNSTRING'] = runstring
        # ---------------------------------------------------------------------
        # get pid
        yaml_dict['PID'] = pid
        # ---------------------------------------------------------------------
        # get time
        yaml_dict['TIME'] = time
        # ---------------------------------------------------------------------
        # get group
        yaml_dict['GROUP'] = group
        # ---------------------------------------------------------------------
        # get group date
        yaml_dict['GROUP_DATE'] = group_date
        # ---------------------------------------------------------------------
        # get errors
        yaml_dict['ERRORS'] = errors
        # ---------------------------------------------------------------------
        # get warnings
        yaml_dict['WARNINGS'] = warnings
        # ---------------------------------------------------------------------
        # save to yaml dict
        to_yaml_dict(save_path, pid, group_date, yaml_dict)


def process_load_messages(params: ParamDict):
    """
    Load all messages from the message directory and push into individual
    yaml files

    :param params: ParamDict, the parameter dictionary of constants
    :return: None, writes yaml file to {DRS_DATA_MSG}/yamls
    """
    # construct path to yaml dicts
    yaml_path = os.path.join(params['DRS_DATA_MSG'], 'yamls')
    # get the log path
    log_path = os.path.join(params['DRS_DATA_MSG'], 'tool', 'other')
    # get a list of log files
    log_files = []
    for root, dirs, files in os.walk(log_path):
        for filename in files:
            if filename.endswith('apero_processing.log'):
                log_files.append(os.path.join(root, filename))

    # loop around log files
    for l_it, log_file in enumerate(log_files):
        # print progress
        margs = [l_it + 1, len(log_files), log_file]
        print('[{0}/{1}] Analysing log file: {2}'.format(*margs))
        # make yamls
        from_processing_log_file(yaml_path, log_file)


# =============================================================================
# Define html functions
# =============================================================================
def python_str_to_html_str(value):
    value = str(value)
    value = value.replace('\n', '<br>')
    value = value.replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
    return value


def filtered_html_table(outlist: Dict[int, Dict[str, Union[str, List[str]]]],
                        col_names: List[str],
                        col_types: List[str]):
    """
    Generate a html page with a table of data that can be filtered by column
    values.

    :param outlist: dictionary of dictionaries containing the data to display
                    each primary key is a number (must contain at least 1 row)
    :param col_names:
    :param col_types:
    :return:
    """
    # -------------------------------------------------------------------------
    print('Cleaning table data')
    # clean up outlist
    for idnumber in tqdm(outlist):
        for c_it, column_name in enumerate(col_names):
            if col_types[c_it] == 'list':
                for r_it, row in enumerate(outlist[idnumber][column_name]):
                    value = python_str_to_html_str(row)
                    outlist[idnumber][column_name][r_it] = value
            else:
                value = python_str_to_html_str(outlist[idnumber][column_name])
                outlist[idnumber][column_name] = value
    # -------------------------------------------------------------------------
    print('Generating html page')
    # get the column headers text in html format
    column_headers = "\n".join([f'<th>{col}</th>' for col in col_names])

    # some require special formatting
    filter_data_cols = []
    render_data_cols = []

    for c_it, column_name in enumerate(col_names):
        if col_types[c_it] == 'list':
            filter_data_cols.append(f'row.{column_name}.join("")'
                                    f'.toLowerCase().includes(filterValue)')
            render_data_cols.append(f'<td>${{row.{column_name}'
                                    f'.join("<br>")}}</td>')
        else:
            filter_data_cols.append(f'\nrow.{column_name}'
                                    f'.toLowerCase().includes(filterValue)')
            render_data_cols.append(f'<td>${{row.{column_name}}}</td>')
    # push into string format
    filter_col_str = ' ||'.join(filter_data_cols)
    render_col_str = '\n'.join(render_data_cols)

    html_content = f"""
        <h1>Job Status Report</h1>

        <div>
            <label for="filterSelect">Filter by column:</label>
            <select id="filterSelect"></select>
            <input type="text" id="filterInput" 
                   placeholder="Enter filter value">
            <button id="applyFilter">Apply Filter</button>
        </div>

        <br><br>

        <table id="jobTable">
            <tr>
                """ + column_headers + """
            </tr>
        </table>
        <div id="loading">Loading...</div>
        <script>
            const outlist = JSON.parse(`""" + json.dumps(outlist) + """`);

            const filterSelect = document.getElementById("filterSelect");
            const filterInput = document.getElementById("filterInput");
            const applyFilter = document.getElementById("applyFilter");
            const table = document.getElementById("jobTable");
            const loadingDiv = document.getElementById("loading");

            const columns = Object.keys(outlist[1]);
            columns.forEach(column => {
                const option = document.createElement("option");
                option.text = column;
                filterSelect.add(option);
            });

            applyFilter.addEventListener("click", loadFilteredRows);

            function loadFilteredRows() {
                const filterValue = filterInput.value.toLowerCase();
                const filteredData = Object.values(outlist).filter(row => 
                    """ + filter_col_str + """
                );

                renderRows(filteredData);
            }

            function renderRows(data) {
                table.innerHTML = `
                    <tr>
                        """ + column_headers + """
                    </tr>
                `;

                data.forEach(row => {
                    const newRow = table.insertRow();
                    newRow.innerHTML = `
                        """ + render_col_str + """
                    `;
                });

                loadingDiv.style.display = "none";
            }

            loadFilteredRows();
        </script>
    """
    return html_content



def table_to_outlist(table: Table,
                     col_names: List[str]) -> Dict[int, Dict[str, str]]:
    # storage for return dictionary
    outlist = dict()
    # loop around rows in the table
    for it in range(len(table)):
        outlist[it + 1] = dict()
        # loop around columns
        for column in col_names:
            outlist[it + 1][column] = str(table[column][it])

    return outlist



# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # print hello world
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
