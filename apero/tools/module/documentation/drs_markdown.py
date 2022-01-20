#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2021-06-29

@author: cook
"""
from astropy.table import Table
import numpy as np
import os
from typing import Optional, List, Union

# =============================================================================
# Define variables
# =============================================================================
class MarkDownPage:
    def __init__(self, page_ref):
        # store the page reference
        self.page_ref = page_ref
        # storage of lines for output file
        self.lines = []
        # add page ref to top of page
        self.add_reference(page_ref)
        # multi-line table flag
        self.multiline_table_enabled = False

    def write_page(self, filename: str):
        """
        Write a page to filename

        :param filename: str, the path and filename of the page to write

        :return: None, writes to 'filename'
        """
        with open(filename, 'w') as page:
            for line in self.lines:
                page.write(line + '\n')

    # -------------------------------------------------------------------------
    # add methods (widgets)
    # -------------------------------------------------------------------------
    def add_newline(self, nlines: int = 1):
        """
        Add new line(s) to a page

        :param nlines: int, the number of lines to add (default = 1)

        :return: None, updates page
        """
        for _ in range(nlines):
            self.lines += ['']

    def add_table_of_contents(self, items: List[str],
                              names: Optional[List[str]] = None,
                              sectionname: str = 'Contents',
                              maxdepth: int = 1):

        self.add_newline()
        # no names means items are url links to other pages
        if names is None:
            self.lines += ['.. toctree::']
            self.lines += ['    :maxdepth: {0}'.format(maxdepth)]
            self.lines += ['    :caption: {0}'.format(sectionname)]
            self.add_newline()
            for it in range(len(items)):
                self.lines += ['    {0}'.format(items[it])]
        # names means we have references to other pages
        else:
            # add contents section
            self.add_section(sectionname)
            # loop around names and items and add to contents list
            for it in range(len(names)):
                lineref = '* :ref:`{0} <{1}>`'.format(names[it], items[it])
                self.lines += [lineref]
        self.add_newline()


    def add_back_to_top(self):
        """
        Add a reference to go back to the top of the page
        :return:
        """
        self.lines += ['.. only:: html', '']
        self.lines += ['  :ref:`Back to top <{0}>`'.format(self.page_ref)]

    def add_title(self, title: str):
        """
        Add a title to a page
        :param title: str, the title to add

        :return: None, updates page
        """
        self.add_newline()
        length = np.max([len(title) + 2, 80])
        self.lines += ['#' * length]
        self.lines += [title]
        self.lines += ['#' * length]
        self.add_newline()

    def add_reference(self, reference: str):
        """
        Add a reference to a section / page

        :param reference: str, th e reference to add
        :return:
        """
        self.add_newline()
        self.lines += ['.. _{0}:'.format(reference)]
        self.add_newline()

    def add_section(self, section_title: str):
        """
        Add a section to a page
        :param title: str, the title to add

        :return: None, updates page
        """
        self.add_newline()
        length = np.max([len(section_title) + 2, 80])
        self.lines += ['*' * length]
        self.lines += [section_title]
        self.lines += ['*' * length]
        self.add_newline()

    def add_sub_section(self, section_title: str):
        """
        Add a section to a page
        :param title: str, the title to add

        :return: None, updates page
        """
        self.add_newline()
        length = np.max([len(section_title) + 2, 80])
        self.lines += ['^' * length]
        self.lines += [section_title]
        self.lines += ['^' * length]
        self.add_newline()

    def add_csv_table(self, title: str, csv_file: str,
                      abs_path: Union[str, None] = None):
        """
        Create a csv table in the markdown page

        :param title: str, the title of the table
        :param csv_file: str, the path to the csv file

        :return: None, updates page
        """
        # if a abs_path is supplied we can check the file for rows, if there
        #   are no rows do not add the csv-table
        table_has_rows = True
        # check abs_path
        if abs_path is not None:
            # if we cannot load table don't add csv-table
            try:
                table = Table.read(abs_path, format='csv')
                # check length of table
                if len(table) == 0:
                    table_has_rows = False
                # delete table
                del table
            except Exception as _:
                table_has_rows = False
        # only add csv table if we have rows
        if table_has_rows:
            self.add_newline()
            self.lines += ['.. csv-table:: {0}'.format(title)]
            self.lines += ['   :file: {0}'.format(csv_file)]
            self.lines += ['   :header-rows: 1']
            self.lines += ['   :class: csvtable']
            self.add_newline()
        else:
            self.add_newline()
            self.add_text('N/A')
            self.add_newline()

    def enable_multiline_table(self):
        """
        If table uses the |br| tag must add these lines

        :return: None, updates page
        """
        # if we have already enabled multiline tables don't do it again
        if self.multiline_table_enabled:
            return
        # enable multiline tables
        self.lines += ['.. |br| raw:: html']
        self.lines += ['']
        self.lines += ['     <br>']
        # flag that for this page we have already enabled multiline tables
        self.multiline_table_enabled = True

    def add_text(self, text: str):
        """
        Add text to the markdown page
        :param text: str, the text to add

        :return: None, updates page
        """
        # add the text
        self.add_newline()
        self.lines += text.split('\n')
        self.add_newline()

    def add_image(self, filename: str, width: Optional[int] = None,
                  align: str = 'center'):
        """
        Add image to the markdown page

        :param filename: str, the filename to the image (relative to this
                         directory)
        :param width: int, the percentage of the page to take up
        :param align: str, either 'center', 'left' or 'right'

        :return: None, updates page
        """
        self.add_newline()
        self.lines += ['.. only:: html']
        self.add_newline()
        self.lines += ['    .. image:: {0}'.format(filename)]
        if width is not None:
            self.lines += ['        :width: {0}%'.format(width)]
        if align is not None:
            self.lines += ['        :align: {0}'.format(align)]
        self.add_newline()
        self.lines += ['.. only:: latex']
        self.add_newline()
        self.lines += ['    This section can only currently be viewed in the '
                       'html documentation.']

    def include_file(self, filename: str):
        """
        Include a rst file

        :param filename: str, the rst file to add

        :return: None, updates page
        """
        self.add_newline()
        self.lines += ['.. include:: {0}'.format(filename)]
        self.add_newline()

    def add_code_block(self, codetype: str, codetext: List[str]):
        """
        Add a code block

        :param codetype: str, the code type (i.e. bash, python etc)
        :param codetext: List of strings, the code text to add

        :return: None, updates page
        """
        self.add_newline()
        self.lines += ['.. code-block:: {0}'.format(codetype)]
        self.add_newline()
        # loop around lines of code
        for codeit in codetext:
            self.lines += ['    {0}'.format(codeit)]
        self.add_newline()


# =============================================================================
# Define functions
# =============================================================================


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # print hello world
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
