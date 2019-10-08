#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-10-04 at 14:14

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
# define latex packages to add (with options)
PACKAGELIST = dict()
PACKAGELIST['graphicx'] = None
PACKAGELIST['geometry'] = 'margin=1cm'
PACKAGELIST['xcolor'] = 'table, xcdraw'
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
# LATEX COMMAND
LATEX_CMD = 'pdflatex -halt-on-error'

# =============================================================================
# Define classes
# =============================================================================
class LatexDocument:
    def __init__(self, filename, extension='.pdf'):
        # remove extensions
        if extension in filename:
            self.filename = filename[:-len(extension)]
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
        print(self._t_)

    def write_latex(self):
        # deal with an unfinished file (no \end{document})
        if not self.finished:
            self.end()
        # write file to disk
        write_file(self.latexfilename, self._t_)

    def compile(self, logfile):
        # get current working directory
        cwd = os.getcwd()
        if os.path.dirname(self.latexfilename) != '':
            # change to path
            os.chdir(os.path.dirname(self.latexfilename))
        # compile the tex file
        cargs = [LATEX_CMD, self.latexfilename, logfile]
        os.system('{0} {1} >> {2}'.format(*cargs))
        # change back to original directory
        if os.path.dirname(self.latexfilename) != '':
            os.chdir(cwd)

    def openpdf(self):
        os.system('okular {0}'.format(self.pdffilename))

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
    def preamble(self, documentclass=None, packages=None):
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

    def end(self):
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

    def newline(self, number=1):
        for _ in range(number):
            self._t_ += '\n'

    def add_title(self, title, authors=None):
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

    # ----------------------------------------------------------------------
    # document latex functions
    # ----------------------------------------------------------------------
    def section(self, text):
        self.newline(2)
        self._t_ += cmd('section', text)
        self.newline()

    def subsection(self, text):
        self.newline(2)
        self._t_ += cmd('subsection', text)
        self.newline()

    def subsubsection(self, text):
        self.newline(2)
        self._t_ += cmd('subsubsection', text)
        self.newline()

    def add_text(self, text):
        self.newline()
        # deal with text as list or string
        if isinstance(text, str):
            text = [text]
        # loop around and add
        for text_it in text:
            self._t_ += text_it

    def insert(self, text):
        self.newline()
        self._t_ += text

    def insert_latex(self, filename):
        lines = open_file(filename)
        # write to text
        self.newline()
        for line in lines:
            self._t_ += line

    def insert_table(self, table, units=None, caption=None, label=None,
                     colormask=None):
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
                         tablealign='h!', preamble=r'\centering')
        if units is not None:
            latexdict['units'] = units
        if caption is not None:
            latexdict['caption'] = caption
        # fix table - underscores need '\_'
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
        # remove table file
        if os.path.exists(self.tablefile):
            os.remove(self.tablefile)

    def add_command(self, command, inputs=None, options=None):
        self.newline()
        self._t_ += cmd(command, inputs, options)
        self.newline()

    # ----------------------------------------------------------------------
    # environment latex functions
    # ----------------------------------------------------------------------
    def equation(self, text, label=None):
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

    def figure(self, filename, height=None, width=None, caption=None,
               label=None):
        self.newline(2)
        # add equation start
        self._t_ += cmd('begin', 'figure') + '[ht]'
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
def clean(text):
    if isinstance(text, list):
        return cleanlist(text)
    else:
        newtext = str(text)
    # 1. deal with symbols
    for symbol in SYMBOLS:
        if symbol in newtext:
            newtext = newtext.replace(symbol, SYMBOLS[symbol])

    # return new text
    return newtext


def cleanlist(textlist):
    if isinstance(textlist, str):
        return clean(textlist)
    else:
        # 1. deal with symbols
        for symbol in SYMBOLS:
            textlist = np.char.replace(textlist, symbol, SYMBOLS[symbol])
    # return new text
    return textlist


def cmd(command, inputs=None, options=None):
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


def comment(text):
    return r'% {0}'.format(text)


def open_file(filename):
    # open file
    readfile = open(filename, 'r')
    lines = readfile.readlines()
    readfile.close()
    return lines


def write_file(filename, text):
    writefile = open(filename, 'w')
    writefile.writelines(text)
    writefile.close()


def apply_colormask(lines, colormask, table):
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
    doc = LatexDocument('test.pdf')
    doc.preamble()
    doc.begin()
    doc.add_title('This is a test', 'Neil Cook')
    
    doc.section('Introduction')
    doc.add_text('Here is the text of your introduction.')
    
    doc.equation(r'\alpha = \sqrt{\beta}', label='simple_equation')

    doc.subsection('Subsection Heading Here')
    doc.add_text('Write your subsection text here.')

    doc.figure('plot_TEST1_PID-00015701409882315794.pdf',
               width=14, caption='Test figure 1', label='simple_figure')

    doc.subsection('Table test section')
    doc.insert_table(datatable, caption='Test table', label='simple_table',
                     colormask=datamask)

    doc.section('Conclusion')
    doc.add_text('Write your conclusion here')

    doc.end()

    doc.write_latex()
    doc.compile('log.txt')
    doc.openpdf()


# =============================================================================
# End of code
# =============================================================================
