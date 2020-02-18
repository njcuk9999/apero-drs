********************************************************************************
Required Input Header Keys
********************************************************************************

-------------------------------------------------------------------------------
Main
-------------------------------------------------------------------------------

.. code-block::

    OBSTYPE = 'OBJECT  '           / Observation / Exposure type ['DARK', 'FLAT', 'ALIGN', 'COMPARISON', 'OBJECT']
    TRG_TYPE= 'TARGET  '           / target or sky object ['TARGET', 'SKY', '']
    OBJECT = 'HD159170'            / Target name
    OBJNAME = 'HD159170'           / Target name   [DUPLICATE, should not be used any more use 'OBJECT']

object specific parameters

.. code-block::

    OBJRA   = '17:33:29.84'        / Target right ascension [HH:MM:SS.SSSS]
    OBJDEC  = '-5:44:41.3'         / Target declination [DD:MM:SS.SSSS]
    OBJEQUIN=               2000.0 / Target equinox
    OBJRAPM =                 0.00 / Target right ascension proper motion in as/yr
    OBJDECPM=                 0.00 / Target declination proper motion in as/yr
    OBJTEMP =              9900.00 / Object effective temperature [K]
    GAIA_ID =  1958476259155515008 / The Gaia ID used for BERV params  [OPTIONAL BUT RECOMMENDED]
    OBJPLX  =    12.22203034418218 / PLX [mas] used to calc. BERV [OPTIONAL BUT RECOMMENDED]
    OBSRV   =                  0.0 / RV [km/s] used to calc. BERV [OPTIONAL BUT RECOMMENDED]

    AIRMASS =                1.151 / Airmass at start of observation
    PI_NAME = 'QSO Team'
    GAIN    =                0.999 / Amplifier gain (electrons/ADU)
    RDNOISE =                 10.9 / Read noise (electrons)
    FRMTIME =              5.57192 / [sec] Frame time, cadence of IR reads
    EXPTIME =              300.884 / [sec] Integration time
    SATURATE=                60000 / Saturation value (ADU)

Used to figure out what sequence files should be processed in:

.. code-block::

    CMPLTEXP=                    1 / Exposure number within the exposure sequence
    NEXP    =                    1 / Total number of exposures within the sequence

Date:

.. code-block::

    MJDATE  =        58593.5428846 / Modified Julian Date at start of observation   [ONLY USED VISUALLY]
    MJDEND  =        58593.5467937 / Modified Julian Date at end of observation
    DATE-OBS= '2019-04-20'         / Date at start of observation (UTC) [YYYY-MM-DD]   [ONLY USED VISUALLY]
    UTC-OBS = '13:01:45.23'        / Time at start of observation (UTC) [HH:MM:SS.SS]   [ONLY USED VISUALLY]


Used to know what position fibers/wheel where in:

.. code-block::

    SBCREF_P= 'pos_pk  '           / SPIRou Reference Fiber Position (predefined)
    SBCCAS_P= 'pos_pk  '           / SPIRou Cassegrain Fiber Position (predefined)
    SBCDEN_P=                 1.96 / SPIRou Calib-Reference density (0 to 3.3)  [ONLY USED FOR LOGGING?]
    SBCALI_P= 'P5      '           / SPIRou calibwh predefined position or angle

-------------------------------------------------------------------------------
Other
-------------------------------------------------------------------------------

Used to report the air temperature [used in dark master -- logging only?]:

.. code-block::

    TEMPERAT=                 2.33 / 86 temp, air, weather tower deg C

Used to report the cassigrain temperature [used in dark master -- logging only?]:

.. code-block::

    SB_POL_T=                 4.03 / SPIRou tpolar temp at start of exp (deg C

used in dark master -- logging only?:

.. code-block::

    RELHUMID=                 6.48 / 87 relative humidity, weather tower %