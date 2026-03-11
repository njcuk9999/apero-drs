# CCF MASKS

Add any files here to use as masks.

Masks can be used in two ways.


1. CCF_DEFAULT_MASK = "TEFF"

    In this mode the masks are determined by TEFF in the header
    and which mask is used for which TEFF is controlled by CCF_TEFF_MASK_TABLE
    
    by default CCF_TEFF_MASK_TABLE = 'teff_mask.csv'


2. CCF_DEFAULT_MASK = filename

   Just uses this mask for all files



## CCF_TEFF_MASK_TABLE

This file must be a csv file

Columns are as follows:

mask: the filename of the mask

kind: 'default' or 'range'
      must have only one default column - this is used for cases where
      there is no Teff value or a Teff value is out of bounds
      all other value must be 'range'

datatype: 'fits', 'ascii'
      these are the only two type allowed - see below for format of the 
      mask files themselves

teff_min: 
      if kind is 'default' this column can be blank
      otherwise this is the minimum Teff allowed for this mask [in K]
      teff_min exactly is included in this Teff bracket

teff_max:
      if kind is 'default' this column can be blank
      otherwise this is the maximum Teff allowed for this mask [in K]
      teff_max exactly is excluded in this Tef bracket

## CCF file format

### fits files

fits binary table, must have at least the columns:
ll_mask_s: the start of the line in nm
ll_mask_e: the end of the line in nm
w_mask: the weight of each line

other columns will be ignored

### ascii files

must have no header value
must be separated by spaces
must have exactly three columns (ll_mask_s, ll_mask_e, w_mask) - see 
description of fits files

i.e.

      970.0717907416      970.0750243196        0.0275813427
      970.1473799456      970.1506137756        0.0323880938
      970.5622657625      970.5655009755        0.0389980926
      970.6149583983      970.6181937869        0.0200845833
      970.8330558432      970.8362919588        0.4554797947



