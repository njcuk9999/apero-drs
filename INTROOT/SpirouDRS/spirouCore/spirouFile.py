#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-04-19 at 16:16

@author: cook
"""
import numpy as np
import os
import glob

# =============================================================================
# Define variables
# =============================================================================

# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
class PathException(Exception):
    """Raised when config file is incorrect"""
    pass

class Paths():
    def __init__(self, *args, **kwargs):
        """
        Set up a path object (to be used for file operations)

        """
        # set up storage
        self.rel_paths = []
        self.abs_paths = []
        self.root = None

        # set root from kwargs
        self.root = kwargs.get('root', None)
        if self.root is not None:
            self.root = os.path.abspath(self.root)

        # load args
        self.__load_args(args)

        # update root
        self.add_root()

        # update wildcards
        self.update_wildcards()


    def __load_args(self, args):
        # arguments are expected to be either a list of strings, a list or
        # another path object
        for ai, arg in enumerate(args):
            try:
                if type(arg) == str:
                    self.rel_paths.append(arg)
                elif type(arg) in [list, np.array]:
                    self.rel_paths += list(arg)
                elif type(arg) == Paths:
                    self.rel_paths += arg.rel_paths
                    self.abs_paths += arg.abs_paths
                    self.root = arg.root
                else:
                    raise ValueError()
            except:
                emsg = ('Argument {0}={1} format={2} not understood. Argument '
                        'must be a string, a list or another paths object')
                raise PathException(emsg.format(ai+1, arg, type(arg)))
        # copy to abs_paths
        self.abs_paths = list(self.rel_paths)

    def __add__(self, value):
        return Paths(self, value)

    def add_root(self, check=False):
        # deal with user inputted roots
        # if root is blank do nothing
        if self.root == None:
            pass
        # if root is a string
        elif type(self.root) == str:
            # if check, check that root exists
            if check:
                if not os.path.exists(self.root):
                    emsg = 'Root = {0} does not exist'
                    raise PathException(emsg)
            self.abs_paths = []
            # loop around relative paths and add root
            for rel_path in self.rel_paths:
                self.abs_paths.append(os.path.join(self.root, rel_path))
        # if root is not a string break
        else:
            emsg = 'Root = {0} not a valid python string'
            raise PathException(emsg)

    def replace_root(self, root=None, check=False):
        # deal with user inputted roots
        # if root is blank do nothing
        if root == None:
            pass
        # if root is a string
        elif type(root) == str:
            # if check, check that root exists
            if check:
                if not os.path.exists(root):
                    emsg = 'Root = {0} does not exist'
                    raise PathException(emsg)
            # change to abs_root
            root = os.path.abspath(root) + os.path.sep
            # construct the abs part of original root
            part = self.root + os.path.sep
            # loop around relative paths and replace the first old root with
            #     the new root
            for ai, abs_path in enumerate(self.abs_paths):
                # replace
                self.abs_paths[ai] = abs_path.replace(part, root, 1)
            # finally update the root
            self.root = root
        # if root is not a string break
        else:
            emsg = 'Root = {0} not a valid python string'
            raise PathException(emsg)

    def update_wildcards(self):
        # storage for new paths
        rel_paths = []
        # loop around the absolute path
        for ai, abs_path in enumerate(self.abs_paths):
            # get directory path and filename
            dirname = os.path.dirname(abs_path)
            relpath = self.rel_paths[ai]
            # check that dir exists
            if os.path.exists(dirname):
                # look for wild cards (regular expression "magic")
                if glob.has_magic(abs_path):
                    # get files using wild cards
                    absfiles = list(glob.glob(abs_path))
                    # loop around files
                    for absfile in absfiles:
                        # set abs part
                        part = self.root + os.path.sep
                        # remove the root (as we are appending rel_path)
                        relfile = absfile.replace(part, '', 1)
                        # add to rel_paths
                        rel_paths.append(relfile)
                # else just append normal file
                else:
                    rel_paths.append(relpath)
            # if dirname does not exist we can't access wildcards so skip
            else:
                rel_paths.append(relpath)
        # add rel paths to self
        self.rel_paths = rel_paths
        # finally add the root back
        self.add_root()



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
