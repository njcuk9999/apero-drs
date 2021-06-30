#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2021-06-29

@author: cook
"""
import numpy as np
import os
from typing import Optional, List

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

    def add_table_of_contents(self, names: List[str], items: List[str]):

        # add contents section
        self.add_section('Contents')
        # loop around names and items and add to contents list
        for it in range(len(names)):
            lineref = '* :ref:`{0} <{1}>`'.format(names[it], items[it])
            self.lines += [lineref]

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

    def add_csv_table(self, title: str, csv_file: str):
        """
        Create a csv table in the markdown page

        :param title: str, the title of the table
        :param csv_file: str, the path to the csv file

        :return: None, updates page
        """
        self.add_newline()
        self.lines += ['.. csv-table:: {0}'.format(title)]
        self.lines += ['   :file: {0}'.format(csv_file)]
        self.lines += ['   :header-rows: 1']
        self.lines += ['   :class: csvtable']
        self.add_newline()

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

    def include_file(self, filename: str):
        """
        Include a rst file

        :param filename: str, the rst file to add

        :return: None, updates page
        """
        basename = os.path.basename(filename)
        self.add_newline()
        self.lines += ['.. include:: {0}'.format(basename)]
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
