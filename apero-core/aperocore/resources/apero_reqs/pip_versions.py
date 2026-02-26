#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-02-25 at 11:22

@author: cook
"""
from tqdm import tqdm


# =============================================================================
# Define variables
# =============================================================================
PIP_FREEZE_FILE = 'pip_freeze.txt'

REQ_FILE = 'requirements_all.txt'
# -----------------------------------------------------------------------------

TRANSLATION = dict()
TRANSLATION['Pillow'] = 'pillow'
TRANSLATION['sqlalchemy_utils'] = 'SQLAlchemy-Utils'

# =============================================================================
# Define functions
# =============================================================================
def function1():
    return 0


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # read pip freeze file
    with open(PIP_FREEZE_FILE, 'r') as f:
        lines = f.readlines()
    # ----------------------------------------------------------------------
    # read the requirements file
    with open(REQ_FILE, 'r') as f:
        req_lines = f.readlines()
    # ----------------------------------------------------------------------
    # find all packages in the requirements file
    req_packages = dict()
    for line in tqdm(req_lines):
        if line.startswith('#'):
            continue
        if line.strip() == '':
            continue

        package = line.split(' ')[0]

        req_packages[package] = line
    # ----------------------------------------------------------------------
    # look for the package in the pip file
    for package in tqdm(req_packages):

        if package in TRANSLATION:
            _package = TRANSLATION[package]
        else:
            _package = package

        version = None
        for line in lines:
            if line.startswith(_package + '=='):
                if '==' in line:
                    version = line.split('==')[1].strip()
                    break
        # if version isn't none update the line in req_packages
        if version is not None:

            package_line = req_packages[package]

            if '# Current version:' in package_line:
                # split at current version
                split_line = package_line.split('# Current version:')[0]
                # add new version
                new_line = split_line + '# Current version: {0}\n'.format(version)
                # update req_packages
                req_packages[package] = new_line
    # ----------------------------------------------------------------------
    # write the new requirements file
    with open(REQ_FILE, 'w') as f:
        for line in tqdm(req_lines):
            if line.startswith('#'):
                f.write(line)
            elif line.strip() == '':
                f.write(line)
            else:
                package = line.split(' ')[0]
                if package in req_packages:
                    f.write(req_packages[package])
                else:
                    f.write(line)



# =============================================================================
# End of code
# =============================================================================
