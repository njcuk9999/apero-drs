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

from apero.base import base
from apero.core.core import drs_break
from apero import lang
from apero.core.core import drs_log
from apero.io import drs_path


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_changelog.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry
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
SSH_USER = 'cook'
SSH_HOST = 'venus.astro.umontreal.ca'
SSH_PATH = '/home/cook/www/apero-drs/'


# =============================================================================
# Define functions
# =============================================================================
def compile_docs(params):
    # get package
    package = params['DRS_PACKAGE']
    # get paths
    doc_dir = drs_break.get_relative_folder(package, DOC_DIR)
    out_dir = drs_break.get_relative_folder(package, OUT_DIR)
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
        # Cleaning build directories
        WLOG(params, '', textentry('40-506-00001'))
        os.system('make clean')
        # ------------------------------------------------------------------
        # build html
        # ------------------------------------------------------------------
        # Compiling HTML
        WLOG(params, '', textentry('40-506-00002'))
        # Running make html
        WLOG(params, '', textentry('40-506-00003'))
        # make html using sphinx
        os.system('make html')
        # construct html directory
        html_dir = drs_break.get_relative_folder(package, HTML_DIR)
        # ------------------------------------------------------------------
        # build latex
        # ------------------------------------------------------------------
        # Compling Latex
        WLOG(params, '', textentry('40-506-00004'))
        # Running make latexpdf
        WLOG(params, '', textentry('40-506-00005'))
        # make latex using sphinx
        os.system('make latexpdf')
        # construct latex directory
        latex_dir = drs_break.get_relative_folder(package, LATEX_DIR)
        # compile latex
        if pdflatex not in ['None', None, '']:
            # change to latex dir
            # Running pdflatex
            WLOG(params, '', textentry('40-506-00006'))
            os.chdir(latex_dir)
            # run pdflatex twice (to build table of contents and cross-links)
            os.system('{0} {1}'.format(pdflatex, LATEX_FILE))
            os.system('{0} {1}'.format(pdflatex, LATEX_FILE))

        # ------------------------------------------------------------------
        # copy files to output directory
        # ------------------------------------------------------------------
        # clear out the output directory
        # Removing content of {0}
        WLOG(params, '', textentry('40-506-00007', args=[out_dir]))
        os.system('rm -rf {0}/*'.format(out_dir))
        # ------------------------------------------------------------------
        # copy all files from the html folder
        # Copying html files
        WLOG(params, '', textentry('40-506-00008'))
        os.system('rm -rf {0}/*'.format(out_dir))
        # copy
        drs_path.copytree(html_dir, out_dir)
        # ------------------------------------------------------------------
        # copy pdf (latex) file
        # Copying pdf
        WLOG(params, '', textentry('40-506-00009'))
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
    out_dir = drs_break.get_relative_folder(package, OUT_DIR)
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
