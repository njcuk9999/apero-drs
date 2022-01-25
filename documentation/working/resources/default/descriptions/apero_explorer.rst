The apero_explorer recipe is designed as a graphical user interface (GUI) between the user and the
various databases that APERO uses. The script downloads a static copy of the SQL database,
changes are not updated or saved in real time (but can be updated/saved by selecting the
correct menu options).

Tables within the database currently accessible with the explorer are:

- calib: The calibration database
- tellu: The telluric database
- index: The file index database
- log: The logger database
- object: The object astrometric database
- lang: The text and language database

The GUI allows the user to:

- Do File operations:
    - Open a pickle file to replace the current database
    - Import a csv file to replace the current database
    - Save a pickle file of the current database
    - Export a csv file of the current database

- Edit the current database
    - Find and replace a string with another value
    - Filter rows by a certain criteria
    - Add rows and columns

- Table operations
    - refresh the current database (with updates since launching the GUI)
    - Save changes for the current database to the main database
    - Clean strings
    - Remove formatting
    - Get some information of the table formatting

.. note:: No changes will be saved unless you use the "Table>Save to Database" option

.. note:: We do not recommend changing any of the database entries without good reason
          and without talking to the developers

1.1 Some examples
^^^^^^^^^^^^^^^^^^^^^^

- Example 1: Copy all extracted 2D spectra, telluric corrected 2D spectra and telluric reconstructed absorption files for fiber AB for Gl699  to /home/test/apero-files/

    .. code-block::

        apero_get.py --outtypes EXT_E2DS_FF,TELLU_OBJ,TELLU_RECON --fibers=AB --outpath=/home/test/apero-files/ --objnames=Gl699



- Example 2: Copy all extracted (non-telluric corrected) 1D spectra files of WASP-127 to /home/test/apero-files/

    .. code-block::

        apero_get.py --outtype EXT_S1D_W,EXT_S1D_V,SC1D_W_FILE,SC1D_V_FILE --objnames=WASP-127 --outpath=/home/test/files/

- Example 3: Copy all telluric corrected 2D spectra fibers AB, A and B for targets Gl699, Trappist-1 and AuMic to /home/test/apero-files/


    .. code-block::

        apero_get.py --outtypes TELLU_OBJ --fibers=AB,A,B --outpath=/home/test/apero-files/ --objnames=Gl699,Trappist-1,AuMic


- Example 4: Copy all extracted 2D spectra for fiber AB of DPRTYPE=DARK_DARK_SKY (Sky files) to /home/test/apero-files/

    .. code-block::

        apero_get.py --outtypes EXT_E2DS_FF --fibers=AB --outpath=/home/test/apero-files/ --dprtypes=DARK_DARK_SKY

- Example 5: Copy all extracted 2D spectra for fibers AB and C of DPRTYPE=FP_FP (FP calibration files) to /home/test/apero-files/

    .. code-block::

        apero_get.py --outtypes EXT_E2DS_FF --fibers=AB,C --outpath=/home/test/apero-files/ --dprtypes=FP_FP

- Example 6: Copy all telluric corrected 2D spectra for fibers A and B for many objects to /home/test/apero-files/

    .. code-block::

        apero_get.py --outtypes TELLU_OBJ --fibers=A,B --outpath=/home/test/apero-files/ --objnames=EXLUP,V830TAU,BDP23_2063B,HD_96064_BC,G_272M127,J23453034P4104001,ROSS_1050,ROSS_477,TOI1759,G_75M55,TWA25,GL846,HD_207966B,J00372598P5133072,J23181789P4617214,TYC_4384M1735M1,V2247OPH,2MASSJ11021804P1630333,BDP04_4988,BDP08_4887,GJ494,GL270,GL338B,GL536,GL212,GL410,HD_263175B,NLTT46858,OTSER,BDP05_3409,GL412A,GL514,GJ3305,GJ1026A,LP_831M68,HD_154363B,HD_31867B,NLTT45473,GL205,GL686,GL880,WOLF_209,GL378,J20412815P5725473,DHTAUB,DOTAU,TWA13A,TWA13B,AUMIC,G_114M10,NLTT36190,HD_31412B,HD_46375B,LP_733M99,GJ3470,G_145M11,G_230M31,18_PUP_B,G_270M12,GJ3192A,HD_164595B,HD_50281B,L_657M32,NLTT39578,SIGCRBC,JH_223,GL411,XZTAU,GL15A,GL382,TWA7,V347AUR,HD_213519B,WOLF_1450,GL752A,G_270M164,G_28M21,GL687,GL48,GL617B,GJ1026B,ROSS_555,G_106M36,GL317,GL362,GL725B,GL849,GL876,HD_4271B,NLTT44569,NLTT45430,UCAC4_538M053123,V_CW_UMA,G240M52,GJ1105,GJ4333,GL15B,GL480,HD_6660B,PM_J08402P3127,G_275M2,J04510138P3127238,TYC_3980M1081M1,CEBOO,GL251,GL436,GL581,GL725A,PM_J09553M2715,EPIC_248131102,GJ768_1B,TOI732,EV_LAC,G_102M4,G_232M62,NLTT35712,GJ1148,GJ3378,GL169_1A,GL445,LP_128M32,NLTT40692,GJ4338,NLTT37349,GJ1103,GJ1214,GJ1256,GJ1289,GJ490B,GJ669B,GL166C,K2_25,GJ1151,GJ1154,GJ4274,GJ493_1,GJ4063,GL408,GL699,UCAC3_226M217434,GJ3789,HD_183870B,GL905,LP_071M082,PM_J18482P0741,GJ1286,GJ1002,G_139M12,GJ4071,PM_J21463P3813,20_LMI_B,GL412B,GJ3622,GJ1111,1RXSJ173353_5P165515,GJ1245B,TRAPPIST1,J1835379P325954,TVLM_513M46

