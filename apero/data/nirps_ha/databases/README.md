# Databases go in here

## Updating reset.calib.csv

Just edit the file - but make sure all fits file are placed in
`apero/data/reset/calibdb`

## Updating reset.object.csv database

Note this can be done from a raw directory or manually.


- For a manual list (i.e. from another location), use the following commands:

    ```bash
    dfits */*.fits | fitsort OBJECT RA_DEG DEC_DEG MJDEND OBJRV OBJTEMP > spirou_targets.txt
    
    apero_database.py --objdb=spirou_targets*.txt
    ```

    _Note if this is not for SPIROU one should replace the header keywords with
    the valid header keys for this instrument (i.e. `RA_DEG -> RA`)_


- or to update using the currently defined raw data:

    ```bash
    apero_database.py --objdb=True
    ```
