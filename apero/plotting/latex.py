#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-10-04 at 14:14

@author: cook
"""
from astropy.table import Table
from collections import OrderedDict
import glob
import numpy as np
import os
import shutil
from typing import Dict, List, Union

from apero.base import base
from apero.core import constants

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'plotting.latex.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get parameter dictionary class
ParamDict = constants.ParamDict
# define known extensions
KNOWN_EXTENSIONS = ['.pdf', '.tex', '.html']
# define latex packages to add (with options)
PACKAGELIST = OrderedDict()
PACKAGELIST['graphicx'] = None
PACKAGELIST['geometry'] = 'margin=1cm'
PACKAGELIST['xcolor'] = 'table, xcdraw'
PACKAGELIST['placeins'] = None
# define colours
GOOD_COLOUR = '67FD9A'
BAD_COLOUR = 'FD6864'
ROW_END_TEX = '\\\\\n'
# -----------------------------------------------------------------------------
# LATEX SYMBOLS
SYMBOLS = OrderedDict()
SYMBOLS['_'] = r'\_'
SYMBOLS['>'] = r'$>$'
SYMBOLS['<'] = r'$<$'
SYMBOLS['%'] = r'\%'
SYMBOLS['['] = r'\['
SYMBOLS[']'] = r'\]'


# =============================================================================
# Define classes
# =============================================================================
class LatexDocument:
    def __init__(self, params: ParamDict, filename: str,
                 extension: str = '.pdf'):
        """
        Construct Latex instance

        :param params: ParamDict, parameter dictionary of constants
        :param filename: str, the filename to save the html document to
        :param extension: str, the extension to save the html file to
        """
        # save params
        self.params = params
        # remove extensions
        if extension in filename:
            self.filename = filename[:-len(extension)]
        else:
            self.filename = filename
        # remove any known extensions
        for ext in KNOWN_EXTENSIONS:
            while self.filename.endswith(ext):
                self.filename = self.filename[:-len(ext)]
        # set up latex filename
        self.latexfilename = self.filename + '.tex'
        # set up pdf filename
        self.pdffilename = self.filename + '.pdf'
        # set up temporary table filename
        self.tablefile = self.filename + '.tablelatex'
        # set up the storage of the text
        self._t_ = ''
        # set up flags
        self.started = False
        self.finished = False

    # ----------------------------------------------------------------------
    # user functions
    # ----------------------------------------------------------------------
    def print(self):
        """
        Print the text storage

        :return: None, prints self._t_
        """
        print(self._t_)

    def write_latex(self):
        """
        Write the latex file using writing function

        :return: None, writes html file
        """
        # deal with an unfinished file (no \end{document})
        if not self.finished:
            self.end()
        # write file to disk
        write_file(self.latexfilename, self._t_)

    def openpdf(self):
        """
        Open the latex using okular

        :return: None runs firefox on the html filename
        """
        command = 'okular {0}'.format(self.pdffilename)
        if shutil.which('okular') is not None:
            os.system(command)
        else:
            print('Cannot run command: {0}'.format(command))

    def cleanup(self):
        """
        Remove all temporary files from the filename

        :return: None - removes files
        """
        # get all files in directory that have the filename (without extension)
        files = np.sort(glob.glob(self.filename + '*'))
        # loop around files
        for filename in files:
            # get extension
            ext = '.' + filename.split('.')[-1]
            # do not remove extensions of known types
            if ext in KNOWN_EXTENSIONS:
                continue
            # remove everything else
            else:
                os.remove(filename)

    # ----------------------------------------------------------------------
    # top level latex functions
    # ----------------------------------------------------------------------
    def preamble(self, documentclass: Union[str, None] = None,
                 packages: Union[Dict[str, str], None] = None):
        """
        Add the latex preamble text (head and body)

        :param documentclass: str, the document class (if None set to "article")
        :param packages: dictionary of packages, list of latex packages required

        :return: None, updates the text storage
        """
        # add documentclass
        if documentclass is None:
            self._t_ += cmd('documentclass', 'article')
        else:
            self._t_ += cmd('documentclass', documentclass)
        self.newline(2)
        # add comment
        self._t_ += comment('Add packages')
        self.newline()
        # add default packages
        for pname in PACKAGELIST:
            # deal with user defined packages duplication
            if packages is not None and pname in packages:
                continue
            # get options
            options = PACKAGELIST[pname]
            # deal with no options
            if options is None:
                self._t_ += cmd('usepackage', pname)
            else:
                self._t_ += cmd('usepackage', pname, options)
            self.newline()
        # add user packages
        if packages is not None:
            for pname in packages:
                # get options
                options = packages[pname]
                # deal with no options
                if options is None:
                    self._t_ += cmd('usepackage', pname)
                else:
                    self._t_ += cmd('usepackage', pname, options)
        self.newline()

    def begin(self):
        """
        The latex begin document text

        :return: None, updates the text storage
        """
        # do not add if we have started already
        if self.started:
            return
        # add comment
        self.newline(2)
        self._t_ += comment('Begin document')
        self.newline()
        # set started to True
        self.started = True
        # add \begin{document}
        self._t_ += cmd('begin', 'document')
        self.newline()

    def add_title(self, title: str,
                  authors: Union[List[str], str, None] = None):
        """
        Add a title to the html page

        :param title: str, the title to add
        :param authors: list of strings or a string, the author(s) to add to
                        the html page

        :return: None, updates the text storage
        """
        self.newline()
        self._t_ += comment('Add title and authors')
        self.newline()
        self._t_ += cmd('title', title)
        self.newline()
        if authors is not None:
            if isinstance(authors, list):
                for author in authors:
                    self._t_ += cmd('author', author)
                    self.newline()
            else:
                self._t_ += cmd('author', authors)
        self.newline(2)
        self._t_ += cmd('maketitle')

    def newline(self, number: int = 1):
        """
        Add some new lines to the text storage

        :param number: int, the number of lines to add

        :return: None, updates text storage
        """
        for _ in range(number):
            self._t_ += '\n'

    def end(self):
        """
        The final code to add to the latex document (end, document)

        :return: None, updates text storage
        """
        # do not add if we have finished already
        if self.finished:
            return
        # add comment
        self.newline(2)
        self._t_ += comment('End document')
        self.newline()
        # set finished to True
        self.finished = True
        # add \begin{document}
        self._t_ += cmd('end', 'document')
        self.newline()

    # ----------------------------------------------------------------------
    # document latex functions
    # ----------------------------------------------------------------------
    def section(self, text: str):
        """
        Add a section title to the section

        :param text: str, the title of the section

        :return: None, updates text storage
        """
        self.newline(2)
        self._t_ += cmd('section', text)
        self.newline()

    def subsection(self, text: str):
        """
        Add a sub-section title to the section

        :param text: str, the title of the sub-section

        :return: None, updates text storage
        """
        self.newline(2)
        self._t_ += cmd('subsection', text)
        self.newline()

    def subsubsection(self, text: str):
        """
        Add a sub-sub-section title to the section

        :param text: str, the title of the sub-sub-section

        :return: None, updates text storage
        """
        self.newline(2)
        self._t_ += cmd('subsubsection', text)
        self.newline()

    def add_text(self, text: str):
        """
        Add a text block to the latex document

        :param text: str, the text to add to the block

        :return: None, updates text storage
        """
        self.newline()
        # deal with text as list or string
        if isinstance(text, str):
            text = [text]
        # loop around and add
        for text_it in text:
            self._t_ += text_it

    def insert(self, text: str):
        """
        insert a single line of text

        :param text: str
        :return:
        """
        self.newline()
        self._t_ += text

    def insert_latex(self, filename: str):
        """
        inserts latex code from "filename" into the text storage

        :param filename: str, the filename to read latex code from

        :return: None, updates text storage
        """
        lines = open_file(filename)
        # write to text
        self.newline()
        for line in lines:
            self._t_ += line

    def insert_table(self, table: Table,
                     units: Union[Dict[str, str], None] = None,
                     caption: Union[str, None] = None,
                     label: Union[str, None] = None,
                     colormask: Union[np.ndarray, list, None] = None):
        """
        Insert a table into the html document

        :param table: astropy.table.Table instance, the table to add
        :param units: Dict or None, this is not used for html but here to
                      be the same as latex function
        :param caption: str, the caption for the table
        :param label: str, this is not used for html but here to be same as
                      latex function
        :param colormask: np.ndarray or list, the mask of True / False for
                          colouring table elements by (decided by "GOOD_COLOUR"
                          and "BAD_COLOUR" global constants)

        :return: None, updates text storage
        """
        # get the number of columns
        num_cols = len(table.colnames)
        # set up the column alignment
        col_align = '|l' * num_cols + '|'
        # set up caption
        if caption is not None and label is not None:
            caption = caption + ' ' + cmd('label', label)
        elif caption is not None:
            caption = caption
        elif label is not None:
            caption = cmd('label', label)
        else:
            caption = None
        # set up latex dictionary
        latexdict = dict(header_start=r'\hline', header_end=r'\hline',
                         data_end=r'\hline', col_align=col_align,
                         tablealign='[h!]', preamble=r'\centering')
        if units is not None:
            latexdict['units'] = units
        if caption is not None:
            latexdict['caption'] = caption
        # fix table - need to clean bad characters
        for col in table.colnames:
            # check if column has strings
            if isinstance(table[col][0], str):
                table[col] = cleanlist(table[col])
        # write to temporary file
        table.write(self.tablefile, format='latex', overwrite=True,
                    latexdict=latexdict)
        # open table and insert into text
        lines = open_file(self.tablefile)
        # deal with colour mask defined
        lines = apply_colormask(lines, colormask, table)
        # write to text
        self.newline()
        for line in lines:
            self._t_ += line
        self.newline()
        # remove table file
        if os.path.exists(self.tablefile):
            os.remove(self.tablefile)

    def add_command(self, command: str,
                    inputs: Union[str, None] = None,
                    options: Union[str, None] = None):
        """
        Add a latex command to the text storage

        in form:
            command
            command[options]
            command[options]{inputs}

        depending whether options and inputs are set

        :param command: str, a valid latex command
        :param inputs: str or None, the inputs to given command
        :param options: str or None, the options for given command

        :return: None, updates text storage
        """
        self.newline()
        self._t_ += cmd(command, inputs, options)
        self.newline()

    # ----------------------------------------------------------------------
    # environment latex functions
    # ----------------------------------------------------------------------
    def equation(self, text: str, label: Union[str, None] = None):
        """
        Add equation to the latex document

        :param text: str, the equation to add (supports full latex math code)
        :param label: str, the label reference to give this equation

        :return: None, updates text storage
        """
        self.newline(2)
        # add equation start
        self._t_ += cmd('begin', 'equation')
        self.newline()
        # add label if defined
        if label is not None:
            self._t_ += '\t' + cmd('label', label)
            self.newline()
        # add equation text
        self._t_ += '\t' + text
        self.newline()
        # add equation end
        self._t_ += cmd('end', 'equation')
        self.newline()

    def figure(self, filename: str, height: Union[int, None] = None,
               width: Union[int, None] = None, caption: Union[str, None] = None,
               label: Union[str, None] = None):
        """
        Add a figure (image from source "filename") to the latex document,
        can set height, width and caption

        :param filename: str, the absolute path to the image to add
        :param height: int or None, if set forces the height of the figure
        :param width: int or None, if set forces the width of the figure
        :param caption: str or None, if set adds a caption to the figure
        :param label: str or None, if set adds the reference to the figure

        :return: None, updates text storage
        """
        self.newline(2)
        # add equation start
        self._t_ += cmd('begin', 'figure') + '[hp]'
        self.newline()
        # add centering
        self._t_ += '\t' + cmd('centering')
        self.newline()
        # add graphic
        if height is not None and width is not None:
            options = 'width={0}cm, height={1}cm'.format(height, width)
            self._t_ += '\t' + cmd('includegraphics', filename, options)
        elif height is not None:
            options = 'height={0}cm'.format(height)
            self._t_ += '\t' + cmd('includegraphics', filename, options)
        elif width is not None:
            options = 'width={0}cm'.format(width)
            self._t_ += '\t' + cmd('includegraphics', filename, options)
        else:
            self._t_ += '\t' + cmd('includegraphics', filename)
        self.newline()
        # add label if defined
        if label is not None:
            self._t_ += '\t' + cmd('label', label)
            self.newline()
        # add caption if defined
        if caption is not None:
            self._t_ += '\t' + cmd('caption', caption)
            self.newline()
        # add equation end
        self._t_ += cmd('end', 'figure')
        self.newline(2)


# =============================================================================
# Define functions
# =============================================================================
def cmd(command: str, inputs: Union[str, None] = None,
        options: Union[str, None] = None) -> str:
    """
    Add a latex command in the form:

        command
        command[options]
        command[options]{inputs}

    depending whether options and inputs are set

    :param command: str, the latex command to add
    :param inputs: str or None, if set the string of inputs (valid for latex)
    :param options: str or None, if set the string of options (valid for latex)

    :return: None, updates text storage
    """
    # set up keywords
    kwargs = dict(command=command, input=inputs, options=options)
    # add command name
    command = r'\{command}'.format(**kwargs)
    # add options
    if options is not None:
        command += r'[{options}]'.format(**kwargs)
    # add input
    if inputs is not None:
        command += r'{{{input}}}'.format(**kwargs)
    # return
    return command


def clean(text: Union[List[str], str]) -> Union[List[str], str]:
    """
    Clean some text so that it is valid for latex

    :param text: str or list of strings, the text to be cleaned

    :return: str or list of strings, the updated text that should be valid
             for latex
    """
    # if we have a list go to clean list function
    if isinstance(text, list):
        return cleanlist(text)
    # else copy new text
    else:
        newtext = str(text)
    # define a proxy for not replacing
    proxy = '@' * 100
    # 1. deal with symbols
    for symbol in SYMBOLS:
        # special case for % (if it is a comment)
        if newtext.strip().startswith('%'):
            newtext = newtext.replace('%', proxy, 1)
        # make sure we have no corrections already
        if SYMBOLS[symbol] in newtext:
            newtext = newtext.replace(SYMBOLS[symbol], proxy)
        # clean symbol
        if symbol in newtext:
            newtext = newtext.replace(symbol, SYMBOLS[symbol])
        # re-replace corrections already applied
        if proxy in newtext:
            newtext = newtext.replace(proxy, SYMBOLS[symbol])
    # return new text
    return newtext


def cleanlist(textlist: Union[List[str], str]) -> Union[List[str], str]:
    """
    Wrapper around "clean" - clean text function - takes a list of strings
    and cleans them

    :param textlist: list of strings or string, a list of strings to clean
                     ready for use in latex

    :return: list of strings or string, update textlist of strings cleaned
    """
    if isinstance(textlist, str):
        return clean(textlist)
    else:
        # 1. deal with symbols
        for symbol in SYMBOLS:
            textlist = np.char.replace(textlist, symbol, SYMBOLS[symbol])
    # return new text
    return textlist


def comment(text: str) -> str:
    """
    Add a latex command

    :param text: string, the command to add (without % prefix)

    :return: the updated comment text
    """
    return r'% {0}'.format(text)


def open_file(filename: str) -> List[str]:
    """
    Read a text file and return all lines of text

    :param filename: str, the filename to open

    :return: list of strings, the strings to read
    """
    # read the lines
    with open(filename, 'r') as rfile:
        lines = rfile.readlines()
    # return lines
    return lines


def write_file(filename: str, text: Union[List[str], str]):
    """
    Write the "text" to "filename"

    :param filename: str, the filename to write to

    :param text: list of strings, the text to write

    :return: None, writes to "filename"
    """
    if isinstance(text, str):
        text = [text]
    # write the lines
    with open(filename, 'w') as wfile:
        wfile.writelines(text)


def apply_colormask(lines: List[str], colormask: Union[list, np.ndarray],
                    table: Table) -> List[str]:
    """
    Apply a colour mask to the latex table - i.e. colour any rows that
    have colormask == True with "GOOD_COLOUR" and colour any rows that have
    colormask == False with "BAD_COLOUR"

    :param lines: list of strings, the latex table entry lines to column
    :param colormask: list or numpy array, same as length of lines, a True or
                      False for each line to be coloured "good" (else coloured
                      "bad")
    :param table: astropy.table.Table the original table to make sure length
                  is correct

    :return: list of strings, the updated "lines"
    """
    if colormask is not None:
        # get good latex cmd
        goodcmd = cmd('rowcolor', GOOD_COLOUR, 'HTML') + ' '
        # get bad latex cmd
        badcmd = cmd('rowcolor', BAD_COLOUR, 'HTML') + ' '
        # make sure colormask is the same length as table
        if len(colormask) == len(table):
            # set the initial line number
            row = 1
            # set new lines storage
            newlines = []
            # loop around old lines (in reverse to avoid units/column names)
            for line in lines[::-1]:
                # if we have a line we need to edit it
                if line.endswith(ROW_END_TEX):
                    # skip the header
                    if row > len(colormask):
                        newlines.append(line)
                        continue
                    # if true line is good
                    if colormask[-row]:
                        newline = goodcmd + line
                    # else line is bad
                    else:
                        newline = badcmd + line
                    # append to storage
                    newlines.append(newline)
                    row += 1
                # else do not touch the line
                else:
                    newlines.append(line)
            # reverse lines
            newlines = newlines[::-1]

        # if colormask is not correct length do nothing
        else:
            newlines = list(lines)
    # if colormask is not set do nothing
    else:
        newlines = list(lines)
    # return new lines
    return newlines


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # get params
    _params = constants.load()
    # -------------------------------------------------------------------------
    # create a test latex file
    # -------------------------------------------------------------------------
    # step 1. we need some fake table data
    x = np.arange(10000, 50000, 5000)
    y = (x / 10000.0) ** 2
    n = np.char.add(np.char.add('SIMP', x.astype(str)), '_NEW')
    # push into a table
    datatable = Table()
    datatable['name'] = n
    datatable['value'] = x
    datatable['value2'] = y
    # create a mask (for the coloured rows)
    datamask = np.array(x % 10000).astype(bool)
    # ----------------------------------------------------------------------
    # test the various parts of the Latex document
    # ----------------------------------------------------------------------
    # start the latex document
    doc = LatexDocument(_params, 'test.pdf')
    # load the preamble
    doc.preamble()
    # begin the latex document
    doc.begin()
    # add a title + authors
    doc.add_title('This is a test', 'Neil Cook')
    # add an introduction section
    doc.section('Introduction')
    # add some introductory text
    doc.add_text('Here is the text of your introduction.')
    # add an equation
    doc.equation(r'\alpha = \sqrt{\beta}', label='simple_equation')
    # add a sub-section
    doc.subsection('Subsection Heading Here')
    # add some text to the sub-section
    doc.add_text('Write your subsection text here.')
    # add a test figure (must exist on disk)
    doc.figure('plot_TEST1_PID-00015701409882315794.pdf',
               width=14, caption='Test figure 1', label='simple_figure')
    # add a sub section for the table
    doc.subsection('Table test section')
    # add the table
    doc.insert_table(datatable, caption='Test table', label='simple_table',
                     colormask=datamask)
    # add a conclusion section
    doc.section('Conclusion')
    # add some conclusion text
    doc.add_text('Write your conclusion here')
    # end the document
    doc.end()
    # write the latex file to disk
    doc.write_latex()


# =============================================================================
# End of code
# =============================================================================
