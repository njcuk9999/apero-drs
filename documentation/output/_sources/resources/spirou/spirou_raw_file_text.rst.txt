^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
1.2 APERO definition of DRSMODE
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For "DRSMODE" we use the following header keys

 * SBRHB1_P
 * SBRHB2_P

 and DRSMODE is defined as following:

+---------------+------------------------+------------------------+
|   DRSMODE     |      SBRHB1_P          |      SBRHB2_P          |
+===============+========================+========================+
| SPECTROSCOPY  | P16                    | P16                    |
+---------------+------------------------+------------------------+
| POLAR         | P2 or P4 or P14 or P16 | P2 or P4 or P14 or P16 |
+---------------+------------------------+------------------------+
| UNKNOWN       | anything else          | anything else          |
+---------------+------------------------+------------------------+

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
1.3 APERO definition of TRG_TYPE
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TRG_TYPE may be in the header, in which case it is used.

If TRG_TYPE is not in header we assign it based on the following keys:

* OBSTYPE
* OBJECT
* OBJNAME

Then TRG_TYPE is set as follows:

* If OBSTYPE is not "OBJECT" then TRG_TYPE = ''
* If OBSTYPE is "OBJECT" and "SKY" in OBJECT or OBJNAME then TRG_TYPE = 'SKY'
* else if OBSTYPE is "OBJECT" then TRG_TYPE = 'TARGET'
