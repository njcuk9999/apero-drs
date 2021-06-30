#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-01-07 at 14:59

@author: cook
"""
from astropy.table import Table
import numpy as np
import os
import shutil
from typing import List, Tuple

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.core import drs_misc
from apero.core.core import drs_log
from apero.core.core import drs_file
from apero.core.core import drs_text
from apero.core.utils import drs_recipe
from apero.io import drs_path
from apero.tools.module.documentation import drs_markdown


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
# get drs classes
ParamDict = constants.ParamDict
PseudoConst = constants.PseudoConstants
DrsRecipe = drs_recipe.DrsRecipe
DrsInputFile = drs_file.DrsInputFile
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
# -----------------------------------------------------------------------------
# definitions dirs
DEF_DIR = '../documentation/working/dev/definitions/'


# =============================================================================
# Define user functions
# =============================================================================
def compile_file_definitions(params: ParamDict, recipe: DrsRecipe):

    # load file mod
    filemod = recipe.filemod.get()
    # load pseudo constants
    pconst = constants.pload()
    # get instrument name
    instrument = params['INSTRUMENT']
    # define file types to add
    sectionnames = ['1. Raw Files', '2. Preprocesed files', '3. Reduced Files',
                    '4. Calibration files', '5 Telluric files']
    filetypes = ['raw_file', 'pp_file', 'red_file', 'calib_file', 'tellu_file']
    # list of columns to be flagged as modified by the DRS
    mod_cols = ['HDR[TRG_TYPE]', 'HDR[DRSMODE]']
    # dict of columns to remove if present
    remove_cols = dict()
    remove_cols['raw_file'] = ['file type']
    remove_cols['red_file'] = ['dbname', 'dbkey']

    # add text to sections
    add_texts = dict()
    # add text for instruments add_text[key] = [instrument, txt file]
    add_texts['raw_file'] = dict(SPIROU='spirou_raw_file_text.rst',
                                 NIRPS_HA='nirps_ha_raw_file_text.rst')
    # storage of output tables
    table_storage = dict()
    mod_storage = dict()
    # -------------------------------------------------------------------------
    # loop around file types
    for filetype in filetypes:
        # log progress
        WLOG(params, '', 'Processing {0}'.format(filetype))
        # get file set
        files = getattr(filemod, filetype).fileset
        # get raw table
        table = _compile_files(params, pconst, files)
        # remove empty columns
        table = _remove_empty_cols(table)
        # remove columns
        if filetype in remove_cols:
            table = _remove_cols(table, remove_cols[filetype])
        # modifiy column names
        table, modded = _modify_cols(table, mod_cols, fmt='{0}\*')
        # print progress - number of file types
        msg = '\tAdding {0} file types'
        WLOG(params, '', msg.format(len(table)))
        # print progress - number of columns
        msg = '\tAdding {0} columns'
        WLOG(params, '', msg.format(len(table.colnames)))
        # push to storage
        table_storage[filetype] = table
        mod_storage[filetype] = modded
    # -------------------------------------------------------------------------
    # get directory to save file to
    def_dir = drs_misc.get_relative_folder(__PACKAGE__, DEF_DIR)
    # storage file names
    filenames = dict()
    # save tables as csv
    for filetype in table_storage:
        # construct filename
        fargs = [instrument.lower(), filetype]
        filename = os.path.join(def_dir, '{0}_{1}.csv'.format(*fargs))
        # print progress
        margs = [filetype, filename]
        WLOG(params, '', 'Saving {0} csv to: {1}'.format(*margs))
        # save table
        table_storage[filetype].write(filename, format='csv', overwrite=True)
        # store filename
        filenames[filetype] = filename
    # -------------------------------------------------------------------------
    # make markdown document
    page_ref = '{0}_file_def'.format(instrument.lower())
    markdown = drs_markdown.MarkDownPage(page_ref)
    # add page title
    markdown.add_title('{0} file definitions'.format(instrument))
    # -------------------------------------------------------------------------
    # get refnames
    refnames = dict()
    for filetype in filetypes:
        refnames[filetype] = '{0}_{1}'.format(instrument.lower(), filetype)
    # add table of contents
    markdown.add_table_of_contents(sectionnames, list(refnames.values()))
    # -------------------------------------------------------------------------
    # loop around table section names
    for it in range(len(sectionnames)):
        # get filetype and name
        filetype = filetypes[it]
        name = sectionnames[it]
        # ------------------------------------------------------------------
        # get filename as just a filename (assume they are in the same
        #     directory)
        filename = os.path.basename(filenames[filetype])
        # ------------------------------------------------------------------
        # add section
        markdown.add_section(name)
        # add reference
        markdown.add_reference(refnames[filetype])
        # ------------------------------------------------------------------
        # add sub-section
        markdown.add_sub_section('{0}.1  File definition table'.format(it + 1))
        # add table
        markdown.add_csv_table(title='{0} file definition table'.format(name),
                               csv_file=filename)
        # ------------------------------------------------------------------
        # add text if required
        if mod_storage[filetype]:
            # construct text to add
            modtext = ('\* these columns may be added/updated by APERO '
                       'before use.')
            markdown.add_text(text=modtext)
        # ------------------------------------------------------------------
        # add HDR text
        hdrtext = '"HDR[XXX]" denotes key from file header'
        markdown.add_text(text=hdrtext)
        # ------------------------------------------------------------------
        # add additional text for this section
        if filetype in add_texts:
            # based on instrument
            if instrument in add_texts[filetype]:
                # construct filename
                basename = add_texts[filetype][instrument]
                filepath = os.path.join(def_dir, basename)
                # add text via filename
                if os.path.exists(filepath):
                    markdown.include_file(filename=filepath)
                else:
                    wmsg = 'Section text "{0}" does not exist'
                    wargs = [filepath]
                    WLOG(params, 'warning', wmsg.format(*wargs))
        # ------------------------------------------------------------------
        # add a back to top
        markdown.add_back_to_top()

    # -------------------------------------------------------------------------
    # construct markdown filename
    markdown_basename = '{0}_file_definitions.rst'.format(instrument.lower())
    markdown_filename = os.path.join(def_dir, markdown_basename)
    # log progress
    WLOG(params, '', 'Writing markdown file: {0}'.format(markdown_filename))
    # write markdown to file
    markdown.write_page(markdown_filename)


def compile_docs(params):
    # get package
    package = params['DRS_PACKAGE']
    # get paths
    doc_dir = drs_misc.get_relative_folder(package, DOC_DIR)
    out_dir = drs_misc.get_relative_folder(package, OUT_DIR)
    # get pdflatex
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
        html_dir = drs_misc.get_relative_folder(package, HTML_DIR)
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
        latex_dir = drs_misc.get_relative_folder(package, LATEX_DIR)
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
    out_dir = drs_misc.get_relative_folder(package, OUT_DIR)
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
# Define worker functions
# =============================================================================
def _compile_files(params: ParamDict, pconst: PseudoConst,
                   fileset: List[DrsInputFile]) -> Table:
    """
    Compile a table of parameters based on an input fileset (list of Drs
    Input Files), one row per input file

    :param params: ParamDict, parameter dictionary of constants
    :param pconst: PsuedoConst, the pseudo constant class
    :param fileset: list of DrsInputFile instances, to make the table

    :return: astropy.table.Table, the astropy table, one row per input file
    """
    # dictionary storage for file summary parameters
    storage = dict()
    # loop around file sets
    for filedef in fileset:
        # get the summary for this file
        filedict = filedef.summary(params, pconst)
        # add to storage
        for key in filedict:
            if key in storage:
                storage[key].append(filedict[key])
            else:
                storage[key] = [filedict[key]]
    # convert storage to table
    table = Table()
    # loop around dictionary keys and add to table
    for key in storage:
        table[key] = storage[key]
    # return the astropy table
    return table


def _remove_empty_cols(table: Table) -> Table:
    """
    Remove empty columns from a table

    :param table: astropy.table.Table

    :return: astropy.table.Table, the updated table without empty columns
    """
    # new table
    newtable = Table()
    # loop around original column names
    for col in table.colnames:
        # empty col
        empty_col = True
        # get unique values for col
        uvalues = np.unique(np.array(table[col]))
        # loop around unique values and see if they are nulls
        for uvalue in uvalues:
            if not drs_text.null_text(uvalue, ['None', '--', '', 'Null']):
                empty_col = False
        # only add non-empty columns
        if not empty_col:
            newtable[col] = np.array(table[col])
    # return new table
    return newtable


def _remove_cols(table: Table, cols: List[str]) -> Table:
    """
    Remove certain columns from table

    :param table: astropy.table.Table - the input astropy
    :param cols: list of strings, the columns to remove

    :return: astropy.table.Table - the update table
    """
    # loop around columns
    for col in cols:
        # only deal with columns in this table
        if col in table.colnames:
            # remove column
            del table[col]
    # return table
    return table


def _modify_cols(table: Table, cols: List[str],
                 fmt: str = '{0}') -> Tuple[Table, bool]:
    """
    Modify column names by given format for "cols"

    :param table: astropy.table.Table - the input astropy
    :param cols: list of strings, the columns to modify
    :param fmt: str, the format by which to modify the columns

    :return: Tuple, 1. astropy.table.Table - the updated table, 2. bool, whether
             table was updated
    """
    modified = False
    # loop around columns
    for col in cols:
        # only deal with columns in this table
        if col in table.colnames:
            # copy values for column
            values = np.array(table[col])
            # remove column
            del table[col]
            # add new column (updated)
            table[fmt.format(col)] = values
            # change modified to True
            modified = True
    # return table
    return table, modified


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
