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
    # read the yaml file
    yaml_dict = base.load_yaml(RES_FILE)

    # read params
    params = constants.load()

    # get the raw directory
    output_dir = params['DRS_DATA_RAW']

    # Step 1: Ask if user would like to start from a mini data set
    print('\n' + '='*80)
    print('Mini Data Set Setup')
    print('='*80)
    question = ('\nWould you like to start from a mini data set? '
                '(yes/no): ')
    response = input(question).strip().lower()
    if response not in ['yes', 'y']:
        print('Exiting mini data setup.')
        return 0

    # Step 2: List available mini data sets
    print('\n' + '-'*80)
    print('Available mini data sets:')
    print('-'*80)
    available_keys = list(yaml_dict.keys())
    for idx, key in enumerate(available_keys, 1):
        name = yaml_dict[key].get('name', key)
        print(f'  {idx}. {name} [{key}]')
    print('-'*80)

    # Step 3: Ask which mini data set to start from (validation loop)
    selected_key = None
    while selected_key is None:
        try:
            question = ('\nWhich mini data set would you like to use? '
                        '(Enter number or press Ctrl+C to exit): ')
            selection = input(question).strip()
            selection_idx = int(selection)
            if 1 <= selection_idx <= len(available_keys):
                selected_key = available_keys[selection_idx - 1]
            else:
                emsg = (f'Invalid selection. Please enter a number '
                        f'between 1 and {len(available_keys)}.')
                print(emsg)
        except ValueError:
            print('Invalid input. Please enter a number.')
        except KeyboardInterrupt:
            print('\n\nExiting mini data setup.')
            return 0

    # Get the selected mini data set info
    selected_info = yaml_dict[selected_key]
    print(f"\nSelected: {selected_info.get('name', selected_key)}")

    # Step 4: Load the file list and check for missing files
    file_list_name = selected_info.get('file')
    if file_list_name is None:
        print(f'Error: No file list defined for {selected_key}')
        return 1

    # Load file list
    file_list_path = os.path.join(RES_PATH, file_list_name)
    if not os.path.exists(file_list_path):
        print(f'Error: File list not found at {file_list_path}')
        return 1

    # Read file list
    with open(file_list_path, 'r') as f:
        file_paths = [line.strip() for line in f if line.strip()]

    print(f'\nChecking for {len(file_paths)} files in {output_dir}...')

    # Check for missing files
    missing_files = []
    for file_path in file_paths:
        output_file = os.path.join(output_dir, file_path)
        if not os.path.exists(output_file):
            missing_files.append(file_path)

    if not missing_files:
        msg = (f'All {len(file_paths)} files are already '
               f'present in {output_dir}')
        print(msg)
        return 0

    msg = (f'Found {len(missing_files)} missing files out '
           f'of {len(file_paths)} total files.')
    print(msg)

    # Step 5: Prompt for download or raw data directory
    url = selected_info.get('url')
    source_type = None
    source_location = None

    if url is not None:
        # URL is available, offer download or raw data directory
        print('\nOptions:')
        print('  1. Download from URL')
        print('  2. Copy from raw data directory')

        while source_type is None:
            try:
                question = '\nSelect option (1 or 2, or Ctrl+C to exit): '
                choice = input(question).strip()
                if choice == '1':
                    source_type = 'url'
                    source_location = url
                elif choice == '2':
                    source_type = 'directory'
                    question = 'Enter path to raw data directory: '
                    raw_dir = input(question).strip()
                    if not os.path.exists(raw_dir):
                        print(f'Error: Directory does not exist: {raw_dir}')
                        continue
                    source_location = raw_dir
                else:
                    print('Invalid choice. Please enter 1 or 2.')
            except KeyboardInterrupt:
                print('\n\nExiting mini data setup.')
                return 0
    else:
        # No URL, only ask for raw data directory
        print('\nNo URL available for download.')
        while source_location is None:
            try:
                question = 'Enter path to raw data directory: '
                raw_dir = input(question).strip()
                if not os.path.exists(raw_dir):
                    print(f'Error: Directory does not exist: {raw_dir}')
                    continue
                source_type = 'directory'
                source_location = raw_dir
            except KeyboardInterrupt:
                print('\n\nExiting mini data setup.')
                return 0

    # Step 6: Ask whether to symlink or copy (only for directory sources)
    copy_method = 'copy'
    if source_type == 'directory':
        print('\nFile transfer method:')
        print('  1. Symlink (faster, requires source directory to remain)')
        print('  2. Copy (slower, but independent of source)')

        while True:
            try:
                question = '\nSelect method (1 or 2, or Ctrl+C to exit): '
                method_choice = input(question).strip()
                if method_choice == '1':
                    copy_method = 'symlink'
                    break
                elif method_choice == '2':
                    copy_method = 'copy'
                    break
                else:
                    print('Invalid choice. Please enter 1 or 2.')
            except KeyboardInterrupt:
                print('\n\nExiting mini data setup.')
                return 0

    # Step 7: Copy/download files
    msg = f'\n{copy_method.capitalize()}ing {len(missing_files)} files...'
    print(msg)
    print('-'*80)

    errors = []
    success_count = 0

    for file_path in tqdm(missing_files, desc='Processing files'):
        output_file = os.path.join(output_dir, file_path)
        output_dir_path = os.path.dirname(output_file)

        # Create output directory if it doesn't exist
        os.makedirs(output_dir_path, exist_ok=True)

        try:
            if source_type == 'url':
                # Download from URL
                source_url = f"{source_location.rstrip('/')}/{file_path}"
                urllib.request.urlretrieve(source_url, output_file)
                success_count += 1
            elif source_type == 'directory':
                # Copy or symlink from directory
                source_file = os.path.join(source_location, file_path)
                if not os.path.exists(source_file):
                    errors.append(f'File not found: {source_file}')
                    continue

                if copy_method == 'symlink':
                    os.symlink(source_file, output_file)
                else:
                    shutil.copy2(source_file, output_file)
                success_count += 1
        except urllib.error.URLError as e:
            errors.append(f'URL error for {file_path}: {e}')
        except FileNotFoundError as e:
            errors.append(f'File not found: {file_path} - {e}')
        except Exception as e:
            errors.append(f'Error processing {file_path}: {e}')

    print('-'*80)
    msg = (f'\nCompleted: {success_count}/{len(missing_files)} files '
           f'processed successfully.')
    print(msg)

    if errors:
        print(f'\nEncountered {len(errors)} errors:')
        for error in errors[:10]:  # Show first 10 errors
            print(f'  - {error}')
        if len(errors) > 10:
            print(f'  ... and {len(errors) - 10} more errors.')
        return 1

    print('\nMini data setup completed successfully!')
    return 0


# =============================================================================
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
