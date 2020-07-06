#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-05-21

@author: cook
"""
import numpy as np


# https://en.wikipedia.org/wiki/Adler-32
# Alder 32 algorithm
# try with sample string:
#
# string = 'Wikipedia'

# =============================================================================
# Define variables
# =============================================================================


# =============================================================================
# Define functions
# =============================================================================

def adler32(string):

    b = [a for a in string.encode(encoding ='ascii')]
    b = np.array(b,dtype = int)
    A = (np.cumsum(b)+1)[-1] % 635521
    n = np.arange(len(b),0,-1)
    B = np.cumsum( (np.cumsum(b)+1) )[-1]  % 65521
    A32= B *65536 + A
    return hex(A32)[2:]

# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main code
    mystring = 'Wikipedia'
    mycode = adler32(mystring)

    print('{0} --> {1}'.format(mystring, mycode))

# =============================================================================
# End of code
# =============================================================================
