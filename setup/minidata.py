#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2026-01-15 at 15:02

@author: cook
"""
import os
import shutil
import urllib.error
import urllib.request

from tqdm import tqdm

from apero.base import base
from apero.core import constants
from apero.core.core import drs_log

# Get Logging function
WLOG = drs_log.wlog

# =============================================================================
# Define variables
# =============================================================================
# path to mini data resources
RES_PATH = os.path.join(os.path.dirname(__file__), 'minidata')
# path to mini data yaml file
RES_FILE = os.path.join(RES_PATH, 'minidata.yaml')
# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def main():
    # Load the mini data set configuration from YAML file
    yaml_dict = base.load_yaml(RES_FILE)
    # Load the DRS parameters and configuration
    params = constants.load()
    params.set(key='PID', value='0000')
    # Get the path to the raw data directory
    output_dir = params['DRS_DATA_RAW']
    # -------------------------------------------------------------------------
    # Step 1: Prompt user and display welcome message
    if not _ask_start_from_minidata(params):
        return 0
    # -------------------------------------------------------------------------
    # Step 2-3: Show available mini data sets and ask user to select one
    selected_key = _select_minidata(params, yaml_dict)
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
        source_type, source_location = _get_source_location(
            params, selected_info, missing_files, len(file_paths)
        )
        if source_type is None:
            return 0
        # ---------------------------------------------------------------------
        # Ask user for copy method if using directory source
        copy_method = _get_copy_method(params, source_type)
        # ---------------------------------------------------------------------
        # Transfer the files
        success = _transfer_files(
            params, missing_files, output_dir, source_type,
            source_location, copy_method
        )
        if not success:
            return 1
    else:
        # Notify user all files are already present
        _print_all_files_present(params, file_paths, output_dir)
    # -------------------------------------------------------------------------
    # Step 8: Offer to clean up extraneous files
    if _ask_cleanup_files(params):
        _cleanup_extraneous_files(params, yaml_dict, output_dir)
    # -------------------------------------------------------------------------
    return 0


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
    WLOG(params, '', 'Mini Data Set Setup')
    WLOG(params, '', '='*80)
    # Ask user for confirmation
    question = ('\nWould you like to start from a mini data set? '
                '(yes/no): ')
    response = input(question).strip().lower()
    # Return False if user declines
    if response not in ['yes', 'y']:
        WLOG(params, '', 'Exiting mini data setup.')
        return False
    # Return True to continue
    return True


def _select_minidata(params, yaml_dict):
    '''
    Display available mini data sets and let user select one.

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
    # Display mini data set list header
    WLOG(params, '', '\n' + '-'*80)
    WLOG(params, '', 'Available mini data sets:')
    WLOG(params, '', '-'*80)
    # Get list of available mini data set keys
    available_keys = list(yaml_dict.keys())
    # Display each mini data set with its name
    for idx, key in enumerate(available_keys, 1):
        name = yaml_dict[key].get('name', key)
        WLOG(params, '', f'  {idx}. {name} [{key}]')
    WLOG(params, '', '-'*80)
    # Loop until user makes valid selection
    selected_key = None
    while selected_key is None:
        try:
            # Prompt user for selection
            question = ('\nWhich mini data set would you like to use? '
                        '(Enter number or press Ctrl+C to exit): ')
            selection = input(question).strip()
            # Convert selection to integer
            selection_idx = int(selection)
            # Validate selection is in valid range
            if 1 <= selection_idx <= len(available_keys):
                selected_key = available_keys[selection_idx - 1]
            else:
                # Inform user of valid range
                emsg = (f'Invalid selection. Please enter a number '
                        f'between 1 and {len(available_keys)}.')
                WLOG(params, 'warning', emsg)
        except ValueError:
            # Inform user input must be a number
            WLOG(params, 'warning', 'Invalid input. Please enter a number.')
        except KeyboardInterrupt:
            # User pressed Ctrl+C to exit
            WLOG(params, '', '\n\nExiting mini data setup.')
            return None
    # Get the selected mini data set info
    selected_info = yaml_dict[selected_key]
    # Display user selection confirmation
    WLOG(params, '', f"\nSelected: {selected_info.get('name', selected_key)}")
    # Return selected key
    return selected_key


def _load_file_list(params, selected_info, selected_key):
    '''
    Load the file list for the selected mini data set.

    Parameters
    ----------
    params : ParamDict
        Parameter dictionary of constants
    selected_info : dict
        Information dictionary for selected mini data set
    selected_key : str
        Key identifier for selected mini data set

    Returns
    -------
    list or None
        List of file paths from the file list, or None on error
    '''
    # Get the file list name from selected info
    file_list_name = selected_info.get('file')
    # Check if file list is defined
    if file_list_name is None:
        emsg = f'Error: No file list defined for {selected_key}'
        WLOG(params, 'error', emsg)
        return None
    # Construct full path to file list
    file_list_path = os.path.join(RES_PATH, file_list_name)
    # Check if file list file exists
    if not os.path.exists(file_list_path):
        emsg = f'Error: File list not found at {file_list_path}'
        WLOG(params, 'error', emsg)
        return None
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
        WLOG(params, '', '\nOptions:')
        WLOG(params, '', '  1. Download from URL')
        WLOG(params, '', '  2. Copy from raw data directory')
        # Loop until user makes valid choice
        while source_type is None:
            try:
                # Prompt user for choice
                question = '\nSelect option (1 or 2, or Ctrl+C to exit): '
                choice = input(question).strip()
                # Check user choice
                if choice == '1':
                    # User chose to download from URL
                    source_type = 'url'
                    source_location = url
                elif choice == '2':
                    # User chose to copy from directory
                    source_type = 'directory'
                    # Prompt for raw data directory path
                    question = 'Enter path to raw data directory: '
                    raw_dir = input(question).strip()
                    # Check if directory exists
                    if not os.path.exists(raw_dir):
                        emsg = f'Error: Directory does not exist: {raw_dir}'
                        WLOG(params, 'warning', emsg)
                        continue
                    # Store directory path
                    source_location = raw_dir
                else:
                    # Inform user of valid choices
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
                raw_dir = input(question).strip()
                # Check if directory exists
                if not os.path.exists(raw_dir):
                    emsg = f'Error: Directory does not exist: {raw_dir}'
                    WLOG(params, 'warning', emsg)
                    continue
                # Store directory information
                source_type = 'directory'
                source_location = raw_dir
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
        # Display copy method options
        WLOG(params, '', '\nFile transfer method:')
        msg = '  1. Symlink (faster, requires source directory to remain)'
        WLOG(params, '', msg)
        WLOG(params, '', '  2. Copy (slower, but independent of source)')
        # Loop until user makes valid choice
        while True:
            try:
                # Prompt user for method choice
                question = '\nSelect method (1 or 2, or Ctrl+C to exit): '
                method_choice = input(question).strip()
                # Check user choice
                if method_choice == '1':
                    # User chose symlink
                    copy_method = 'symlink'
                    break
                elif method_choice == '2':
                    # User chose copy
                    copy_method = 'copy'
                    break
                else:
                    # Inform user of valid choices
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


def _ask_cleanup_files(params):
    '''
    Ask user if they want to remove extraneous files.

    Parameters
    ----------
    params : ParamDict
        Parameter dictionary of constants

    Returns
    -------
    bool
        True if user wants to clean up, False otherwise
    '''
    # Prompt user for cleanup confirmation
    cleanup_response = input('\nWould you like to remove extraneous files '
                             'from the raw data directory? (yes/no): ')
    # Normalize response to lowercase
    cleanup_response = cleanup_response.strip().lower()
    # Return True if user says yes
    if cleanup_response in ['yes', 'y']:
        return True
    # Return False otherwise
    return False


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
    # Display cleanup banner
    WLOG(params, '', '\n' + '='*80)
    WLOG(params, '', 'Mini Data Set Cleanup')
    WLOG(params, '', '='*80)
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
        WLOG(params, '', '\nNo extraneous files found.')
        return 0
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
    # Prompt user for confirmation
    question = ('\nRemove all extraneous files? (yes/no, or Ctrl+C to '
                'exit): ')
    response = input(question).strip().lower()
    if response not in ['yes', 'y']:
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
# Start of code
# =============================================================================
# Main code here
if __name__ == '__main__':
    # ----------------------------------------------------------------------
    # run main function
    main()

# =============================================================================
# End of code
# =============================================================================
