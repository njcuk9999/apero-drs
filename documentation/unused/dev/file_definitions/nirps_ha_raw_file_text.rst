^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
1.2 APERO definition of TRG_TYPE
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TRG_TYPE may be in the header, in which case it is used.

If TRG_TYPE is not in header we assign it based on the following key:

* HIERARCH ESO DPR TYPE

Then TRG_TYPE is set as follows:

* If HIERARCH ESO DPR TYPE contains "SKY" then TRG_TYPE = 'SKY'
* If HIERARCH ESO DPR TYPE contains "OBJECT" or "STAR" then TRG_TYPE = 'TARGET'
* Else TRG_TYPE = ''
