The apero_get recipe is a quick and efficient way of copying (or linking to) data from the
main data directories of apero.

apero_get allow the user to select a specific file or files based on:

- object name: (using the --objnames argument), this select only files with
  the given object name (Can use the * to get all objects in separate directories)

- output file type: (using the --outtypes argument), this selects only files
  with the given output (see file definitions, i.e. :ref:`file definitions for SPIROU <spirou_file_def>`)
  (the name column) for the specific values for each file

- data types (using the --dprtypes argument), this similarly to output file type
  relates to the input file type (see pre-processing file definitions, i.e. :ref:`file definitions for SPIROU <spirou_pp_file>`)
  (the HDR[DPRTYPE] column) for the specific values for each file

- fibers - the fibers to use (i.e. for spirou some combination of AB, A, B, C)

The user can also set the output directory where files should be copied to and
whether the copied files are just symlinks or full copies of the data.

.. note:: We recommend running with --test the first time this is used to make
          sure you have the files you want (and check whether all the options worked)

The apero_get recipe also allows quick copying of the full raw data set (or symlinks) this is useful when doing a full
reduction and wanting a consistent dataset (where a normal raw directory may be getting new files every day)

   .. code-block::

       apero_get.py --raw --symlink --outpath /home/test/apero-files/raw/


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


- Example 6: Copy all science observations for extracted 2D spectra.
             Note SPIROU does not use OBJ_SKY and NIRPS does not use POL_FP,POL_DARK but this command covers both instruments.
             Warning this may copy a LOT of objects. Run with --test first!

    .. code-block::

        apero_get.py --objnames=* --outtypes=EXT_E2DS_FF --outpath=/spirou/cook/test --dprtypes=OBJ_FP,OBJ_DARK,OBJ_SKY,POLAR_FP,POL_DARK



- Example 7: Copy all telluric corrected 2D spectra for fibers A and B for many objects to /home/test/apero-files/

    .. code-block::

        apero_get.py --outtypes TELLU_OBJ --fibers=A,B --outpath=/home/test/apero-files/ --objnames=EXLUP,V830TAU,BDP23_2063B,HD_96064_BC,G_272M127,J23453034P4104001,ROSS_1050,ROSS_477,TOI1759,G_75M55,TWA25,GL846,HD_207966B,J00372598P5133072,J23181789P4617214,TYC_4384M1735M1,V2247OPH,2MASSJ11021804P1630333,BDP04_4988,BDP08_4887,GJ494,GL270,GL338B,GL536,GL212,GL410,HD_263175B,NLTT46858,OTSER,BDP05_3409,GL412A,GL514,GJ3305,GJ1026A,LP_831M68,HD_154363B,HD_31867B,NLTT45473,GL205,GL686,GL880,WOLF_209,GL378,J20412815P5725473,DHTAUB,DOTAU,TWA13A,TWA13B,AUMIC,G_114M10,NLTT36190,HD_31412B,HD_46375B,LP_733M99,GJ3470,G_145M11,G_230M31,18_PUP_B,G_270M12,GJ3192A,HD_164595B,HD_50281B,L_657M32,NLTT39578,SIGCRBC,JH_223,GL411,XZTAU,GL15A,GL382,TWA7,V347AUR,HD_213519B,WOLF_1450,GL752A,G_270M164,G_28M21,GL687,GL48,GL617B,GJ1026B,ROSS_555,G_106M36,GL317,GL362,GL725B,GL849,GL876,HD_4271B,NLTT44569,NLTT45430,UCAC4_538M053123,V_CW_UMA,G240M52,GJ1105,GJ4333,GL15B,GL480,HD_6660B,PM_J08402P3127,G_275M2,J04510138P3127238,TYC_3980M1081M1,CEBOO,GL251,GL436,GL581,GL725A,PM_J09553M2715,EPIC_248131102,GJ768_1B,TOI732,EV_LAC,G_102M4,G_232M62,NLTT35712,GJ1148,GJ3378,GL169_1A,GL445,LP_128M32,NLTT40692,GJ4338,NLTT37349,GJ1103,GJ1214,GJ1256,GJ1289,GJ490B,GJ669B,GL166C,K2_25,GJ1151,GJ1154,GJ4274,GJ493_1,GJ4063,GL408,GL699,UCAC3_226M217434,GJ3789,HD_183870B,GL905,LP_071M082,PM_J18482P0741,GJ1286,GJ1002,G_139M12,GJ4071,PM_J21463P3813,20_LMI_B,GL412B,GJ3622,GJ1111,1RXSJ173353_5P165515,GJ1245B,TRAPPIST1,J1835379P325954,TVLM_513M46

- Example 8: For LBL copy these files (or change the objnames as appropriate)

    .. code-block::

        apero_get.py --outpath /space/spirou/obj_fullv07254 --outtypes TELLU_OBJ,TELLU_PCLEAN,TELLU_RECON,TELLU_TEMP_S1D,TELLU_TEMP,EXT_E2DS_FF --objnames GJ4071,GJ4338,DHTAUB,GL686,K2_25,18_PUP_B,1RXSJ173353_5P165515,20_LMI_B,42_PEG,51_PEG,55CNCB,72_OPH,AUMIC,BDP04_4988,BDP05_3409,BDP08_4887,BDP23_2063B,BPTAU,CITAU,DGTAU,DOTAU,2MASS_J04372171P2651014,EV_LAC,EXLUP,FUORI,G240M52,GJ1002,GJ1012,GJ1026A,GJ1026B,GJ1103,GJ1105,GJ1111,GJ1148,GJ1151,GJ1154,GJ1214,GJ1245B,GJ1256,GJ1286,GJ1289,GJ3192A,GJ3305,GJ3378,GJ3470,GJ3622,GJ3789,GJ4063,GJ4274,GJ4333,GJ490B,GJ493_1,GJ494,GJ669B,GJ768_1B,GL15A,GL15B,GL166C,GL169_1A,GL205,GL212,GL251,GL270,GL317,GL338B,GL362,GL378,GL382,GL388,GL406,GL408,GL410,GL411,GL412A,GL412B,GL436,GL445,GL447,GL48,GL480,GL514,GL536,GL581,GL617B,GL687,GL699,GL725A,GL725B,GL752A,GL846,GL849,GL876,GL880,GL905,GMAUR,GQLUP,G_102M4,G_106M36,G_114M10,G_145M11,G_230M31,G_232M62,G_270M12,G_270M164,G_272M127,G_275M2,G_28M21,G_75M55,HATP11,HD_189733,HD_133112,HD_154363B,HD_164595B,HD_183870B,HD_185603,HD_207966B,HD_213519B,HD_263175B,HD_31412B,HD_31867B,HD_4271B,HD_46375B,HD_50281B,HD_6660B,HD_96064_BC,J00372598P5133072,J04510138P3127238,J20412815P5725473,J23181789P4617214,J23453034P4104001,JH_223,K2_33,LKCA4,LP_071M082,LP_128M32,LP_733M99,LP_831M68,L_657M32,NLTT35712,NLTT36190,NLTT37349,NLTT39578,NLTT40692,NLTT44569,NLTT45430,NLTT45473,NLTT46858,PM_J08402P3127,PM_J09553M2715,PM_J18482P0741,PM_J21463P3813,ROSS_1050,ROSS_477,ROSS_555,RULUP,RYLUP,RYTAU,SIGCRBC,TAUBOO,TOI1728,TOI1759,TOI2136,TOI732,TOI1452,TOI1695,TOI442,TOI736,TRAPPIST1,TVLM_513M46,TWA13A,TWA13B,TWA25,TWA7,TW_HYA,TYC_3980M1081M1,TYC_3154M921M1,TYC_4384M1735M1,UCAC3_226M217434,UCAC4_538M053123,V1298TAU,V2129OPH,V2247OPH,V347AUR,V410TAU,V830TAU,WASP127,WASP69,WASP80,WASP11,WASP52,WASP12,WOLF_1450,WOLF_209,XZTAU,TOI727,TOI4860,SKY,WASP33,BDM11_2741,UCAC2_44133324,WASP39

        apero_get.py --outpath /space/spirou/obj_fullv07254 --dprtypes FP_FP --outtypes EXT_E2DS_FF

