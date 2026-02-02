#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-11-19 at 14:33

@author: cook
"""
import os
import shutil
import urllib.error
import urllib.request
from pathlib import Path

import yaml
from tqdm import tqdm

from aperocore import drs_lang
from aperocore.base import base
from aperocore.constants import param_functions
from aperocore.core import drs_log
from aperocore.core import drs_misc
from aperocore.core import drs_text

# =============================================================================
# Define variables
# =============================================================================
__PATH__ = Path(__file__).parent.parent.parent
__NAME__ = 'apero.setup.drs_demo.py'
__INSTRUMENT__ = 'None'
# load the yaml file
__YAML__ = yaml.load(open(__PATH__.joinpath('info.yaml')),
                     Loader=yaml.FullLoader)
# =============================================================================
# Get variables from info.yaml
# =============================================================================
__version__ = base.__version__
__date__ = base.__date__
__authors__ = __YAML__['DRS.AUTHORS']
__release__ = __YAML__['DRS.RELEASE']
INSTRUMENTS = __YAML__['DRS.INSTRUMENTS']
# -----------------------------------------------------------------------------
# get print colours
COLOR = drs_misc.Colors()
# get ParamDict
ParamDict = param_functions.ParamDict
# get execptions
AperoCodedException = drs_log.AperoCodedException
# get WLOG
WLOG = drs_log.wlog
# get textwrap
textentry = drs_lang.textentry
# get the user input function
user_input = drs_text.user_input
# path to mini data resources
SETUP_PATH = os.path.dirname(os.path.dirname(__file__))
RES_PATH = os.path.join(SETUP_PATH, 'resources')
# path to demo yaml file
DEMO_FILE = os.path.join(RES_PATH, 'demos.yaml')


# =============================================================================
# Define user functions
# =============================================================================
def start_from_demo(params: ParamDict):
    # first check if demo setup is enabled
    if not params.get('DISABLE_DEMO_PROMPT', False):
        return
    # Load the mini data set configuration from YAML file
    yaml_dict = base.load_yaml(DEMO_FILE)
    # Get the path to the raw data directory
    output_dir = params['PATH.RAW']
    # -------------------------------------------------------------------------
    # Step 1: Prompt user and display welcome message
    if not _ask_start_from_minidata(params):
        return 0
    # -------------------------------------------------------------------------
    # Step 2-3: Show available mini data sets and ask user to select one
    selected_key = _select_demo(params, yaml_dict)
    if selected_key is None:
        return 0
    # -------------------------------------------------------------------------
    # Step 4: Load file list and check for missing files
    selected_info = yaml_dict[selected_key]
    file_paths = _load_file_list(params, selected_info, selected_key)
    if file_paths is None:
        return 1
    missing_files = _check_missing_files(params, file_paths, output_dir)
    # -------------------------------------------------------------------------
    # Step 5-7: If missing files, prompt for source and transfer them
    if missing_files:
        # Prompt user for download/copy source
        slargs = [params, selected_info, missing_files, len(file_paths)]
        source_type, source_location = _get_source_location(*slargs)
        if source_type is None:
            return 0
        # ---------------------------------------------------------------------
        # Ask user for copy method if using directory source
        copy_method = _get_copy_method(params, source_type)
        # ---------------------------------------------------------------------
        # Transfer the files
        targs = [params, missing_files, output_dir, source_type,
                 source_location, copy_method]
        success = _transfer_files(*targs)
        if not success:
            return 1
    else:
        # Notify user all files are already present
        _print_all_files_present(params, file_paths, output_dir)
    # -------------------------------------------------------------------------
    # Step 8: Offer to clean up extraneous files (if any exist)
    _cleanup_extraneous_files(params, yaml_dict, output_dir)
    # -------------------------------------------------------------------------
    return 0


# =============================================================================
# Define worker functions
# =============================================================================
def _ask_start_from_minidata(params):
    '''
    Ask user if they want to start from a mini data set.

    Parameters
    ----------
    params : ParamDict
        Parameter dictionary of constants

    Returns
    -------
    bool
        True if user wants to continue, False otherwise
    '''
    # Display banner
    WLOG(params, '', '='*80)
    WLOG(params, '', 'Demo setup')
    WLOG(params, '', '='*80)
    # Ask user for confirmation
    question = ('\nWould you like to start from a demo set? '
                '(yes/no): ')
    response = drs_text.user_input(question, dtype='YN')
    # Return False if user declines
    if not response:
        WLOG(params, '', 'Exiting demo setup.')
        return False
    # Return True to continue
    return True


def _select_demo(params, yaml_dict):
    '''
    Display available demo sets and let user select one.

    Parameters
    ----------
    params : ParamDict
        Parameter dictionary of constants
    yaml_dict : dict
        Dictionary of mini data sets from YAML file

    Returns
    -------
    str or None
        Selected mini data set key, or None if user cancels
    '''
    # Prompt user for selection
    question = ('\nWhich demo set would you like to use? '
                '(Enter number or press Ctrl+C to exit): ')
    # Get list of available mini data set keys
    available_keys = list(yaml_dict.keys())
    options = list(range(1, len(available_keys) + 1))
    # Loop until user makes valid selection
    selected_key = None
    selected_info = 'None'
    # loop until valid selection or Ctrl+C given
    while selected_key is None:
        try:
            selection = drs_text.user_input(question, dtype=int,
                                            options=options,
                                            optiondescs=available_keys)
            selected_key = available_keys[selection - 1]
            # Get the selected mini data set info
            selected_info = yaml_dict[selected_key]
        except KeyboardInterrupt:
            # User pressed Ctrl+C to exit
            WLOG(params, '', '\n\nExiting mini data setup.')
            return None

    # Display user selection confirmation
    if 'name' not in selected_info:
        wmsg = ('Error: demo yaml for {0} incomplete (missing "name")'
                '\n\tdemo path: {1}')
        wargs = [selected_key, DEMO_FILE]
        WLOG(params, 'warning', wmsg.format(*wargs))
        return None
    # otherwise print selection
    WLOG(params, '', f"\nSelected: {selected_info.get('name', selected_key)}")
    # Return selected key
    return selected_key


def _load_file_list(params, selected_info, selected_key):
    '''
    Load the file list for the selected demo data set.

    Parameters
    ----------
    params : ParamDict
        Parameter dictionary of constants
    selected_info : dict
        Information dictionary for selected demo data set
    selected_key : str
        Key identifier for selected demo data set

    Returns
    -------
    list or None
        List of file paths from the file list, or None on error
    '''
    # Get the file list name from selected info
    file_list_name = selected_info.get('file')
    # Check if file list is defined
    if file_list_name is None:
        emsg = 'Error: No file list defined for {0}'
        eargs = [selected_key]
        raise AperoCodedException(params, message=emsg.format(*eargs),
                                  targs=eargs)
    # Construct full path to file list
    file_list_path = os.path.join(RES_PATH, file_list_name)
    # Check if file list file exists
    if not os.path.exists(file_list_path):
        emsg = 'Error: File list not found at {0}'
        eargs = [file_list_path]
        raise AperoCodedException(params, message=emsg.format(*eargs),
                                  targs=eargs)
    # Read file list from file
    with open(file_list_path, 'r') as f:
        file_paths = [line.strip() for line in f if line.strip()]
    # Return list of file paths
    return file_paths


def _check_missing_files(params, file_paths, output_dir):
    '''
    Check which files from file list are missing in output directory.

    Parameters
    ----------
    params : ParamDict
        Parameter dictionary of constants
    file_paths : list
        List of file paths to check
    output_dir : str
        Path to DRS_DATA_RAW directory

    Returns
    -------
    list
        List of missing file paths
    '''
    # Print status message
    msg = f'\nChecking for {len(file_paths)} files in {output_dir}...'
    WLOG(params, '', msg)
    # Initialize empty list for missing files
    missing_files = []
    # Loop through all expected files
    for file_path in file_paths:
        # Construct full output file path
        output_file = os.path.join(output_dir, file_path)
        # Check if file exists
        if not os.path.exists(output_file):
            # Add to missing files list
            missing_files.append(file_path)
    # Return list of missing files
    return missing_files


def _get_source_location(params, selected_info, missing_files, total_files):
    '''
    Prompt user for source location of files (URL or directory).

    Parameters
    ----------
    params : ParamDict
        Parameter dictionary of constants
    selected_info : dict
        Information dictionary for selected mini data set
    missing_files : list
        List of missing file paths
    total_files : int
        Total number of files expected

    Returns
    -------
    tuple
        (source_type, source_location) or (None, None) if cancelled
    '''
    # Get URL from selected info if available
    url = selected_info.get('url')
    # Initialize variables
    source_type = None
    source_location = None
    # Print status message
    msg = (f'Found {len(missing_files)} missing files out of '
           f'{total_files} total files.')
    WLOG(params, '', msg)
    # Check if URL is available
    if url is not None:
        # URL is available, offer both download and directory options
        # Loop until user makes valid choice
        while source_type is None:
            try:
                # Prompt user for choice
                question = '\nSelect option (or Ctrl+C to exit): '
                # Use drs_text.user_input to get a validated int option with descriptions
                choice = user_input(question, dtype=int, options=[1, 2],
                                  optiondescs=['Download from URL',
                                               'Copy from raw data directory'])
                # Check user choice
                if choice == 1:
                    # User chose to download from URL
                    source_type = 'url'
                    source_location = url
                elif choice == 2:
                    # User chose to copy from directory
                    source_type = 'directory'
                    # Prompt for raw data directory path using PATH dtype
                    question = 'Enter path to raw data directory: '
                    raw_dir = user_input(question, dtype='PATH')
                    # Check if directory exists
                    if not os.path.exists(raw_dir):
                        emsg = f'Directory does not exist: {raw_dir}'
                        WLOG(params, 'warning', emsg)
                        continue
                    # Store directory path as string
                    source_location = str(raw_dir)
                else:
                    # Inform user of valid choices (shouldn't happen with user_input)
                    WLOG(params, 'warning', 'Invalid choice. Enter 1 or 2.')
            except KeyboardInterrupt:
                # User pressed Ctrl+C to exit
                WLOG(params, '', '\n\nExiting mini data setup.')
                return None, None
    else:
        # No URL available, only ask for directory
        WLOG(params, '', '\nNo URL available for download.')
        # Loop until user provides valid directory
        while source_location is None:
            try:
                # Prompt for raw data directory path
                question = 'Enter path to raw data directory: '
                raw_dir = user_input(question, dtype='PATH')
                # Check if directory exists
                if not os.path.exists(raw_dir):
                    emsg = f'Directory does not exist: {raw_dir}'
                    WLOG(params, 'warning', emsg)
                    continue
                # Store directory information
                source_type = 'directory'
                source_location = str(raw_dir)
            except KeyboardInterrupt:
                # User pressed Ctrl+C to exit
                WLOG(params, '', '\n\nExiting mini data setup.')
                return None, None
    # Return source type and location
    return source_type, source_location


def _get_copy_method(params, source_type):
    '''
    Ask user whether to symlink or copy files (for directory sources).

    Parameters
    ----------
    params : ParamDict
        Parameter dictionary of constants
    source_type : str
        Type of source ('url' or 'directory')

    Returns
    -------
    str
        Copy method ('copy' or 'symlink')
    '''
    # Default to copy method
    copy_method = 'copy'
    # Only ask about copy method for directory sources
    if source_type == 'directory':
        # Loop until user makes valid choice
        while True:
            try:
                # options descriptions
                optiondescs = ['Symlink (faster, requires source directory '
                               'to remain)',
                               'Copy (slower, but independent of source)']
                # Prompt user for method choice with descriptions
                question = '\nSelect file transfer method (or Ctrl+C to exit): '
                method_choice = user_input(question, dtype=int, options=[1, 2],
                                         optiondescs=optiondescs)
                # Check user choice
                if method_choice == 1:
                    # User chose symlink
                    copy_method = 'symlink'
                    break
                elif method_choice == 2:
                    # User chose copy
                    copy_method = 'copy'
                    break
                else:
                    # Inform user of valid choices (shouldn't happen with user_input)
                    WLOG(params, 'warning', 'Invalid choice. Enter 1 or 2.')
            except KeyboardInterrupt:
                # User pressed Ctrl+C to exit
                WLOG(params, '', '\n\nExiting mini data setup.')
                return None
    # Return copy method
    return copy_method


def _transfer_files(params, missing_files, output_dir, source_type,
                    source_location, copy_method):
    '''
    Transfer missing files from source to output directory.

    Parameters
    ----------
    params : ParamDict
        Parameter dictionary of constants
    missing_files : list
        List of missing file paths to transfer
    output_dir : str
        Path to DRS_DATA_RAW directory
    source_type : str
        Type of source ('url' or 'directory')
    source_location : str
        Location of source (URL or directory path)
    copy_method : str
        Copy method ('copy' or 'symlink')

    Returns
    -------
    bool
        True if successful, False if errors occurred
    '''
    # Display transfer method and file count
    msg = f'\n{copy_method.capitalize()}ing {len(missing_files)} files...'
    WLOG(params, '', msg)
    WLOG(params, '', '-'*80)
    # Initialize error tracking
    errors = []
    success_count = 0
    # Loop through each missing file
    for file_path in tqdm(missing_files, desc='Processing files'):
        # Construct full output file path
        output_file = os.path.join(output_dir, file_path)
        # Get the directory path for output file
        output_dir_path = os.path.dirname(output_file)
        # Create output directory if it doesn't exist
        os.makedirs(output_dir_path, exist_ok=True)
        # Attempt to transfer file
        try:
            if source_type == 'url':
                # Construct full URL for file
                source_url = f"{source_location.rstrip('/')}/{file_path}"
                # Download file from URL
                urllib.request.urlretrieve(source_url, output_file)
                # Increment success counter
                success_count += 1
            elif source_type == 'directory':
                # Construct source file path
                source_file = os.path.join(source_location, file_path)
                # Check if source file exists
                if not os.path.exists(source_file):
                    # Add error message
                    errors.append(f'File not found: {source_file}')
                    continue
                # Check copy method
                if copy_method == 'symlink':
                    # Create symbolic link
                    os.symlink(source_file, output_file)
                else:
                    # Copy file with metadata preserved
                    shutil.copy2(source_file, output_file)
                # Increment success counter
                success_count += 1
        except urllib.error.URLError as e:
            # Catch URL download errors
            errors.append(f'URL error for {file_path}: {e}')
        except FileNotFoundError as e:
            # Catch file not found errors
            errors.append(f'File not found: {file_path} - {e}')
        except Exception as e:
            # Catch all other exceptions
            errors.append(f'Error processing {file_path}: {e}')
    # Print completion separator
    WLOG(params, '', '-'*80)
    # Format and display completion message
    msg = (f'\nCompleted: {success_count}/{len(missing_files)} files '
           f'processed successfully.')
    WLOG(params, '', msg)
    # Check if any errors occurred
    if errors:
        # Display error count
        WLOG(params, 'warning', f'\nEncountered {len(errors)} errors:')
        # Display first 10 errors
        for error in errors[:10]:
            WLOG(params, 'warning', f'  - {error}')
        # Indicate if there are more errors
        if len(errors) > 10:
            msg = f'  ... and {len(errors) - 10} more errors.'
            WLOG(params, 'warning', msg)
        # Return False to indicate failure
        return False
    # Display success message
    WLOG(params, 'info', '\nMini data setup completed successfully!')
    # Return True to indicate success
    return True


def _print_all_files_present(params, file_paths, output_dir):
    '''
    Print message when all files are already present.

    Parameters
    ----------
    params : ParamDict
        Parameter dictionary of constants
    file_paths : list
        List of all expected file paths
    output_dir : str
        Path to DRS_DATA_RAW directory
    '''
    # Format message with file count and directory
    msg = (f'All {len(file_paths)} files are already '
           f'present in {output_dir}')
    # Display the message
    WLOG(params, 'info', msg)


def _cleanup_extraneous_files(params, yaml_dict, output_dir):
    '''
    Remove files from DRS_DATA_RAW that aren't part of any mini data set.

    Parameters
    ----------
    params : ParamDict
        Parameter dictionary of constants
    yaml_dict : dict
        Dictionary of mini data sets from YAML file
    output_dir : str
        Path to DRS_DATA_RAW directory
    '''
    # Collect all files that are part of any mini data set
    all_minidata_files = set()
    for key in yaml_dict.keys():
        file_list_name = yaml_dict[key].get('file')
        if file_list_name is None:
            continue
        # Construct path to file list
        file_list_path = os.path.join(RES_PATH, file_list_name)
        if not os.path.exists(file_list_path):
            continue
        # Read file list
        with open(file_list_path, 'r') as f:
            file_paths = [line.strip() for line in f if line.strip()]
            for file_path in file_paths:
                all_minidata_files.add(
                    os.path.join(output_dir, file_path)
                )
    # Find all files currently in DRS_DATA_RAW
    existing_files = set()
    for root, dirs, files in os.walk(output_dir):
        for fname in files:
            existing_files.add(os.path.join(root, fname))
    # Find extraneous files
    extraneous_files = sorted(existing_files - all_minidata_files)
    # Check if any extraneous files found
    if not extraneous_files:
        # No files to clean up, exit silently
        return 0
    # Display cleanup banner
    WLOG(params, '', '\n' + '='*80)
    WLOG(params, '', 'Demo Data Set Cleanup')
    WLOG(params, '', '='*80)
    # Display found extraneous files
    msg = f'\nFound {len(extraneous_files)} extraneous files:'
    WLOG(params, '', msg)
    WLOG(params, '', '-'*80)
    for i, fpath in enumerate(extraneous_files[:20], 1):
        rel_path = os.path.relpath(fpath, output_dir)
        WLOG(params, '', f'  {i}. {rel_path}')
    if len(extraneous_files) > 20:
        WLOG(params, '', f'  ... and {len(extraneous_files) - 20} more')
    WLOG(params, '', '-'*80)
    # Now ask user if they want to remove them
    question = ('\nWould you like to remove these extraneous files '
                '(those not in the demo set) '
                'from the raw data directory? (yes/no): ')
    response = user_input(question, dtype='YN')
    if not response:
        WLOG(params, '', 'Skipping removal.')
        return 0
    # Remove extraneous files
    msg = f'\nRemoving {len(extraneous_files)} extraneous files...'
    WLOG(params, '', msg)
    errors = []
    success_count = 0
    # Loop through each extraneous file
    for fpath in tqdm(extraneous_files, desc='Removing files'):
        try:
            # Remove the file
            os.remove(fpath)
            success_count += 1
            # Try to remove empty parent directories
            parent_dir = os.path.dirname(fpath)
            while parent_dir != output_dir:
                try:
                    if not os.listdir(parent_dir):
                        os.rmdir(parent_dir)
                        parent_dir = os.path.dirname(parent_dir)
                    else:
                        break
                except OSError:
                    break
        except Exception as e:
            errors.append(f'Error removing {fpath}: {e}')
    # Display completion separator
    WLOG(params, '', '-'*80)
    # Format and display completion message
    msg = (f'\nCompleted: {success_count}/{len(extraneous_files)} '
           f'files removed successfully.')
    WLOG(params, '', msg)
    # Check if any errors occurred
    if errors:
        WLOG(params, 'warning', f'\nEncountered {len(errors)} errors:')
        for error in errors[:10]:
            WLOG(params, 'warning', f'  - {error}')
        if len(errors) > 10:
            msg = f'  ... and {len(errors) - 10} more errors.'
            WLOG(params, 'warning', msg)
        return 1
    # Display success message
    WLOG(params, 'info', '\nCleanup completed successfully!')
    return 0

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
