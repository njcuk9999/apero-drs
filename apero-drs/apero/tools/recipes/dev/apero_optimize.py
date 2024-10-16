#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2022-12-13 at 11:32

@author: cook
"""
import ast
import os
from typing import Dict, List

from aperocore.base import base
from aperocore.core import drs_log
from apero.utils import drs_startup

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_documentation.py'
__INSTRUMENT__ = 'None'
# Get constants
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog


# =============================================================================
# Define functions
# =============================================================================
def main(**kwargs):
    """
    Main function for apero_documentation.py

    :param kwargs: any additional keywords

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(**kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = drs_startup.setup(__NAME__, __INSTRUMENT__, fkwargs)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = drs_startup.run(__main__, recipe, params)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    return drs_startup.end_main(params, llmain, recipe, success, outputs='None')


def __main__(recipe, params):
    pass


def get_all_pyfiles(path: str) -> List[str]:
    # get all python files in a path
    pyfiles = []
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename.endswith('.py'):
                pyfiles.append(os.path.join(root, filename))
    return pyfiles


def check_for_missing_docstrings(path: str) -> Dict[str, List[str]]:
    # get all python files in path
    pyfiles = get_all_pyfiles(path)
    # storage for output
    storage = dict()
    # loop around all files
    for pyfile in pyfiles:
        # store a count
        count = 0
        # print header
        print('=' * 50)
        print(f' {pyfile}')
        print('=' * 50)
        # Open the file and read the source code
        with open(pyfile, 'r') as file:
            src = file.read()
        # try to use ast
        try:
            # Parse the source code into an Abstract Syntax Tree (AST)
            ast_tree = ast.parse(src)
        except Exception as e:
            emsg = f'[Error] {type(e)}: {str(e)}'
            print('\t' + emsg)
            storage[pyfile] = emsg
            continue
        # Iterate through all the function and class definitions in the AST
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.FunctionDef):
                # Check if the function or class has a docstring
                docstring = ast.get_docstring(node)
                # print a message if doc string is missing
                if docstring is None:
                    count += 1
                    if pyfile in storage:
                        storage[pyfile].append(node.name)
                    else:
                        storage[pyfile] = [node.name]
        print(f'\t{count} missing docstrings found')


    return storage



def check_for_usused_functions(path: str) -> Dict[str, List[str]]:
    # get all python files in path
    pyfiles = get_all_pyfiles(path)


    # Keep track of all the defined functions
    defined_funcs = []
    errors = dict()
    # loop around pyfiles
    for pyfile in pyfiles:
        # Open the file and read the source code
        with open(pyfile, 'r') as file:
            src = file.read()
        # try to use ast
        try:
            # Parse the source code into an Abstract Syntax Tree (AST)
            ast_tree = ast.parse(src)
        except Exception as e:
            emsg = f'[Error] {type(e)}: {str(e)}'
            print('\t' + emsg)
            if pyfile in errors:
                errors[pyfile].append(emsg)
            else:
                errors[pyfile] = [emsg]
            continue

        for node in ast.walk(ast_tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef):
                defined_funcs.append(f'{pyfile}.{node.name}')

    import dis

    # The module you want to analyze
    module = 'apero'

    # Get the bytecode for the module
    bytecode = dis.Bytecode(module)

    # Search for any `CALL_FUNCTION` opcodes that do not have a corresponding
    # `POP_TOP` opcode, which indicates that the function was not called
    for instr in bytecode:
        if instr.opname == 'CALL_FUNCTION' and 'POP_TOP' not in [x.opname for x in instr.next_instr]:
            print(f'Function {instr.argval} was not called')


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
