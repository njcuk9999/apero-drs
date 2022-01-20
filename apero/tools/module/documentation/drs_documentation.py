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
from typing import Any, Dict, List, Tuple

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
DrsRunSequence = drs_recipe.DrsRunSequence
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
# resource directory
RESOURCE_DIR = '../documentation/working/resources/{0}/'
# file definitions dirs
FILE_DEF_DIR = '../documentation/working/auto/file_definitions/{0}/'
# recipe definitions dirs
RECIPE_DEF_DIR = '../documentation/working/auto/recipe_definitions/{0}/'
RD_REL_PATH = '../../auto/recipe_definitions/{0}/'
RD_REL_SCHEMATIC_PATH = '../../../_static/yed/spirou/'
RD_REL_DOC_PATH = '../documentation/working/main/{0}/'
RD_REL_DOC_FILE = 'recipes_{0}.rst'
# recipe sequences dirs
SEQUENCE_DEF_DIR = '../documentation/working/auto/recipe_sequences/{0}/'
RS_REL_PATH = '../../auto/recipe_sequences/{0}/'
RS_REL_DOC_PATH = '../documentation/working/main/{0}/'
RS_REL_DOC_FILE = 'using_apero_{0}.rst'
# define raw and post files per instrument
RAW_FILE_DEF_TEXT_FILE = dict(SPIROU='spirou_raw_file_text.rst',
                              NIRPS_HA='nirps_ha_raw_file_text.rst',
                              NIRPS_HE='nirps_he_raw_file_text.rst')
POST_FILE_DEF_TEXT_FILE = dict(SPIROU='spirou_post_file_text.rst',
                               NIRPS_HA='nirps_ha_post_file_text.rst',
                               NIRPS_HE='nirps_he_post_file_text.rst')


# =============================================================================
# Define user functions
# =============================================================================
def compile_file_definitions(params: ParamDict, recipe: DrsRecipe):
    """
    Compile file definitions as an rst file for sphinx documentation

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe instance, the recipe that called this function

    :return: None writes to file definition rst files
    """
    # load file mod
    filemod = recipe.filemod.get(force=True)
    # get instrument name
    instrument = params['INSTRUMENT']
    # load pseudo constants
    pconst = constants.pload(instrument=instrument)
    # define file types to add
    sectionnames = ['1. Raw Files', '2. Preprocesed files', '3. Reduced Files',
                    '4. Calibration files', '5. Telluric files',
                    '6. Post-processed files']
    filetypes = ['raw_file', 'pp_file', 'red_file', 'calib_file', 'tellu_file',
                 'post_file']
    # list of columns to be flagged as modified by the DRS
    mod_cols = ['HDR[TRG_TYPE]', 'HDR[DRSMODE]']
    # dict of columns to remove if present
    remove_cols = dict()
    remove_cols['raw_file'] = ['file type']
    remove_cols['red_file'] = ['dbname', 'dbkey']
    # add text to sections
    add_texts = dict()
    # add text for instruments add_text[key] = [instrument, txt file]
    add_texts['raw_file'] = RAW_FILE_DEF_TEXT_FILE
    add_texts['post_file'] = POST_FILE_DEF_TEXT_FILE
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
    file_def_dir = FILE_DEF_DIR.format(instrument.lower())
    def_dir = drs_misc.get_relative_folder(__PACKAGE__, file_def_dir)
    # storage file names
    filenames = dict()
    # save tables as csv
    for filetype in table_storage:
        # construct filename
        fargs = [instrument.lower(), filetype]
        filename = '{0}_{1}.csv'.format(*fargs)
        abs_filename = os.path.join(def_dir, filename)
        # print progress
        margs = [filetype, abs_filename]
        WLOG(params, '', 'Saving {0} csv to: {1}'.format(*margs))
        # save table
        table_storage[filetype].write(abs_filename, format='csv',
                                      overwrite=True)
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
    markdown.add_table_of_contents(list(refnames.values()), sectionnames)
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
        resource_dir = RESOURCE_DIR.format(instrument.lower())
        res_dir = drs_misc.get_relative_folder(__PACKAGE__, resource_dir)
        # add additional text for this section
        if filetype in add_texts:
            # based on instrument
            if instrument in add_texts[filetype]:
                # construct filename
                basename = add_texts[filetype][instrument]
                filepath = os.path.join(res_dir, basename)
                # add text via filename
                if os.path.exists(filepath):
                    markdown.include_file(filename=filepath)
                else:
                    # TODO: move to language database
                    wmsg = 'Section text "{0}" does not exist'
                    wargs = [filepath]
                    WLOG(params, 'warning', wmsg.format(*wargs), sublevel=4)
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


def compile_recipe_definitions(params: ParamDict, recipe: DrsRecipe):
    """
    Compile recipe definitions as rst files for sphinx documentation

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe instance, the recipe that called this function

    :return: None writes to file definition rst files
    """
    # load file mod
    recipemod = recipe.recipemod.get(force=True)
    # get instrument name
    instrument = params['INSTRUMENT']
    # load pseudo constants
    pconst = constants.pload(instrument=instrument)
    # get a list of recipe instances
    srecipes = recipemod.recipes
    # get directory to save file to
    recipe_def_dir = RECIPE_DEF_DIR.format(instrument.lower())
    def_dir = drs_misc.get_relative_folder(__PACKAGE__, recipe_def_dir)
    # store list of recipe definitions
    recipe_definitions = []
    # loop around recipes
    for srecipe in srecipes:
        # print we are analysing recipe
        margs = [srecipe.name, srecipe.shortname]
        WLOG(params, 'info', 'Processing {0} [{1}]'.format(*margs))
        # get summary parameters
        summary = _compile_recipe(params, pconst, instrument, srecipe)
        # create page ref
        pargs = [instrument.lower(), summary['SHORTNAME'].lower()]
        page_ref = 'recipes_{0}_{1}'.format(*pargs)
        # start markdown page
        markdown = drs_markdown.MarkDownPage(page_ref)
        # add title
        name = summary['NAME'].strip('.py')
        markdown.add_title('{0}'.format(name))
        # ---------------------------------------------------------------------
        # add section: description
        markdown.add_section('1. Description')
        # add shortname
        markdown.add_text('SHORTNAME: {0}'.format(summary['SHORTNAME']))
        # add description
        if summary['DESCRIPTION_FILE'] is not None:
            # include a file
            markdown.include_file(summary['DESCRIPTION_FILE'])
        else:
            markdown.add_text('No description set')
        # ---------------------------------------------------------------------
        # add section: schematic
        markdown.add_section('2. Schematic')
        # add schematic image
        if summary['SCHEMATIC_FILE'] is not None:
            # get schematic path
            basename = summary['SCHEMATIC_FILE']
            schpath = os.path.join(RD_REL_SCHEMATIC_PATH, basename)
            # include a file
            markdown.add_image(schpath, width=100, align='center')
        else:
            markdown.add_text('No schematic set')
        # ---------------------------------------------------------------------
        # add section: usage
        markdown.add_section('3. Usage')
        # add code block for run
        markdown.add_code_block('', [summary['USAGE']])
        # add code block for positional arguments
        if len(summary['LPOS']) > 0:
            markdown.add_code_block('', summary['LPOS'])
        else:
            markdown.add_text('No optional arguments')
        # ---------------------------------------------------------------------
        # add section: optional arguments
        markdown.add_section('4. Optional Arguments')
        # add code block for run
        if len(summary['LOPT']) > 0:
            markdown.add_code_block('', summary['LOPT'])
        else:
            markdown.add_text('No optional arguments')
        # ---------------------------------------------------------------------
        # add section: special arguments
        markdown.add_section('5. Special Arguments')
        # add code block for run
        if len(summary['LSOPT']) > 0:
            markdown.add_code_block('', summary['LSOPT'])
        else:
            markdown.add_text('No special arguments')
        # ---------------------------------------------------------------------
        # add section: output directory
        markdown.add_section('6. Output directory')
        # add code block for run
        markdown.add_code_block('', [summary['OUTDIR']])
        # ---------------------------------------------------------------------
        # add section: output directory
        markdown.add_section('7. Output files')
        # add code block for run
        markdown.add_csv_table('Outputs', summary['OUTTABLE'])
        # ---------------------------------------------------------------------
        # add section: output directory
        markdown.add_section('8. Debug plots')
        # add code block for run
        if len(summary['DEBUG_PLOTS']) > 0:
            markdown.add_code_block('', summary['DEBUG_PLOTS'])
        else:
            markdown.add_text('No debug plots.')
        # ---------------------------------------------------------------------
        # add section: output directory
        markdown.add_section('9. Summary plots')
        # add code block for run
        if len(summary['SUMMARY_PLOTS']) > 0:
            markdown.add_code_block('', summary['SUMMARY_PLOTS'])
        else:
            markdown.add_text('No summary plots.')
        # ---------------------------------------------------------------------
        # construct markdown filename
        margs = [instrument.lower(), summary['SHORTNAME']]
        markdown_basename = '{0}_recipe_definition_{1}.rst'.format(*margs)
        markdown_filename = os.path.join(def_dir, markdown_basename)
        # log progress
        WLOG(params, '', 'Writing markdown file: {0}'.format(markdown_filename))
        # write markdown to file
        markdown.write_page(markdown_filename)
        # add to list
        recipe_definitions.append(os.path.basename(markdown_filename))
    # -------------------------------------------------------------------------
    # Write recipe_{instrument}.rst (list of recipes)
    # -------------------------------------------------------------------------
    # construct filename
    rs_basename = RS_REL_DOC_FILE.format(instrument.lower())
    # get page reference
    page_ref = 'recipes_{0}'.format(instrument.lower())
    # start markdown page
    markdown = drs_markdown.MarkDownPage(page_ref)
    # add title
    markdown.add_title('{0} recipes'.format(instrument))
    # add text
    text = (f'This section describes all the {instrument} recipes to use with '
            f'APERO. \n For information on how to run these recipes (either '
            f'individually or with the processing tools) see :ref:`here '
            f'<{rs_basename}>`.')
    markdown.add_text(text)
    # construct items for table of contents
    items = []
    # loop around recipe definitions and write to file
    rd_rel_path = RD_REL_PATH.format(instrument.lower())
    for recipe_definition in recipe_definitions:
        items.append(os.path.join(rd_rel_path, recipe_definition))
    # add urls
    markdown.add_table_of_contents(items,
                                   sectionname='{0} recipes'.format(instrument),
                                   maxdepth=1)
    # add back to top
    markdown.add_back_to_top()
    # write file
    doc_path = RD_REL_DOC_PATH.format(instrument.lower())
    rd_basename = RD_REL_DOC_FILE.format(instrument.lower())
    abs_path = drs_misc.get_relative_folder(__PACKAGE__, doc_path)
    markdown.write_page(os.path.join(abs_path, rd_basename))


def compile_recipe_sequences(params: ParamDict, recipe: DrsRecipe):
    """
    Compile recipes sequences as rst files for sphinx documentation

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe instance, the recipe that called this function

    :return: None writes to file definition rst files
    :return:
    """
    # load file mod
    recipemod = recipe.recipemod.get()
    # get instrument name
    instrument = params['INSTRUMENT']
    # get a list of sequences
    sequences = recipemod.sequences
    # get directory to save file to
    sequence_def_dir = SEQUENCE_DEF_DIR.format(instrument.lower())
    def_dir = drs_misc.get_relative_folder(__PACKAGE__, sequence_def_dir)
    # store list of recipe sequences
    recipe_sequences = []
    # loop around recipes
    for sequence in sequences:
        # print we are analysing recipe
        WLOG(params, 'info', 'Processing {0}'.format(sequence.name))
        # get summary parameters for sequence
        summary = _compile_sequence(params, instrument, sequence)
        # ---------------------------------------------------------------------
        # make page
        pargs = [instrument.lower(), summary['NAME']]
        page_ref = '{0}_sequence_{1}'.format(*pargs)
        markdown = drs_markdown.MarkDownPage(page_ref)
        # ---------------------------------------------------------------------
        # add title
        name = summary['NAME']
        markdown.add_title('{0}'.format(name))
        # ---------------------------------------------------------------------
        # add section: output directory
        markdown.add_section('1. Recipes in sequence')
        # add code block for run
        markdown.add_csv_table('Recipes', summary['OUTTABLE'])
        # allow multiple lines in table
        markdown.enable_multiline_table()
        # ---------------------------------------------------------------------
        # construct markdown filename
        margs = [instrument.lower(), summary['NAME']]
        markdown_basename = '{0}_recipe_sequence_{1}.rst'.format(*margs)
        markdown_filename = os.path.join(def_dir, markdown_basename)
        # log progress
        WLOG(params, '', 'Writing markdown file: {0}'.format(markdown_filename))
        # write markdown to file
        markdown.write_page(markdown_filename)
        # add to list
        recipe_sequences.append(os.path.basename(markdown_filename))

    # -------------------------------------------------------------------------
    # Write using_apero_{instrument}.rst (list of sequences + more)
    # -------------------------------------------------------------------------
    # construct filename
    rd_basename = RD_REL_DOC_FILE.format(instrument.lower())
    # get page reference
    page_ref = 'using_apero_{0}'.format(instrument.lower())
    # start markdown page
    markdown = drs_markdown.MarkDownPage(page_ref)
    # add title
    markdown.add_title('{0} sequences'.format(instrument))
    # add text
    text = ('This section describes all the recipe sequences to use with '
            'APERO. \nFor information on individual recipes see :ref:`here '
            '<{0}>`.').format(rd_basename.replace('.rst', ''))
    markdown.add_text(text)
    # construct items for table of contents
    items = []
    # loop around recipe definitions and write to file
    rs_rel_path = RS_REL_PATH.format(instrument.lower())
    for recipe_sequence in recipe_sequences:
        items.append(os.path.join(rs_rel_path, recipe_sequence))
    # add urls
    markdown.add_table_of_contents(items,
                                   sectionname='{0} recipes'.format(instrument),
                                   maxdepth=1)
    # add back to top
    markdown.add_back_to_top()
    # write file
    doc_path = RS_REL_DOC_PATH.format(instrument.lower())
    rd_basename = RS_REL_DOC_FILE.format(instrument.lower())
    abs_path = drs_misc.get_relative_folder(__PACKAGE__, doc_path)
    markdown.write_page(os.path.join(abs_path, rd_basename))


def compile_docs(params: ParamDict, mode: str = 'both'):
    # get package
    package = params['DRS_PACKAGE']
    # get paths
    doc_dir = drs_misc.get_relative_folder(package, DOC_DIR)
    out_dir = drs_misc.get_relative_folder(package, OUT_DIR)
    # get pdflatex
    pdflatex = shutil.which('pdflatex')
    # get current directory
    cwd = os.getcwd()

    if mode == 'both':
        mode = ['html', 'latex']

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
        if 'html' in mode:
            # Compiling HTML
            WLOG(params, '', textentry('40-506-00002'))
            # Running make html
            WLOG(params, '', textentry('40-506-00003'))
            # make html using sphinx
            os.system('make html')
            # construct html directory
            html_dir = drs_misc.get_relative_folder(package, HTML_DIR)
        else:
            html_dir = ''
        # ------------------------------------------------------------------
        # build latex
        # ------------------------------------------------------------------
        if 'latex' in mode:
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
        else:
            latex_dir = ''
        # ------------------------------------------------------------------
        # copy files to output directory
        # ------------------------------------------------------------------
        # clear out the output directory
        # Removing content of {0}
        WLOG(params, '', textentry('40-506-00007', args=[out_dir]))
        os.system('rm -rf {0}/*'.format(out_dir))
        # ------------------------------------------------------------------
        if 'html' in mode:
            # copy all files from the html folder
            # Copying html files
            WLOG(params, '', textentry('40-506-00008'))
            os.system('rm -rf {0}/*'.format(out_dir))
            # copy
            drs_path.copytree(html_dir, out_dir)
        # ------------------------------------------------------------------
        if 'latex' in mode:
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


def upload(params: ParamDict):
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


def _compile_recipe(params: ParamDict, pconst: PseudoConst, instrument: str,
                    recipe: DrsRecipe) -> Dict[str, Any]:
    """
    Compile recipe

    :param params: ParamDict, parameter dictionary of constants
    :param pconst: Pseudo Constant instance, the pseudo consts instances for
                   this instrument
    :param recipe: DrsRecipe instance, the recipe that we are compiling

    :return: dictionary, Recipe summary dictionary
    """
    # get summary information
    summary = recipe.summary(params)
    # get table for outputs
    table = _compile_files(params, pconst, summary['OUTPUTS'])
    # remove empty columns
    table = _remove_empty_cols(table)
    # get directory to save file to
    recipe_def_dir = RECIPE_DEF_DIR.format(instrument.lower())
    def_dir = drs_misc.get_relative_folder(__PACKAGE__, recipe_def_dir)
    # construct filename
    fargs = [instrument.lower(), summary['SHORTNAME'].lower()]
    basename = '{0}_rout_{1}_.csv'
    filename = basename.format(*fargs)
    abs_filename = os.path.join(def_dir, filename)
    # print progress
    margs = [summary['NAME'], filename]
    WLOG(params, '', 'Saving {0} csv to: {1}'.format(*margs))
    # save outtable to file
    table.write(abs_filename, format='csv', overwrite=True)
    # save table filename to out table
    summary['OUTTABLE'] = filename
    # return the summary dictionary
    return summary


def _compile_sequence(params: ParamDict, instrument: str,
                      sequence: DrsRunSequence) -> Dict[str, Any]:
    """
    Compile sequence

    :param params: ParamDict, parameter dictionary of constants
    :param sequence: DrsRunSequence instance, the sequence for which we are
                     compiling

    :return: dictionary, Sequence summary dictionary
    """
    # store parameters in dictionary
    summary = dict()
    # get sequence name
    summary['NAME'] = sequence.name
    # get summary information
    stable = sequence.summary_table()
    # remove empty columns
    stable = _remove_empty_cols(stable)
    # get directory to save file to
    sequence_def_dir = SEQUENCE_DEF_DIR.format(instrument.lower())
    def_dir = drs_misc.get_relative_folder(__PACKAGE__, sequence_def_dir)
    # construct table filename
    fargs = [instrument.lower(), summary['NAME'].lower()]
    basename = '{0}_sequence_{1}.csv'
    filename = basename.format(*fargs)
    abs_filename = os.path.join(def_dir, filename)
    # print progress
    margs = [summary['NAME'], filename]
    WLOG(params, '', 'Saving {0} csv to: {1}'.format(*margs))
    # save outtable to file
    stable.write(abs_filename, format='csv', overwrite=True)
    # save table filename to out table
    summary['OUTTABLE'] = filename
    # return the summary dictionary
    return summary


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
