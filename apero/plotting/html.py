#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-10-08 at 10:04

@author: cook
"""
import numpy as np
import os
import glob
from collections import OrderedDict

# =============================================================================
# Define variables
# =============================================================================
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
    def __init__(self, params, filename, extension='.pdf'):
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
        print(self._t_)

    def write_html(self):
        # deal with an unfinished file (no \end{document})
        if not self.finished:
            self.end()
        # write file to disk
        write_file(self.htmlfilename, self._t_)

    def openhtml(self):
        os.system('firefox {0}'.format(self.htmlfilename))

    def cleanup(self):
        # get all files in directory that have the filename (without extension)
        files = glob.glob(self.filename + '*')
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

    def add_title(self, title, authors=None):
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

    def newline(self, number=1):
        for _ in range(number):
            self._t_ += '\n'

    def end(self):
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
    def section(self, text):
        self.newline(2)
        self._t_ += cmd('h3', text)
        self.newline()

    def subsection(self, text):
        self.newline(2)
        self._t_ += cmd('h4', text)
        self.newline()

    def add_text(self, text):
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

    def insert_table(self, table, units=None, caption=None, label=None,
                     colormask=None):
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

    def figure(self, filename, height=None, width=None, caption=None,
               label=None):
        # set image options
        img_options = dict(src=filename)
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


def cmd(tag, inputs=None, options=None):
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
    # read the lines
    with open(filename, 'r') as f:
        lines = f.readlines()
    # return lines
    return lines


def write_file(filename, text):
    # write the lines
    with open(filename, 'w') as f:
        f.writelines(text)


def apply_colormask(lines, colormask, table):
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
    from astropy.table import Table

    x = np.arange(10000, 50000, 5000)
    y = (x / 10000.0) ** 2
    n = np.char.add(np.char.add('SIMP', x.astype(str)), '_NEW')
    datatable = Table()
    datatable['name'] = n
    datatable['value'] = x
    datatable['value2'] = y
    datamask = np.array(x % 10000).astype(bool)

    # ----------------------------------------------------------------------
    # test
    doc = HtmlDocument('test.pdf')
    doc.preamble()

    doc.add_title('This is a test', 'Neil Cook')

    doc.section('Introduction')
    doc.add_text('Here is the text of your introduction.')

    doc.subsection('Subsection Heading Here')
    doc.add_text('Write your subsection text here.')

    doc.figure('plot_TEST1_PID-00015701409882315794.png',
               width=1024, height=256,
               caption='Test figure 1', label='simple_figure')

    doc.subsection('Table test section')
    doc.insert_table(datatable, caption='Test table', label='simple_table',
                     colormask=datamask)

    doc.section('Conclusion')
    doc.add_text('Write your conclusion here')

    doc.end()

    doc.write_html()
    doc.openhtml()


# =============================================================================
# End of code
# =============================================================================
