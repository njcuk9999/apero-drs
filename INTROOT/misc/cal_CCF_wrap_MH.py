from collections import OrderedDict
from astropy.table import Table

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouStartup

import cal_CCF_E2DS_FP_MH_spirou


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_CCF_E2DS_FP_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get the parameter dictionary class
ParamDict = spirouConfig.ParamDict
# Get Logging function
WLOG = spirouCore.wlog
# define the arguments for each run
# Note: MUST be one entry per run
NUMBER_RUNS = 12
NIGHT_NAMES = ['wavesol_allshape'] * NUMBER_RUNS
E2DSFILES = ['2375577o_pp_e2dsff_wave13_AB.fits',
             '2375577o_pp_e2dsff_wave14_AB.fits',
             '2375577o_pp_e2dsff_wave15_AB.fits',
             '2375577o_pp_e2dsff_wave16_AB.fits',
             '2375577o_pp_e2dsff_wave17_AB.fits',
             '2375577o_pp_e2dsff_wave18_AB.fits',
             '2375577o_pp_e2dsff_wave19_AB.fits',
             '2375577o_pp_e2dsff_wave21_AB.fits',
             '2375577o_pp_e2dsff_wave22_AB.fits',
             '2375577o_pp_e2dsff_wave23_AB.fits',
             '2375577o_pp_e2dsff_wave24_AB.fits',
             '2375577o_pp_e2dsff_wave25_AB.fits']
MASKS = ['gl581_Sep18_cleaned.mas'] * NUMBER_RUNS
RVS = [-76] * NUMBER_RUNS
WIDTHS = [30.0] * NUMBER_RUNS
STEPS = [0.5] * NUMBER_RUNS
WAVEFILES = ['/home/mhobson/SPIRou_data/reduced/wavesol_allshape/Melissa_2374832a_pp_2374836c_pp_wave_new_AB.fits',
'/home/mhobson/SPIRou_data/reduced/wavesol_allshape/Melissa_2375095a_pp_2375097c_pp_wave_new_AB.fits',
'/home/mhobson/SPIRou_data/reduced/wavesol_allshape/Melissa_2375121a_pp_2375125c_pp_wave_new_AB.fits',
'/home/mhobson/SPIRou_data/reduced/wavesol_allshape/Melissa_2375312a_pp_2375316c_pp_wave_new_AB.fits',
'/home/mhobson/SPIRou_data/reduced/wavesol_allshape/Melissa_2375473a_pp_2375475c_pp_wave_new_AB.fits',
'/home/mhobson/SPIRou_data/reduced/wavesol_allshape/Melissa_2375657a_pp_2375661c_pp_wave_new_AB.fits',
'/home/mhobson/SPIRou_data/reduced/wavesol_allshape/Melissa_2375687a_pp_2375691c_pp_wave_new_AB.fits',
'/home/mhobson/SPIRou_data/reduced/wavesol_allshape/Melissa_2375743a_pp_2375747c_pp_wave_new_AB.fits',
'/home/mhobson/SPIRou_data/reduced/wavesol_allshape/Melissa_2375771a_pp_2375775c_pp_wave_new_AB.fits',
'/home/mhobson/SPIRou_data/reduced/wavesol_allshape/Melissa_2375803a_pp_2375807c_pp_wave_new_AB.fits',
'/home/mhobson/SPIRou_data/reduced/wavesol_allshape/Melissa_2375831a_pp_2375835c_pp_wave_new_AB.fits',
'/home/mhobson/SPIRou_data/reduced/wavesol_allshape/Melissa_2376092a_pp_2376096c_pp_wave_new_AB.fits'
             ]
# define which variables to save from run
SAVE_VALUES_LOC = ['CONTRAST', 'RV', 'FWHM', 'MAXCPP', 'WAVEFILE']
SAVE_VALUES_CLOC = ['CONTRAST', 'RV', 'FWHM', 'MAXCPP', 'WAVEFILE']
SAVE_VALUES_CP = ['DRIFT0']
SAVE_VALUES_P = []
# define the output file
OUTPUTFILENAME = 'Gl411_cff_wavenew_allshape.fits'


# =============================================================================
# Define functions
# =============================================================================
def main():

    # check that variables = length of number of runs
    if len(NIGHT_NAMES) != NUMBER_RUNS:
        WLOG(None, 'error', 'NIGHT_NAMES is wrong length')
    if len(E2DSFILES) != NUMBER_RUNS:
        WLOG(None, 'error', 'E2DSFILES is wrong length')
    if len(MASKS) != NUMBER_RUNS:
        WLOG(None, 'error', 'MASKS is wrong length')
    if len(RVS) != NUMBER_RUNS:
        WLOG(None, 'error', 'RVS is wrong length')
    if len(WIDTHS) != NUMBER_RUNS:
        WLOG(None, 'error', 'WIDTHS is wrong length')
    if len(STEPS) != NUMBER_RUNS:
        WLOG(None, 'error', 'STEPS is wrong length')
    if len(WAVEFILES) != NUMBER_RUNS:
        WLOG(None, 'error', 'WAVEFILES is wrong length')

    # define storage
    storage = OrderedDict()
    errors = OrderedDict()

    # run the loop
    for it in range(NUMBER_RUNS):

        # get this iterations arguments
        args = [NIGHT_NAMES[it], E2DSFILES[it], MASKS[it],
                RVS[it], WIDTHS[it], STEPS[it], WAVEFILES[it]]
        # run main
        try:
            ll_it = cal_CCF_E2DS_FP_MH_spirou.main(*args)
        except SystemExit as e:
            errors[it] = e
            continue
        except Exception as e:
            errors[it] = e
            continue
        errors[it] = None

        # get p, loc, cp, cloc
        p, loc = ll_it['p'], ll_it['loc']
        cp, cloc = ll_it['cp'], ll_it['cloc']

        # get loc keys
        for key in SAVE_VALUES_LOC:
            save_key = 'loc_{0}'.format(key)

            if save_key not in storage:
                storage[save_key] = dict()
                storage[save_key] = [loc[key]]
            else:
                storage[save_key].append(loc[key])
        # get cloc keys
        for key in SAVE_VALUES_CLOC:
            save_key = 'cloc_{0}'.format(key)
            if save_key not in storage:
                storage[save_key] = dict()
                storage[save_key] = [cloc[key]]
            else:
                storage[save_key].append(cloc[key])
        # get cp keys
        for key in SAVE_VALUES_P:
            save_key = 'p_{0}'.format(key)
            if save_key not in storage:
                storage[save_key] = dict()
                storage[save_key] = [p[key]]
            else:
                storage[save_key].append(p[key])
        # get cp keys
        for key in SAVE_VALUES_CP:
            save_key = 'cp_{0}'.format(key)
            if save_key not in storage:
                storage[save_key] = dict()
                storage[save_key] = [cp[key]]
            else:
                storage[save_key].append(cp[key])

    # report errors
    WLOG(None, 'warning', '')
    WLOG(None, 'warning', '')
    WLOG(None, 'warning', ' ERROR REPORTING')
    WLOG(None, 'warning', '')
    WLOG(None, 'warning', '')

    for error in errors:
        if errors[error] is not None:
            WLOG(None, 'warning', str(errors[error]))

    # construct output table
    try:
        outtable = Table()
        for key in storage.keys():
            outtable[key] = storage[key]

        outtable.write(OUTPUTFILENAME, format='fits', overwrite=True)
    except Exception as e:
        emsgs = ['Error in writing table', 'Error {0}: {1}'.format(type(e), e)]
        WLOG(None, 'error', emsgs)



# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()


# =============================================================================
# End of code
# =============================================================================