#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI documentation generator.

Builds the markdown documentation tree consumed by apero-ri from the APERO
recipe/file definitions:

    documentation/ari/{docversion}/home/docs/apero/
        index.md
        user_tools/{shortname}.md
        dev_tools/{shortname}.md
        instruments/{instrument}/sequences/{sequence}.md
        instruments/{instrument}/recipes/{shortname}.md
        instruments/{instrument}/tools/{shortname}.md
        instruments/{instrument}/file_definitions/{filetype}.md

Narrative text (including any hand-written mermaid flow diagram) is NOT
generated - it is read verbatim from:

    documentation/descriptions/{instrument}/{kind}/{name}.md

so that re-running the generator never destroys hand-written prose.

Created on 2026-09-29

@author: cook
"""
import ast
import os
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import yaml
from astropy.table import Table

from aperocore.constants import load_functions
from aperocore.constants import param_functions
from aperocore.core import drs_log
from aperocore.core import drs_text
from apero.base import base as apero_base
from apero.core import drs_file
from apero.instruments import select
from apero.instruments.default import instrument as instrument_mod
from apero.utils import drs_recipe

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.tools.module.documentation.ari_docs.py'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# Get Logging function
WLOG = drs_log.wlog
# get drs classes
ParamDict = param_functions.ParamDict
Instrument = instrument_mod.Instrument
DrsRecipe = drs_recipe.DrsRecipe
DrsRunSequence = drs_recipe.DrsRunSequence
DrsInputFile = drs_file.DrsInputFile
# -----------------------------------------------------------------------------
# repo root is five levels above this file
#   apero-drs/apero/tools/module/documentation/ari_docs.py
REPO_ROOT = Path(__file__).resolve().parents[5]
# the hand-written description fragments live here
DESC_ROOT = REPO_ROOT / 'documentation' / 'descriptions'
# the apero-ri documentation tree lives here
ARI_ROOT = REPO_ROOT / 'documentation' / 'ari'
# every generated page sits under this ref inside a version directory
DOCS_PREFIX = os.path.join('home', 'docs')
# the sub-tree owned by this generator (wiped and rebuilt on each run)
APERO_REF = 'apero'
# -----------------------------------------------------------------------------
# description kinds (sub-directory of documentation/descriptions/{instrument})
KIND_RECIPES = 'recipes'
KIND_USER_TOOLS = 'user_tools'
KIND_DEV_TOOLS = 'dev_tools'
KIND_SEQUENCES = 'sequences'
KIND_FILES = 'files'
DESC_KINDS = [KIND_RECIPES, KIND_USER_TOOLS, KIND_DEV_TOOLS, KIND_SEQUENCES,
              KIND_FILES]
# -----------------------------------------------------------------------------
# FontAwesome icons per page kind
ICONS = dict()
ICONS[APERO_REF] = 'fa-solid fa-microscope'
ICONS['instruments'] = 'fa-solid fa-satellite-dish'
ICONS[KIND_RECIPES] = 'fa-solid fa-flask'
ICONS[KIND_USER_TOOLS] = 'fa-solid fa-screwdriver-wrench'
ICONS[KIND_DEV_TOOLS] = 'fa-solid fa-code'
ICONS[KIND_SEQUENCES] = 'fa-solid fa-diagram-project'
ICONS[KIND_FILES] = 'fa-solid fa-file-lines'
ICONS['page'] = 'fa-solid fa-file-lines'
# -----------------------------------------------------------------------------
# file definition sections: (filetype attribute, page name, page label)
FILE_SECTIONS = [('raw_file', 'raw', 'Raw files'),
                 ('pp_file', 'preprocessed', 'Pre-processed files'),
                 ('red_file', 'reduced', 'Reduced files'),
                 ('calib_file', 'calibration', 'Calibration files'),
                 ('tellu_file', 'telluric', 'Telluric files'),
                 ('post_file', 'post_processed', 'Post-processed files')]
# columns removed from the file definition tables (never useful to a reader)
FILE_REMOVE_COLS = dict()
FILE_REMOVE_COLS['raw_file'] = ['file type']
FILE_REMOVE_COLS['red_file'] = ['dbname', 'dbkey']
# -----------------------------------------------------------------------------
# the description file front matter key holding related algorithm page refs
DESC_ALGO_KEY = 'algorithms'
# the description file front matter key holding literature references
DESC_REF_KEY = 'references'
# short summaries for command scripts without recipe-definition metadata
UNREGISTERED_TOOL_SUMMARIES = dict()
UNREGISTERED_TOOL_SUMMARIES['apero_database_kill'] = (
    'Stops APERO database process entries that exceed the configured '
    '60-minute timeout.')
UNREGISTERED_TOOL_SUMMARIES['apero_assets'] = (
    'Checks, updates, and synchronizes APERO data-asset checksums.')
UNREGISTERED_TOOL_SUMMARIES['apero_constants'] = (
    'Generates or cleans constant modules and creates the constants glossary.')
UNREGISTERED_TOOL_SUMMARIES['apero_optimize'] = (
    'Checks Python source files for missing docstrings and unused functions.')


# =============================================================================
# Define markdown helper functions
# =============================================================================
def default_docversion() -> str:
    """
    Build the documentation version directory for the running APERO version.

    Documentation is versioned by major release only (e.g. ``0.8.XXX``);
    differences between sub-versions are handled by hand.

    :return: str, the documentation version directory name
    """
    parts = str(__version__).split('.')
    # fall back to the raw version if it is not the expected X.Y.Z form
    if len(parts) < 2:
        return str(__version__)
    return '{0}.{1}.XXX'.format(parts[0], parts[1])


def md_escape_cell(value: Any) -> str:
    """
    Make a value safe to place inside a markdown table cell.

    :param value: Any, the raw cell value

    :return: str, the cell text with pipes/newlines neutralised
    """
    text = str(value)
    # a literal pipe would end the table cell
    text = text.replace('|', r'\|')
    # newlines would end the table row
    text = text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    return text.strip()


def md_table(table: Table) -> List[str]:
    """
    Convert an astropy table into GitHub-flavoured markdown table lines.

    :param table: astropy.table.Table, the table to convert

    :return: list of str, the markdown lines (empty if the table is empty)
    """
    # nothing to render for an empty table
    if table is None or len(table.colnames) == 0 or len(table) == 0:
        return []
    colnames = list(table.colnames)
    lines = ['| ' + ' | '.join(colnames) + ' |']
    lines += ['| ' + ' | '.join(['---'] * len(colnames)) + ' |']
    # one markdown row per table row
    for row in table:
        cells = [md_escape_cell(row[colname]) for colname in colnames]
        lines += ['| ' + ' | '.join(cells) + ' |']
    return lines


def md_kv_table(rows: List[Tuple[str, str]],
                headers: Tuple[str, str]) -> List[str]:
    """
    Build a simple two-column markdown table.

    :param rows: list of (key, value) tuples to render
    :param headers: tuple of two str, the column headers

    :return: list of str, the markdown lines (empty if there are no rows)
    """
    if len(rows) == 0:
        return []
    lines = ['| {0} | {1} |'.format(*headers), '| --- | --- |']
    for key, value in rows:
        lines += ['| `{0}` | {1} |'.format(md_escape_cell(key),
                                           md_escape_cell(value))]
    return lines


def split_arg_lines(arglines: List[str]) -> List[Tuple[str, str]]:
    """
    Split ``drs_usage`` argument lines of the form "name // help" into pairs.

    :param arglines: list of str, the raw "{arg} // {help}" lines

    :return: list of (arg, help) tuples
    """
    rows = []
    for argline in arglines:
        if '//' in argline:
            name, _, helpstr = argline.partition('//')
        else:
            name, helpstr = argline, ''
        rows.append((name.strip(), helpstr.strip()))
    return rows


def front_matter(label: str, icon: str) -> List[str]:
    """
    Build the YAML front matter block used by the apero-ri docs renderer.

    :param label: str, the card label shown in the docs index/sidebar
    :param icon: str, the FontAwesome icon class

    :return: list of str, the front matter lines
    """
    return ['---', 'card_label: {0}'.format(label),
            'card_icon: {0}'.format(icon), '---', '']


def write_page(path: Path, label: str, icon: str, lines: List[str]):
    """
    Write a markdown documentation page (front matter + body).

    :param path: Path, the absolute markdown file path to write
    :param label: str, the card label for this page
    :param icon: str, the FontAwesome icon class for this page
    :param lines: list of str, the markdown body lines

    :return: None, writes to "path"
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    page_lines = front_matter(label, icon) + lines
    content = '\n'.join(line.rstrip() for line in page_lines).rstrip() + '\n'
    path.write_text(content, encoding='utf-8')


def card_list(items: List[Tuple[str, str]]) -> List[str]:
    """
    Build a markdown bullet list of links used on index pages.

    :param items: list of (link target, display label) tuples

    :return: list of str, the markdown lines
    """
    lines = []
    for target, label in items:
        lines += ['- [{0}]({1})'.format(label, target)]
    lines += ['']
    return lines


# =============================================================================
# Define description-file functions
# =============================================================================
def description_path(instrument: str, kind: str, name: str) -> Path:
    """
    Build the path of a hand-written description fragment.

    :param instrument: str, the instrument name (or "default")
    :param kind: str, one of DESC_KINDS
    :param name: str, the fragment name (no extension)

    :return: Path, the absolute path to the description markdown file
    """
    return DESC_ROOT / instrument.lower() / kind / '{0}.md'.format(name)


def read_description(instrument: str, kind: str,
                     name: str) -> Tuple[dict, str]:
    """
    Read a hand-written description fragment, falling back to "default".

    :param instrument: str, the instrument name (or "default")
    :param kind: str, one of DESC_KINDS
    :param name: str, the fragment name (no extension)

    :return: tuple, 1. the front matter dict, 2. the markdown body
    """
    # look in the instrument directory first, then the shared default one
    candidates = [description_path(instrument, kind, name)]
    if instrument.lower() != 'default':
        candidates += [description_path('default', kind, name)]
    # use the first fragment that exists
    for candidate in candidates:
        if candidate.exists():
            return split_front_matter(candidate.read_text(encoding='utf-8'))
    return dict(), ''


def split_front_matter(text: str) -> Tuple[dict, str]:
    """
    Split an optional YAML front matter block from a markdown body.

    :param text: str, the full markdown file contents

    :return: tuple, 1. the front matter dict, 2. the markdown body
    """
    content = str(text or '')
    if not content.startswith('---'):
        return dict(), content
    match = re.match(r'^---\s*\r?\n(.*?)\r?\n---\s*\r?\n?', content,
                     flags=re.DOTALL)
    if match is None:
        return dict(), content
    meta = yaml.safe_load(match.group(1))
    if not isinstance(meta, dict):
        meta = dict()
    return meta, content[match.end():]


def ensure_description_stub(instrument: str, kind: str, name: str,
                            title: str, fallback: str):
    """
    Create an empty description fragment so authors have somewhere to write.

    Existing fragments are never touched.

    :param instrument: str, the instrument name (or "default")
    :param kind: str, one of DESC_KINDS
    :param name: str, the fragment name (no extension)
    :param title: str, the human readable name used in the stub text
    :param fallback: str, the short description from the definition file

    :return: None, writes a stub markdown file if none exists
    """
    path = description_path(instrument, kind, name)
    # never overwrite hand-written prose
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ['---', '# Related algorithm pages (docs refs under algorithms/)',
             '{0}: []'.format(DESC_ALGO_KEY),
             '# Literature references rendered at the bottom of the page',
             '{0}: []'.format(DESC_REF_KEY), '---', '']
    # seed the body with whatever short description the definition provides
    if len(fallback.strip()) > 0:
        lines += [fallback.strip(), '']
    else:
        lines += ['!!! warning "Undocumented"', '',
                  '    No description has been written for `{0}` '
                  'yet.'.format(title), '']
    lines += ['## Flow', '',
              '<!-- Replace the diagram below with the real steps. -->', '',
              '```mermaid', 'flowchart TD',
              '    A[Inputs] --> B[TODO: describe the steps]',
              '    B --> C[Outputs]', '```', '']
    path.write_text('\n'.join(lines), encoding='utf-8')


# =============================================================================
# Define table-building functions
# =============================================================================
def compile_file_table(params: ParamDict, pconst: Instrument,
                       fileset: List[DrsInputFile],
                       remove_cols: Optional[List[str]] = None) -> Table:
    """
    Build a table of file-definition properties, one row per file definition.

    :param params: ParamDict, parameter dictionary of constants
    :param pconst: Instrument, the pseudo constants for this instrument
    :param fileset: list of DrsInputFile, the file definitions to tabulate
    :param remove_cols: list of str or None, columns to drop from the table

    :return: astropy.table.Table, one row per file definition
    """
    storage: Dict[str, list] = dict()
    # each file definition knows how to summarise itself
    for filedef in fileset:
        filedict = filedef.summary(params, pconst)
        for key in filedict:
            storage.setdefault(key, []).append(filedict[key])
    table = Table()
    for key in storage:
        table[key] = storage[key]
    table = remove_empty_cols(table)
    # drop the columns that are noise for a human reader
    for col in list(remove_cols or []):
        if col in table.colnames:
            del table[col]
    return table


def remove_empty_cols(table: Table) -> Table:
    """
    Remove columns whose values are all null-like.

    :param table: astropy.table.Table, the input table

    :return: astropy.table.Table, the table without empty columns
    """
    newtable = Table()
    nulls = ['None', '--', '', 'Null']
    for col in table.colnames:
        uvalues = np.unique(np.array(table[col]))
        # a column is empty only when every unique value is null-like
        empty = True
        for uvalue in uvalues:
            if not drs_text.null_text(uvalue, nulls):
                empty = False
        if not empty:
            newtable[col] = np.array(table[col])
    return newtable


# =============================================================================
# Define page-building functions
# =============================================================================
def build_recipe_page(params: ParamDict, pconst: Instrument,
                      srecipe: DrsRecipe, instrument: str, kind: str,
                      outdir: Path):
    """
    Write one markdown page describing a single recipe or tool.

    :param params: ParamDict, parameter dictionary of constants
    :param pconst: Instrument, the pseudo constants for this instrument
    :param srecipe: DrsRecipe, the recipe/tool being documented
    :param instrument: str, the instrument name (or "default")
    :param kind: str, one of KIND_RECIPES/KIND_USER_TOOLS/KIND_DEV_TOOLS
    :param outdir: Path, the directory to write the markdown page into

    :return: None, writes a markdown page
    """
    summary = srecipe.summary(params)
    name = str(summary['NAME']).replace('.py', '')
    shortname = str(summary['SHORTNAME'])
    fallback = str(srecipe.description or '')
    if instrument.lower() in ['nirps_ha', 'nirps_he']:
        fallback = fallback.replace('SPIRou @ CFHT',
                                    instrument.replace('_', ' ').upper())
    # make sure an editable description fragment exists for this recipe
    ensure_description_stub(instrument, kind, name, name,
                            fallback)
    meta, body = read_description(instrument, kind, name)
    # -------------------------------------------------------------------------
    # Header: identity of the recipe at a glance
    # -------------------------------------------------------------------------
    lines = ['# {0}'.format(name), '']
    ident = [('Short name', shortname), ('Type', summary['RECIPE_TYPE']),
             ('Kind', summary['RECIPE_KIND']), ('Instrument', instrument)]
    lines += ['  '.join(['**{0}:** {1}'.format(*item) for item in ident]), '']
    # -------------------------------------------------------------------------
    # Description: hand-written prose and mermaid flow diagram, verbatim
    # -------------------------------------------------------------------------
    lines += [body.strip(), '']
    # -------------------------------------------------------------------------
    # Usage: the command line as the user would type it
    # -------------------------------------------------------------------------
    lines += ['## Usage', '', '```bash', str(summary['USAGE']), '```', '']
    # -------------------------------------------------------------------------
    # Arguments: positional first, then optional, then the shared special set
    # -------------------------------------------------------------------------
    pos_rows = split_arg_lines(summary['LPOS'])
    if len(pos_rows) > 0:
        lines += ['## Positional arguments', '']
        lines += md_kv_table(pos_rows, ('Argument', 'Description')) + ['']
    opt_rows = split_arg_lines(summary['LOPT'])
    if len(opt_rows) > 0:
        lines += ['## Optional arguments', '']
        lines += md_kv_table(opt_rows, ('Argument', 'Description')) + ['']
    sopt_rows = split_arg_lines(summary['LSOPT'])
    if len(sopt_rows) > 0:
        # special arguments are identical everywhere so keep them collapsed
        lines += ['## Special arguments', '', '<details>',
                  '<summary>Arguments common to all APERO recipes</summary>',
                  '']
        lines += md_kv_table(sopt_rows, ('Argument', 'Description'))
        lines += ['', '</details>', '']
    # -------------------------------------------------------------------------
    # Outputs: where files go and what they are
    # -------------------------------------------------------------------------
    lines += ['## Outputs', '', '**Output directory:** `{0}`'
              ''.format(summary['OUTDIR']), '']
    outtable = compile_file_table(params, pconst, summary['OUTPUTS'])
    outlines = md_table(outtable)
    if len(outlines) > 0:
        lines += outlines + ['']
    else:
        lines += ['This recipe produces no registered output files.', '']
    # -------------------------------------------------------------------------
    # Plots: the debug/summary plots this recipe can produce
    # -------------------------------------------------------------------------
    lines += plot_section(summary)
    # -------------------------------------------------------------------------
    # Cross links: algorithms and literature declared in the description
    # -------------------------------------------------------------------------
    lines += link_section(meta)
    write_page(outdir / '{0}.md'.format(shortname.lower()), name,
               ICONS.get(kind, ICONS['page']), lines)


def plot_section(summary: Dict[str, Any]) -> List[str]:
    """
    Build the debug/summary plot section of a recipe page.

    :param summary: dict, the ``DrsRecipe.summary`` output

    :return: list of str, the markdown lines (empty if there are no plots)
    """
    debug_plots = list(summary['DEBUG_PLOTS'])
    summary_plots = list(summary['SUMMARY_PLOTS'])
    if len(debug_plots) == 0 and len(summary_plots) == 0:
        return []
    lines = ['## Plots', '']
    if len(debug_plots) > 0:
        lines += ['**Debug plots:** ']
        lines += [', '.join(['`{0}`'.format(p) for p in debug_plots]), '']
    if len(summary_plots) > 0:
        lines += ['**Summary plots:** ']
        lines += [', '.join(['`{0}`'.format(p) for p in summary_plots]), '']
    return lines


def link_section(meta: dict) -> List[str]:
    """
    Build the "see also" / "references" section from description front matter.

    :param meta: dict, the description fragment front matter

    :return: list of str, the markdown lines (empty if nothing is declared)
    """
    lines = []
    algorithms = list(meta.get(DESC_ALGO_KEY) or [])
    if len(algorithms) > 0:
        lines += ['## Algorithms used', '']
        for algorithm in algorithms:
            # algorithms are page refs under the hand-written algorithms tree
            lines += ['- [{0}](/docs/algorithms/{1})'
                      ''.format(str(algorithm).replace('_', ' '), algorithm)]
        lines += ['']
    references = list(meta.get(DESC_REF_KEY) or [])
    if len(references) > 0:
        lines += ['## References', '']
        for reference in references:
            lines += ['- {0}'.format(reference)]
        lines += ['']
    return lines


def build_sequence_page(params: ParamDict, sequence: DrsRunSequence,
                        instrument: str, outdir: Path):
    """
    Write one markdown page describing a single recipe sequence.

    :param params: ParamDict, parameter dictionary of constants
    :param sequence: DrsRunSequence, the sequence being documented
    :param instrument: str, the instrument name
    :param outdir: Path, the directory to write the markdown page into

    :return: None, writes a markdown page
    """
    name = str(sequence.name)
    ensure_description_stub(instrument, KIND_SEQUENCES, name, name, '')
    meta, body = read_description(instrument, KIND_SEQUENCES, name)
    lines = ['# {0}'.format(name), '',
             '**Instrument:** {0}'.format(instrument), '', body.strip(), '',
             '## Recipes in this sequence', '']
    # the sequence knows the ordered list of recipes it runs
    stable = remove_empty_cols(sequence.summary_table())
    seqlines = md_table(stable)
    if len(seqlines) > 0:
        lines += seqlines + ['']
    else:
        lines += ['This sequence contains no recipes.', '']
    lines += link_section(meta)
    write_page(outdir / '{0}.md'.format(name.lower()), name,
               ICONS[KIND_SEQUENCES], lines)


def build_file_definition_pages(params: ParamDict, pconst: Instrument,
                                filemod: Any, instrument: str,
                                outdir: Path) -> List[Tuple[str, str]]:
    """
    Write one markdown page per file-definition category for an instrument.

    :param params: ParamDict, parameter dictionary of constants
    :param pconst: Instrument, the pseudo constants for this instrument
    :param filemod: module, the instrument ``file_definitions`` module
    :param instrument: str, the instrument name
    :param outdir: Path, the directory to write the markdown pages into

    :return: list of (page name, page label) tuples that were written
    """
    written = []
    for filetype, pagename, pagelabel in FILE_SECTIONS:
        # some instruments do not define every file category
        if not hasattr(filemod, filetype):
            continue
        fileset = getattr(filemod, filetype).fileset
        if len(fileset) == 0:
            continue
        table = compile_file_table(params, pconst, fileset,
                                   FILE_REMOVE_COLS.get(filetype))
        ensure_description_stub(instrument, KIND_FILES, pagename, pagelabel,
                                '')
        meta, body = read_description(instrument, KIND_FILES, pagename)
        lines = ['# {0} ({1})'.format(pagelabel, instrument), '']
        if len(body.strip()) > 0:
            lines += [body.strip(), '']
        lines += ['`HDR[XXX]` denotes a key read from the file header.', '']
        lines += md_table(table) + ['']
        lines += link_section(meta)
        write_page(outdir / '{0}.md'.format(pagename), pagelabel,
                   ICONS[KIND_FILES], lines)
        written.append((pagename, pagelabel))
    return written


def build_index(outdir: Path, label: str, icon: str, title: str,
                intro: List[str], items: List[Tuple[str, str]]):
    """
    Write an ``index.md`` giving a directory its card label and contents list.

    :param outdir: Path, the directory the index describes
    :param label: str, the card label for the directory
    :param icon: str, the FontAwesome icon class for the directory
    :param title: str, the page title
    :param intro: list of str, introductory markdown lines
    :param items: list of (link target, display label) tuples

    :return: None, writes ``index.md`` into "outdir"
    """
    lines = ['# {0}'.format(title), ''] + intro + ['']
    if len(items) > 0:
        lines += card_list(items)
    else:
        lines += ['Nothing is currently documented here.', '']
    write_page(outdir / 'index.md', label, icon, lines)


# =============================================================================
# Define main compile functions
# =============================================================================
def reload_for(recipe: DrsRecipe, instrument: str) -> ParamDict:
    """
    Point the running recipe at another instrument's definition modules.

    :param recipe: DrsRecipe, the running recipe
    :param instrument: str, the instrument name (or "default")

    :return: ParamDict, the parameter dictionary for "instrument"
    """
    iparams = load_functions.load_config(select.INSTRUMENTS,
                                         instrument=instrument)
    # load_config sets the default instrument to None - put it back
    if instrument.lower() == 'default':
        iparams.set('OBS.INSTRUMENT', instrument)
    # reload() rebuilds filemod/recipemod from params, so set it there too
    recipe.params.set('OBS.INSTRUMENT', instrument)
    recipe.reload(instrument)
    return iparams


def as_module(modref: Any) -> Any:
    """
    Resolve a recipe's ``filemod``/``recipemod`` to an imported module.

    Depending on how the recipe was built these are either an
    ``ImportModule`` wrapper or the already-imported module itself.

    :param modref: Any, the module or ImportModule wrapper

    :return: Any, the imported module
    """
    if hasattr(modref, 'get'):
        return modref.get()
    return modref


def filter_recipes(srecipes: List[DrsRecipe], kind: str) -> List[DrsRecipe]:
    """
    Split the recipe definitions into recipes, user tools and dev tools.

    :param srecipes: list of DrsRecipe, every recipe defined for an instrument
    :param kind: str, one of KIND_RECIPES/KIND_USER_TOOLS/KIND_DEV_TOOLS

    :return: list of DrsRecipe matching "kind"
    """
    tool_types = ['tool', 'nolog-tool']
    output = []
    for srecipe in srecipes:
        if kind == KIND_RECIPES:
            match = srecipe.recipe_type == 'recipe'
        elif kind == KIND_USER_TOOLS:
            match = (srecipe.recipe_type in tool_types
                     and srecipe.recipe_kind in ['user', 'processing'])
        else:
            match = (srecipe.recipe_type in tool_types
                     and srecipe.recipe_kind in ['admin'])
        if match:
            output.append(srecipe)
    # keep pages in a predictable order between runs
    return sorted(output, key=lambda item: str(item.name))


def compile_instrument(params: ParamDict, recipe: DrsRecipe, instrument: str,
                       apero_dir: Path) -> List[Tuple[str, str]]:
    """
    Generate every page belonging to a single instrument.

    :param params: ParamDict, parameter dictionary of constants for the
                   instrument being documented
    :param recipe: DrsRecipe, the running recipe (provides the definition
                   modules, already reloaded for "instrument")
    :param instrument: str, the instrument name
    :param apero_dir: Path, the root of the generated apero docs tree

    :return: list of (link target, display label) tuples for the parent index
    """
    pconst = load_functions.load_pconfig(select.INSTRUMENTS,
                                         instrument=instrument)
    recipemod = as_module(recipe.recipemod)
    srecipes = list(getattr(recipemod, 'recipes', []))
    inst_dir = apero_dir / 'instruments' / instrument.lower()
    sections = []
    # -------------------------------------------------------------------------
    # Sequences: how a whole night is reduced
    # -------------------------------------------------------------------------
    sequences = list(getattr(recipemod, 'sequences', []))
    if len(sequences) > 0:
        seq_dir = inst_dir / KIND_SEQUENCES
        items = []
        for sequence in sequences:
            WLOG(params, '', '\tSequence: {0}'.format(sequence.name))
            build_sequence_page(params, sequence, instrument, seq_dir)
            items.append((sequence.name.lower(), sequence.name))
        intro = ['A sequence is an ordered set of recipes run together by '
                 '`apero_processing.py`. Use these pages to see what APERO '
                 'actually does to your data, and in what order.']
        build_index(seq_dir, 'Sequences', ICONS[KIND_SEQUENCES],
                    'Sequences ({0})'.format(instrument), intro, items)
        sections.append((KIND_SEQUENCES + '/', 'Sequences'))
    # -------------------------------------------------------------------------
    # Recipes and instrument tools: the individual processing steps
    # -------------------------------------------------------------------------
    recipe_kinds = [(KIND_RECIPES, 'Recipes',
                     'Each recipe is one processing step. The flow diagram '
                     'on each page shows what the recipe does; the tables '
                     'show how to run it and what it produces.'),
                    (KIND_USER_TOOLS, 'Instrument tools',
                     'Tools specific to this instrument.')]
    for kind, label, blurb in recipe_kinds:
        selected = filter_recipes(srecipes, kind)
        if len(selected) == 0:
            continue
        kind_dir = inst_dir / kind
        items = []
        for srecipe in selected:
            WLOG(params, '', '\t{0}: {1}'.format(label, srecipe.name))
            build_recipe_page(params, pconst, srecipe, instrument, kind,
                              kind_dir)
            items.append((srecipe.shortname.lower(),
                          str(srecipe.name).replace('.py', '')))
        build_index(kind_dir, label, ICONS[kind],
                    '{0} ({1})'.format(label, instrument), [blurb], items)
        sections.append((kind + '/', label))
    # -------------------------------------------------------------------------
    # File definitions: what every APERO file is and how it is identified
    # -------------------------------------------------------------------------
    filemod = as_module(recipe.filemod)
    file_dir = inst_dir / 'file_definitions'
    written = build_file_definition_pages(params, pconst, filemod, instrument,
                                          file_dir)
    if len(written) > 0:
        intro = ['Every file APERO reads or writes is declared as a file '
                 'definition. These tables give the file name pattern and '
                 'the header keys used to identify each one.']
        build_index(file_dir, 'File definitions', ICONS[KIND_FILES],
                    'File definitions ({0})'.format(instrument), intro,
                    written)
        sections.append(('file_definitions/', 'File definitions'))
    # -------------------------------------------------------------------------
    # Instrument index tying the above together
    # -------------------------------------------------------------------------
    intro = ['Documentation for the APERO {0} reduction.'.format(instrument)]
    build_index(inst_dir, instrument, ICONS['instruments'], instrument, intro,
                sections)
    return sections


def compile_global_tools(params: ParamDict, recipe: DrsRecipe,
                         apero_dir: Path):
    """
    Generate the instrument-independent user and developer tool pages.

    :param params: ParamDict, parameter dictionary of constants (default
                   instrument)
    :param recipe: DrsRecipe, the running recipe (already reloaded for the
                   default instrument)
    :param apero_dir: Path, the root of the generated apero docs tree

    :return: None, writes markdown pages
    """
    pconst = load_functions.load_pconfig(select.INSTRUMENTS,
                                         instrument='default')
    recipemod = as_module(recipe.recipemod)
    srecipes = list(getattr(recipemod, 'recipes', []))
    tool_kinds = [(KIND_USER_TOOLS, 'User tools',
                   'Tools you run yourself to set up, inspect, query and '
                   'manage an APERO reduction.'),
                  (KIND_DEV_TOOLS, 'Developer tools',
                   'Tools used to maintain APERO itself. Most users will '
                   'never need these.')]
    for kind, label, blurb in tool_kinds:
        selected = filter_recipes(srecipes, kind)
        if len(selected) == 0:
            continue
        kind_dir = apero_dir / kind
        items = []
        for srecipe in selected:
            WLOG(params, '', '\t{0}: {1}'.format(label, srecipe.name))
            build_recipe_page(params, pconst, srecipe, 'default', kind,
                              kind_dir)
            items.append((srecipe.shortname.lower(),
                          str(srecipe.name).replace('.py', '')))
        source_kind = 'bin' if kind == KIND_USER_TOOLS else 'dev'
        source_dir = (REPO_ROOT / 'apero-drs' / 'apero' / 'tools' /
                      'recipes' / source_kind)
        known_names = {Path(str(item.name)).stem for item in selected}
        build_unregistered_tool_pages(kind_dir, kind, source_dir,
                                      source_kind, known_names, items)
        build_index(kind_dir, label, ICONS[kind], label, [blurb], items)


def build_unregistered_tool_pages(outdir: Path, kind: str,
                                  source_dir: Path, source_kind: str,
                                  known_names: set,
                                  items: List[Tuple[str, str]]):
    """
    Add command scripts that have no DrsRecipe definition to the tool index.

    :param outdir: Path, output directory for user or developer tool pages
    :param kind: str, KIND_USER_TOOLS or KIND_DEV_TOOLS
    :param source_dir: Path, directory containing tool Python modules
    :param source_kind: str, ``bin`` or ``dev`` source directory name
    :param known_names: set of str, script stems already documented from defs
    :param items: list of (link target, label) pairs (modified in place)

    :return: None, writes pages and appends their index entries
    """
    if not source_dir.is_dir():
        return
    icon = ICONS[kind]
    for source in sorted(source_dir.glob('*.py')):
        if source.stem in known_names or source.stem.startswith('_'):
            continue
        module_doc = ast.get_docstring(ast.parse(
            source.read_text(encoding='utf-8')))
        description = UNREGISTERED_TOOL_SUMMARIES.get(source.stem)
        if not description and module_doc:
            description = module_doc.strip()
        if not description or 'CODE DESCRIPTION HERE' in description:
            description = ('This script has no DrsRecipe metadata yet. '
                           'See the source module for its current behavior.')
        source_ref = 'apero-drs/apero/tools/recipes/{0}/{1}'
        source_ref = source_ref.format(source_kind, source.name)
        lines = ['# {0}'.format(source.stem), '', description, '',
                 '**Source:** `{0}`'.format(source_ref), '',
                 'This script is catalogued from its source file because it '
                 'does not have a `DrsRecipe` entry. Add recipe metadata '
                 'when it needs generated usage, argument, or output tables.']
        write_page(outdir / '{0}.md'.format(source.stem), source.stem,
                   icon, lines)
        items.append((source.stem, source.stem))


def compile_ari_docs(params: ParamDict, recipe: DrsRecipe,
                     instruments: List[str], docversion: str):
    """
    Generate the whole ``apero`` documentation sub-tree for apero-ri.

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, the running recipe (provides definition modules)
    :param instruments: list of str, the instrument names to document
    :param docversion: str, the documentation version directory to write into

    :return: None, writes the markdown documentation tree
    """
    docversion = str(docversion).strip()
    if re.fullmatch(r'\d+\.\d+\.(?:XXX|\d+)', docversion) is None:
        raise ValueError('Invalid APERO documentation version: {0}'
                         ''.format(docversion))
    # A version selector must never label pages generated from another release.
    running_major = '.'.join(default_docversion().split('.')[:2])
    target_major = '.'.join(docversion.split('.')[:2])
    if target_major != running_major:
        raise ValueError('Cannot generate {0} documentation from APERO {1}'
                         ''.format(docversion, __version__))
    version_dir = ARI_ROOT / docversion / DOCS_PREFIX
    apero_dir = version_dir / APERO_REF
    # the generated sub-tree is disposable - rebuild it from scratch so that
    # renamed/removed recipes do not leave orphan pages behind
    if apero_dir.exists():
        shutil.rmtree(apero_dir)
    apero_dir.mkdir(parents=True, exist_ok=True)
    # -------------------------------------------------------------------------
    # Instrument-independent tools
    # -------------------------------------------------------------------------
    WLOG(params, 'info', 'Compiling APERO tool documentation')
    iparams = reload_for(recipe, 'default')
    compile_global_tools(iparams, recipe, apero_dir)
    # -------------------------------------------------------------------------
    # Per instrument pages
    # -------------------------------------------------------------------------
    inst_items = []
    for instrument in instruments:
        # "None"/"default" is the pseudo instrument handled above
        if instrument.upper() in ['NONE', 'DEFAULT']:
            continue
        WLOG(params, 'info', 'Compiling {0} documentation'.format(instrument))
        iparams = reload_for(recipe, instrument)
        compile_instrument(iparams, recipe, instrument, apero_dir)
        inst_items.append((instrument.lower() + '/', instrument))
    if len(inst_items) > 0:
        intro = ['Select an instrument to see its sequences, recipes, tools '
                 'and file definitions.']
        build_index(apero_dir / 'instruments', 'Instruments',
                    ICONS['instruments'], 'Instruments', intro, inst_items)
    # -------------------------------------------------------------------------
    # Top level index for the generated tree
    # -------------------------------------------------------------------------
    items = [('user_tools/', 'User tools'), ('dev_tools/', 'Developer tools'),
             ('instruments/', 'Instruments')]
    intro = ['Reference documentation for APERO {0}, generated from the '
             'recipe and file definitions.'.format(docversion)]
    build_index(apero_dir, 'APERO', ICONS[APERO_REF], 'APERO', intro, items)
    WLOG(params, '', 'Wrote APERO docs to: {0}'.format(apero_dir))


# =============================================================================
# Define migration functions
# =============================================================================
def rst_to_markdown(text: str) -> str:
    """
    Convert the small subset of rst used in APERO descriptions to markdown.

    This only has to handle the constructs actually present in the legacy
    ``documentation/working/resources`` fragments; anything unrecognised is
    passed through unchanged for a human to fix.

    :param text: str, the rst source

    :return: str, the markdown equivalent
    """
    lines = str(text or '').split('\n')
    output: List[str] = []
    index = 0
    # rst underline characters in the order APERO uses them for nesting
    underlines = ['=', '-', '^', '~', '"', '+']
    while index < len(lines):
        line = lines[index]
        nextline = lines[index + 1] if index + 1 < len(lines) else ''
        stripped = nextline.strip()
        # an overline is a punctuation rule directly above a title
        if _is_rule(line, underlines) and index + 2 < len(lines):
            if _is_rule(lines[index + 2], underlines):
                output.append('{0} {1}'.format(
                    '#' * (underlines.index(line.strip()[0]) + 2),
                    nextline.strip()))
                index += 3
                continue
            # a lone rule with no matching underline carries no meaning
            index += 1
            continue
        # a section title is a line followed by a line of repeated punctuation
        is_title = len(line.strip()) > 0 and _is_rule(nextline, underlines)
        if is_title:
            level = underlines.index(stripped[0]) + 2
            output.append('{0} {1}'.format('#' * level, line.strip()))
            index += 2
            continue
        # code blocks become fenced blocks
        match = re.match(r'^(\s*)\.\.\s+code-block::\s*(\S*)\s*$', line)
        if match is not None:
            index = _convert_rst_block(lines, index + 1, output,
                                       '```{0}'.format(match.group(2)),
                                       '```')
            continue
        # math directives become KaTeX display blocks
        match = re.match(r'^\s*\.\.\s+math::\s*(.*)$', line)
        if match is not None:
            inline = match.group(1).strip()
            if len(inline) > 0:
                output += ['$$', inline, '$$', '']
                index += 1
                continue
            index = _convert_rst_block(lines, index + 1, output, '$$', '$$')
            continue
        # note/warning directives become admonitions
        match = re.match(r'^\s*\.\.\s+(note|warning|tip)::\s*(.*)$', line)
        if match is not None:
            output.append('!!! {0}'.format(match.group(1)))
            output.append('')
            remainder = match.group(2).strip()
            if len(remainder) > 0:
                output.append('    {0}'.format(remainder))
            index = _convert_rst_block(lines, index + 1, output, None, None,
                                       indent='    ')
            continue
        output.append(_convert_rst_inline(line))
        index += 1
    return '\n'.join(line.rstrip() for line in output)


def _is_rule(line: str, underlines: List[str]) -> bool:
    """
    Test whether a line is an rst title rule (e.g. ``=======``).

    :param line: str, the line to test
    :param underlines: list of str, the allowed rule characters

    :return: bool, True if the line is a title rule
    """
    stripped = line.strip()
    return (len(stripped) >= 3 and len(set(stripped)) == 1
            and stripped[0] in underlines)


def _convert_rst_block(lines: List[str], start: int, output: List[str],
                       opener: Optional[str], closer: Optional[str],
                       indent: str = '') -> int:
    """
    Consume an indented rst block and append it to the markdown output.

    :param lines: list of str, all source lines
    :param start: int, the index of the first line after the directive
    :param output: list of str, the markdown output being built (modified)
    :param opener: str or None, a line to emit before the block
    :param closer: str or None, a line to emit after the block
    :param indent: str, indentation to apply to each emitted block line

    :return: int, the index of the first line after the block
    """
    index = start
    # skip the blank line(s) that follow an rst directive
    while index < len(lines) and len(lines[index].strip()) == 0:
        index += 1
    block: List[str] = []
    while index < len(lines):
        line = lines[index]
        # the block ends at the first non-blank line that is not indented
        if len(line.strip()) > 0 and not line.startswith(' '):
            break
        block.append(line)
        index += 1
    # drop trailing blank lines from the captured block
    while len(block) > 0 and len(block[-1].strip()) == 0:
        block.pop()
    if opener is not None:
        output.append(opener)
    for line in block:
        output.append(indent + line.strip() if indent else line[4:])
    if closer is not None:
        output.append(closer)
    output.append('')
    return index


def _convert_rst_inline(line: str) -> str:
    """
    Convert inline rst roles and markup to markdown.

    :param line: str, a single rst line

    :return: str, the markdown equivalent
    """
    # `text <url>`_ -> [text](url)
    line = re.sub(r'`([^`<]+?)\s*<([^>]+)>`_+', r'[\1](\2)', line)
    # :ref:`text <target>` -> text (sphinx cross references have no markdown
    # equivalent, so keep the human readable part only)
    line = re.sub(r':ref:`([^`<]+?)\s*<[^>]+>`', r'\1', line)
    # :math:`x` -> $x$ (KaTeX inline maths)
    line = re.sub(r':math:`(.+?)`', r'$\1$', line)
    # some legacy fragments forget the closing backtick - take one token
    line = re.sub(r':math:`(\S+)', r'$\1$', line)
    # ``literal`` -> `literal`
    line = re.sub(r'``(.+?)``', r'`\1`', line)
    return line


def migrate_descriptions(params: ParamDict, recipe: DrsRecipe,
                         instruments: List[str]):
    """
    Convert the legacy rst description fragments into the markdown tree.

    Reads ``documentation/working/resources/{instrument}/descriptions/*.rst``
    and writes ``documentation/descriptions/{instrument}/{kind}/*.md``.
    Authored pages are preserved; only generated placeholder stubs are
    replaced, so the migration can be re-run safely.

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, the running recipe used to load definitions
    :param instruments: list of str, instruments to migrate

    :return: None, writes markdown files
    """
    legacy_root = REPO_ROOT / 'documentation' / 'working' / 'resources'
    if not legacy_root.exists():
        WLOG(params, 'warning', 'No legacy descriptions at: {0}'
                                ''.format(legacy_root))
        return
    selected = {str(item).lower() for item in instruments}
    count = 0
    for inst_dir in sorted(legacy_root.iterdir()):
        desc_dir = inst_dir / 'descriptions'
        if not desc_dir.is_dir():
            continue
        instrument = ('default' if inst_dir.name.lower() == 'default'
                      else inst_dir.name.upper())
        if instrument.lower() not in selected:
            continue
        # The live definitions distinguish recipes, tools, and sequences.
        reload_for(recipe, instrument)
        recipemod = as_module(recipe.recipemod)
        file_kinds = dict()
        for srecipe in getattr(recipemod, 'recipes', []):
            descfile = getattr(srecipe, 'description_file', None)
            if not descfile:
                continue
            if srecipe.recipe_type == 'recipe':
                kind = KIND_RECIPES
            elif srecipe.recipe_kind in ['user', 'processing']:
                kind = KIND_USER_TOOLS
            else:
                kind = KIND_DEV_TOOLS
            file_kinds[Path(descfile).stem] = (
                kind, Path(str(srecipe.name)).stem)
        for sequence in getattr(recipemod, 'sequences', []):
            descfile = getattr(sequence, 'description_file', None)
            if descfile:
                file_kinds[Path(descfile).stem] = (
                    KIND_SEQUENCES, sequence.name)
        for rst_file in sorted(desc_dir.glob('*.rst')):
            if rst_file.stem in file_kinds:
                kind, name = file_kinds[rst_file.stem]
            else:
                kind = KIND_RECIPES
                name = rst_file.stem
            outpath = description_path(inst_dir.name, kind, name)
            # Replace only a placeholder created by the docs generator.
            if outpath.exists():
                current = outpath.read_text(encoding='utf-8')
                placeholder = '<!-- Replace the diagram below with the real '
                placeholder += 'steps. -->'
                if placeholder not in current:
                    continue
            outpath.parent.mkdir(parents=True, exist_ok=True)
            body = rst_to_markdown(rst_file.read_text(encoding='utf-8'))
            header = ['---', '{0}: []'.format(DESC_ALGO_KEY),
                      '{0}: []'.format(DESC_REF_KEY), '---', '']
            outpath.write_text('\n'.join(header) + body.strip() + '\n',
                               encoding='utf-8')
            count += 1
    WLOG(params, '', 'Migrated {0} description fragments'.format(count))


# =============================================================================
# End of code
# =============================================================================
