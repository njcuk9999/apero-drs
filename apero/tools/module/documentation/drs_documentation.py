#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-01-07 at 14:59

@author: cook
"""
import os
import shutil
from distutils.dir_util import copy_tree

from apero import core
from apero.core import constants
from apero import locale


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_changelog.py'
__INSTRUMENT__ = 'None'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get Logging function
WLOG = core.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# --------------------------------------------------------------------------
DOC_DIR = '../documentation/working'
OUT_DIR = '../documentation/output'
HTML_DIR = '../documentation/working/_build/html/'
LATEX_DIR = '../documentation/working/_build/latex/'
LATEX_FILE = 'apero-docs.tex'
PDF_FILE = 'apero-docs.pdf'
# -----------------------------------------------------------------------------
RSYNC_CMD = 'rsync -avz -e "{SSH}" {INPATH} {USER}@{HOST}:{OUTPATH}'
# -----------------------------------------------------------------------------
SSH_OPTIONS = 'ssh -oport=5822'
SSH_USER = 'cpapir'
SSH_HOST = 'genesis.astro.umontreal.ca'
SSH_PATH = '/home/cpapir/www/apero-drs/'


# =============================================================================
# Define functions
# =============================================================================
def compile_docs(params):
    # get package
    package = params['DRS_PACKAGE']
    # get paths
    doc_dir = constants.get_relative_folder(package, DOC_DIR)
    out_dir = constants.get_relative_folder(package, OUT_DIR)
    # get pdflatex
    pdflatex = params['DRS_PDFLATEX_PATH']
    if pdflatex in ['None', None, '']:
        pdflatex = shutil.which('pdflatex')

    # get current directory
    cwd = os.getcwd()

    # everything else inside a try loop
    try:
        # change to doc dir
        os.chdir(doc_dir)
        # ------------------------------------------------------------------
        # clean build
        # ------------------------------------------------------------------
        # TODO: Move to language DB
        WLOG(params, '', 'Cleaning build directories')
        os.system('make clean')
        # ------------------------------------------------------------------
        # build html
        # ------------------------------------------------------------------
        # TODO: Move to language DB
        WLOG(params, '', 'Compiling HTML')
        # TODO: Move to language DB
        WLOG(params, '', '\tRunning make html')
        # make html using sphinx
        os.system('make html')
        # construct html directory
        html_dir = constants.get_relative_folder(package, HTML_DIR)
        # ------------------------------------------------------------------
        # build latex
        # ------------------------------------------------------------------
        # TODO: Move to language DB
        WLOG(params, '', 'Compling Latex')
        # TODO: Move to language DB
        WLOG(params, '', '\tRunning make latexpdf')
        # make latex using sphinx
        os.system('make latexpdf')
        # construct latex directory
        latex_dir = constants.get_relative_folder(package, LATEX_DIR)
        # compile latex
        if pdflatex not in ['None', None, '']:
            # change to latex dir
            # TODO: Move to language DB
            WLOG(params, '', '\tRunning pdflatex')
            os.chdir(latex_dir)
            # run pdflatex twice (to build table of contents and cross-links)
            os.system('{0} {1}'.format(pdflatex, LATEX_FILE))
            os.system('{0} {1}'.format(pdflatex, LATEX_FILE))

        # ------------------------------------------------------------------
        # copy files to output directory
        # ------------------------------------------------------------------
        # clear out the output directory
        # TODO: Move to language DB
        WLOG(params, '', 'Removing content of {0}'.format(out_dir))
        os.system('rm -rf {0}/*'.format(out_dir))
        # ------------------------------------------------------------------
        # copy all files from the html folder
        # TODO: Move to language DB
        WLOG(params, '', 'Copying html files')
        os.system('rm -rf {0}/*'.format(out_dir))
        # copy
        copy_tree(html_dir, out_dir)
        # ------------------------------------------------------------------
        # copy pdf (latex) file
        # TODO: Move to language DB
        WLOG(params, '', 'Copying pdf')
        # construct input/output pdf path
        inpdf = os.path.join(latex_dir, PDF_FILE)
        outpdf = os.path.join(out_dir, PDF_FILE)
        # copy pdf to the output directory
        if os.path.exists(inpdf):
            shutil.copy(inpdf, outpdf)
        # ------------------------------------------------------------------
        # change back to current directory
        os.chdir(cwd)

    except Exception as e:
        # change back to current directory
        os.chdir(cwd)
        # raise exception
        raise e
    except KeyboardInterrupt as e:
        # change back to current directory
        os.chdir(cwd)
        # raise exception
        raise e
    except SystemExit as e:
        # change back to current directory
        os.chdir(cwd)
        # raise exception
        raise e


def upload(params):
    # get package
    package = params['DRS_PACKAGE']
    # get paths
    out_dir = constants.get_relative_folder(package, OUT_DIR)
    # make sure we copy contents not directory
    if not out_dir.endswith(os.sep):
        out_dir += os.sep
    # get rsync dict
    rdict = dict()
    rdict['SSH'] = SSH_OPTIONS
    rdict['USER'] = SSH_USER
    rdict['HOST'] = SSH_HOST
    rdict['INPATH'] = out_dir
    rdict['OUTPATH'] = SSH_PATH
    # run command (will require password)
    os.system(RSYNC_CMD.format(**rdict))


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
