#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-10-08 at 10:04

@author: cook
"""
from astropy.table import Table
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
__NAME__ = 'plotting.html.py'
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
# define colours
GOOD_COLOUR = '67FD9A'
BAD_COLOUR = 'FD6864'
# define style
CSS = """
<style>
html{
    width:100%;
    height:100%;
}
body{
    width:100%;
    height:100%;
}

table {
  border-collapse: collapse;
}

table, td, th {
  border: 1px solid black;
}
</style>
"""


# =============================================================================
# Define class
# =============================================================================
class HtmlDocument:
    def __init__(self, params: ParamDict, filename: str,
                 extension: str = '.html'):
        """
        Construct HTML instance

        :param params: ParamDict, parameter dictionary of constants
        :param filename: str, the filename to save the html document to
        :param extension: str, the extension to save the html file to
        """
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
        self.htmlfilename = self.filename + '.html'
        # set up temporary table filename
        self.tablefile = self.filename + '.tablehtml'
        # set up the storage of the text
        self._t_ = ''
        # set up flags
        self.started = False
        self.finished = False
        # count the table and figure numbers
        self.figurenum = 1
        self.tablenum = 1

    # ----------------------------------------------------------------------
    # user functions
    # ----------------------------------------------------------------------
    def print(self):
        """
        Print the text storage

        :return: None, prints self._t_
        """
        print(self._t_)

    def write_html(self):
        """
        Write the html file using writing function

        :return: None, writes html file
        """
        # deal with an unfinished file (no \end{document})
        if not self.finished:
            self.end()
        # write file to disk
        write_file(self.htmlfilename, self._t_)

    def openhtml(self):
        """
        Open the html using firefox

        :return: None runs firefox on the html filename
        """
        command = 'firefox {0}'.format(self.htmlfilename)
        if shutil.which('firefox') is not None:
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
    def preamble(self):
        """
        Add the html preamble text (head and body)

        :return: None, updates the text storage
        """
        # do not add if we have started already
        if self.started:
            return
        else:
            # set started to True
            self.started = True
        self._t_ += r'<!DOCTYPE html>'
        self.newline()
        self._t_ += r'<html>'
        self.newline()
        self._t_ += r'<head>'
        self.newline()
        self._t_ += CSS
        self.newline()
        self._t_ += r'</head>'
        self.newline()
        self._t_ += r'<body>'
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
        self._t_ += cmd('h1', title)
        self.newline()
        if authors is not None:
            if isinstance(authors, list):
                authortext = ', '.join(authors)
            else:
                authortext = str(authors)
            self._t_ += cmd('h2', authortext)
            self.newline()

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
        The final code to add to the html document (/body /html)

        :return: None, updates text storage
        """
        # do not add if we have finished already
        if self.finished:
            return
        else:
            # set finished to True
            self.finished = True
        self._t_ += r'</body>'
        self.newline()
        self._t_ += r'</html>'
        self.newline()

    # ----------------------------------------------------------------------
    # document html functions
    # ----------------------------------------------------------------------
    def section(self, text: str):
        """
        Add a section title to the section

        :param text: str, the title of the section

        :return: None, updates text storage
        """
        self.newline(2)
        self._t_ += cmd('h3', text)
        self.newline()

    def subsection(self, text: str):
        """
        Add a sub-section title to the section

        :param text: str, the title of the sub-section

        :return: None, updates text storage
        """
        self.newline(2)
        self._t_ += cmd('h4', text)
        self.newline()

    def add_text(self, text: Union[List[str], str]):
        """
        Add a text block to the html document

        :param text: str, the text to add to the block

        :return: None, updates text storage
        """
        self.newline()
        self._t_ += r'<p>'
        self.newline()
        # deal with text as list or string
        if isinstance(text, str):
            text = [text]
        # loop around and add
        for text_it in text:
            self._t_ += text_it + r'<br>'
            self.newline()
        self.newline()
        self._t_ += r'</p>'
        self.newline()

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
        # units / label not used for html
        _ = units, label
        # write to temporary file
        table.write(self.tablefile, format='html', overwrite=True)
        # open table and insert into text
        lines = open_file(self.tablefile)
        # deal with colour mask defined
        lines = apply_colormask(lines, colormask, table)
        # add caption
        if caption is None:
            caption = 'Table {0}'.format(self.tablenum)
        else:
            caption = 'Table {0}: {1}'.format(self.tablenum, caption)
        # add the caption
        self.newline()
        self.add_text(caption)
        self.newline()
        # write to text
        self.newline()
        for line in lines:
            self._t_ += line
        # count tables
        self.tablenum += 1

    def figure(self, filename: str, height: Union[int, None] = None,
               width: Union[int, None] = None, caption: Union[str, None] = None,
               label: Union[str, None] = None):
        """
        Add a figure (image from source "filename") to the html document,
        can set height, width and caption

        :param filename: str, the absolute path to the image to add
        :param height: int or None, if set forces the height of the figure
        :param width: int or None, if set forces the width of the figure
        :param caption: str or None, if set adds a caption to the figure
        :param label: str or None, not used for html document

        :return: None, updates text storage
        """
        # we don't use label from html
        _ = label
        # make sure filename is just the basename
        basename = os.path.basename(filename)
        # set image options
        img_options = dict(src=basename)
        if height is not None:
            img_options['height'] = str(width)
        if width is not None:
            img_options['width'] = str(width)
        self.newline()
        self._t_ += cmd('img', options=img_options)
        self.newline()
        if caption is not None:
            self.add_text(caption)
            self.newline()


# =============================================================================
# Define functions
# =============================================================================
def cmd(tag: str, inputs: Union[str, None] = None,
        options: Union[Dict[str, str], None] = None) -> str:
    """
    Add a html command in the form:

    <tag> </tag>
    <tag option> </tag>
    <tag option> inputs </tag>

    Depending on inputs and options

    where options = dict(option1=value1, option2=value2) such that
    <tag option1="value1" option2="value2"> inputs </tag>

    :param tag: str, the command "tag"
    :param inputs: str or None, if set the command "input"
    :param options: dict or None, a set of options for the command

    :return: None, updates text storage
    """
    # define tag start/end
    start = r'<{0}>'.format(tag)
    end = r'</{0}>'.format(tag)
    # add options
    if options is not None:
        textoptions = ''
        for option in options:
            textoptions += ' {0}="{1}"'.format(option, options[option])
        command = r'<{0}{1}>'.format(tag, textoptions)
    else:
        command = start
    # add inputs
    if inputs is None:
        pass
    else:
        command += inputs
    # add end
    command += end
    return command


def open_file(filename):
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
    Apply a colour mask to the html table - i.e. colour any rows that
    have colormask == True with "GOOD_COLOUR" and colour any rows that have
    colormask == False with "BAD_COLOUR"

    :param lines: list of strings, the html table entry lines to column
    :param colormask: list or numpy array, same as length of lines, a True or
                      False for each line to be coloured "good" (else coloured
                      "bad")
    :param table: astropy.table.Table the original table to make sure length
                  is correct

    :return: list of strings, the updated "lines"
    """
    if colormask is not None:
        # get good latex cmd
        goodcmd = r'<tr bgcolor="#{0}">'.format(GOOD_COLOUR)
        # get bad latex cmd
        badcmd = r'<tr bgcolor="#{0}">'.format(BAD_COLOUR)

        # need to store when we are before head
        afterhead = False
        # make sure colormask is the same length as table
        if len(colormask) == len(table):
            # set the initial line number
            row = 0
            # set new lines storage
            newlines = []
            # loop around old lines
            for line in lines:
                # skip until after head
                if r'</thead>' in line:
                    afterhead = True
                if not afterhead:
                    newlines.append(line)
                    continue
                # if we have a line we need to edit it
                if line.strip() == r'<tr>':
                    # skip the header
                    if row >= len(colormask):
                        newlines.append(line)
                        continue
                    # if true line is good
                    if colormask[row]:
                        newline = line.replace(r'<tr>', goodcmd)
                    # else line is bad
                    else:
                        newline = line.replace(r'<tr>', badcmd)
                    # append to storage
                    newlines.append(newline)
                    row += 1
                # else do not touch the line
                else:
                    newlines.append(line)
            # reverse lines
            newlines = newlines

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
    # Create a test html file
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
    # test the various parts of the Html document
    # ----------------------------------------------------------------------
    # start the html document
    doc = HtmlDocument(_params, 'test.pdf')
    # load the preamble
    doc.preamble()
    # add a title + authors
    doc.add_title('This is a test', 'Neil Cook')
    # add an introduction section
    doc.section('Introduction')
    # add some introductory text
    doc.add_text('Here is the text of your introduction.')
    # add a sub-section
    doc.subsection('Subsection Heading Here')
    # add some text to the sub-section
    doc.add_text('Write your subsection text here.')
    # add a test figure (must exist on disk)
    doc.figure('plot_TEST1_PID-00015701409882315794.png',
               width=1024, height=256,
               caption='Test figure 1', label='simple_figure')
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
    # write the html file to disk
    doc.write_html()
    # try to open (this may not work but should not generate a python error)
    doc.openhtml()


# =============================================================================
# End of code
# =============================================================================
