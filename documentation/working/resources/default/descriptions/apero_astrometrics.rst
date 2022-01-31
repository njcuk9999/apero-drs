The apero astrometrics recipe allows one to add an object or a set of objects
to the astrometrics database (pending list) - to allow APERO to get the best
possible coordinates, proper motions and parallax as possible.

The online database `can be view here<https://docs.google.com/spreadsheets/d/1dOogfEwC7wAagjVFdouB1Y1JdF9Eva4uDW6CTZ8x2FM/edit?usp=sharing>`_ (but not edited).

The first thing that is checked is whether the object (or one of its aliases)
exists in the database. If it does the code skips this objects.

.. note:: An object can be forced to be updated with the --overwrite command.
          This is only recommended if an object currently in the astrometric
          database is deemed to be suspicious.


Once an object has been found not to be present currently in the database the
user is asked whether they with to add the object to the database.

The apero astrometrics recipe then cross-matches the name against SIMBAD, and
tries to update the astrometrics with the best possible proper motions (see
section 1.1 below) it then produces a print out to the screen similar to the
following:

.. code-block::

    ==================================================
        {CLEAN_OBJ_NAME} [{ORIGINAL_OBJ_NAME}]
     ==================================================
        Aliases:
             - {ALIASES}


        RA:    {RA}             ({COORD_SOURCE})
        DEC:   {DEC}            ({COORD_SOURCE})
        PMRA:  {PMRA} mas/yr    ({PM_SOURCE})
        PMDE:  {PMDE} mas/yr    ({PM_SOURCE})
        PLX:   {PLX} mas        ({PLX_SOURCE})
        RV:    {RV} km/s        ({RV_SOURCE})
        SPT:   {SPT}            ({SPT_SOURCE})
        EPOCH: {EPOCH}
        Jmag: {JMAG}
        Hmag: {HMAG}
        Kmag: {KMAG}
     ==================================================


where:

 - "CLEAN_OBJ_NAME" is a cleaned version of the name (capitalized, white spaces
   and puntucation removed) used throughout APERO.
 - "ORIGINAL_OBJ_NAME" is the name input by the user
 - "ALIASES" are SIMBAD (or otherwise) other names that should and can be used
   for this target (any with cleaned versions of these will use the "CLEAN_OBJ_NAME"
   throughout APERO.
 - "RA"/"DEC" and the "COORD_SOURCE" are the Right ascension, declination and
   where they come from.
   .. note:: "COORD_SOURCE" should match "PM_SOURCE" (see section 1.1 below)
 - "PMRA/PMDE" and the "PM_SOURCE" are the proper motions and where they come from
   .. note:: "COORD_SOURCE" should match "PM_SOURCE" (see section 1.1 below)
- "RV" and "RV_SOURCE" are the radial velocity and where it comes from -- if available
  (normally a bib code reference)
- "SPT" and "SPT_SOURCE" are the spectral type and source -- if available
  (normally a bib code reference)
- EPOCH is the JD time of the coordinates and proper motion (see section 1.1 below)
- "Jmag", "Hmag" and "Kmag" are the J/H and K magnitudes from SIMBAD

.. warning:: You must must check these parameters carefully as this will
             define these parameters will define this observation throughout APERO.
             The must describe the astrophysical object for which you are naming.
             If they are not correct DO NOT add this object.



1.1 SIMBAD, coordinates and proper motions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Crossmatching an object name with SIMBAD is a great way to find the correct
astrophysical object against a list of aliases and a large database of
coordinates, motions and distances. However the coordinates given by
SIMBAD are at 2000.0 but the proper motions are not. Therefore we only
use SIMBAD to get a list of aliases for a certain astrophysical object and
check against a few proper motion catalogues (matching to the ID from SIMBAD)
to get coordinates that match the proper motion epoch.

For example:

Gl699 has the following aliases (from SIMBAD):

- BD+04  3561a
- AC2000  146626
- ASCC 1153178
- CCDM J17578+0441A
- Ci 20 1069
- CSI+04-17554
- CSV   7737
- 1E 1755.3+0438
- GAT   12
- GCRV 10392
- GEN# +0.00403561
- G 140-24
- GJ   699
- GSC 00425-00184
- GSC 00425-02502
- HIC  87937
- HIP  87937
- IRAS 17553+0438
- JP11    18
- Karmn J17578+046
- LFT 1385
- LHS    57
- LSPM J1757+0441
- LTT 15309
- 2MASS J17574849+0441405
- MCC 799
- NAME Barnard's star
- NAME Barnard Star
- NLTT 45718
- NSV  9910
- 8pc 549.01
- PLX 4098
- PLX 4098.00
- PM J17578+0441N
- StKM 2-1355
- TIC 325554331
- TYC  425-2502-1
- UBV   15269
- UCAC2  33428712
- UCAC4 474-068224
- USNO-B1.0 0946-00315199
- USNO 347
- USNO 876
- uvby98 000403561
- V* V2500 Oph
- VVO   6
- WEB 14849
- WISEA J175747.94+044323.8
- Zkh 269
- [RHG95]  2849
- Gaia EDR3 4472832130942575872
- Gaia DR2 4472832130942575872


From this we find Gaia EDR3, Gaia DR2, UAC4 and HIP ids. We then cross match
against these proper motion catalogues and obtain coordinates (ra and dec) that
match the same epoch (i.e. for Gaia DR2 2015.5). We only match enough catalogues
to provide one set of none-null coordaintes and proper motions.

Currently the order of priority with proper motion catalogues is as follows:

- Gaia EDR3
- Gaia DR2
- UCAC4
- HIP

If a astrophysical object does not have an alias in any of these catalogues
we return a warning and skip this target.

Once all targets have been matched (or skipped) the online database is updated
(in the pending list) waiting the verification of administrators.

.. note:: that if a astrophyiscal object is in the pending list but not in the
          main list it will be used in APERO by default (assuming users allow updates
          from the database). If an astrophyiscal object is both in the main and pending
          lists, the pending list entry will NOT be used. The main list will be
          updated at specific times deemed by the administrators (to minimize
          inconsistencies between large redictions whereby changing a targets astrometrics
          could induce differences between unreduced and already reduced observations).

