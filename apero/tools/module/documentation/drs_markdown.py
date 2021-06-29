#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2021-06-29

@author: cook
"""
import numpy as np


# =============================================================================
# Define variables
# =============================================================================



class MarkDownPage:
    def __init__(self):
        # storage of lines for output file
        self.lines = []

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

    def add_title(self, title: str):
        """
        Add a title to a page
        :param title: str, the title to add

        :return: None, updates page
        """
        self.add_newline()
        length = np.max([len(title) + 2, 80])
        self.lines += ['*' * length]
        self.lines += [title]
        self.lines += ['*' * length]
        self.add_newline()

    def add_section(self, section_title: str):
        """
        Add a section to a page
        :param title: str, the title to add

        :return: None, updates page
        """
        self.add_newline()
        length = np.max([len(section_title) + 2, 80])
        self.lines += ['=' * length]
        self.lines += [section_title]
        self.lines += ['=' * length]
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
        self.add_newline()

    def add_text(self, text: str):
        """
        Add text to the markdown page
        :param text: str, the text to add

        :return: None, updates page
        """
        self.add_newline()
        self.lines += text.split('\n')
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
