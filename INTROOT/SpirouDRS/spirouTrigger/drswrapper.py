import sys
from collections import namedtuple

import cal_BADPIX_spirou
import cal_CCF_E2DS_FP_spirou
import cal_CCF_E2DS_spirou
import cal_DARK_spirou
import cal_FF_RAW_spirou
import cal_HC_E2DS_EA_spirou
import cal_SHAPE_spirou
import cal_SLIT_spirou
import cal_WAVE_E2DS_EA_spirou
import cal_extract_RAW_spirou
import cal_loc_RAW_spirou
import cal_preprocess_spirou
import obj_fit_tellu
import pol_spirou

from .log import log
from .utilmisc import flatten

CcfParams = namedtuple('CcfParams', ('mask', 'v0', 'range', 'step'))

FIBER_LIST = ('AB', 'A', 'B', 'C')


# Exception representing any failure for a DRS recipe
class RecipeFailure(Exception):
    def __init__(self, reason, command_string):
        self.reason = reason
        self.command_string = command_string

    def __str__(self):
        return 'DRS command failed (' + self.reason + '): ' + self.command_string


class DRS:
    def __init__(self, trace=False, log_command=True):
        self.trace = trace
        self.log_command = log_command

    def cal_preprocess(self, exposure):
        return self.__logwrapper(cal_preprocess_spirou, exposure.night, exposure.raw.name)

    def cal_extract_RAW(self, exposure):
        return self.__logwrapper(cal_extract_RAW_spirou, exposure.night, exposure.preprocessed.name)

    def cal_DARK(self, exposures):
        return self.__sequence_logwrapper(cal_DARK_spirou, exposures)

    def cal_BADPIX(self, flat_exposure, dark_exposure):
        flat_file = flat_exposure.preprocessed.name
        dark_file = dark_exposure.preprocessed.name
        return self.__logwrapper(cal_BADPIX_spirou, flat_exposure.night, flat_file, dark_file)

    def cal_loc_RAW(self, exposures):
        return self.__sequence_logwrapper(cal_loc_RAW_spirou, exposures)

    def cal_FF_RAW(self, exposures):
        return self.__sequence_logwrapper(cal_FF_RAW_spirou, exposures)

    def cal_SLIT(self, exposures):
        return self.__sequence_logwrapper(cal_SLIT_spirou, exposures)

    def cal_SHAPE(self, hc_exposure, fp_exposures):
        night = hc_exposure.night
        hc_file = hc_exposure.preprocessed.name
        fp_files = [fp_exposure.preprocessed.name for fp_exposure in fp_exposures]
        return self.__logwrapper(cal_SHAPE_spirou, night, hc_file, fp_files)

    def cal_HC_E2DS(self, exposure, fiber):
        file = exposure.e2ds(fiber).name
        return self.__logwrapper(cal_HC_E2DS_EA_spirou, exposure.night, file)

    def cal_WAVE_E2DS(self, fp_exposure, hc_exposure, fiber):
        hc_file = hc_exposure.e2ds(fiber).name
        fp_file = fp_exposure.e2ds(fiber).name
        return self.__logwrapper(cal_WAVE_E2DS_EA_spirou, hc_exposure.night, fp_file, [hc_file])

    def cal_CCF_E2DS(self, exposure, params, telluric_corrected, fp):
        file = exposure.e2ds('AB', telluric_corrected, flat_fielded=True).name
        ccf_recipe = cal_CCF_E2DS_FP_spirou if fp else cal_CCF_E2DS_spirou
        return self.__logwrapper(ccf_recipe, exposure.night, file, params.mask, params.v0, params.range, params.step)

    def pol(self, exposures):
        input_files = [exposure.e2ds(fiber).name for exposure in exposures for fiber in ('A', 'B')]
        return self.__logwrapper(pol_spirou, exposures[0].night, input_files)

    # TODO: need to update this to work with new creation model
    # def obj_mk_tellu(self, exposure):
    #     return self.__logwrapper(obj_mk_tellu, exposure.night, [exposure.e2ds('AB', flat_fielded=True).name])

    def obj_fit_tellu(self, exposure):
        return self.__logwrapper(obj_fit_tellu, exposure.night, [exposure.e2ds('AB', flat_fielded=True).name])

    # Exception type internally used to represent a quality control failure for a DRS recipe
    class __QCFailure(Exception):
        def __init__(self, errors):
            super().__init__('QC failure: ' + ', '.join(errors))
            self.errors = errors

    def __logwrapper(self, module, night, *args):
        # Get a string representation of the command, ideally matching what the command line call would be
        command_string = ' '.join((module.__NAME__, night, *map(str, flatten(args))))
        if self.log_command:
            log.info(command_string)
        try:
            return self.__run(module, night, *args)
        except SystemExit:
            failure = RecipeFailure('system exit', command_string)
            log.error(failure)
            raise failure
        except DRS.__QCFailure:
            failure = RecipeFailure('QC failure', command_string)
            log.error(failure)
            raise failure
        except Exception:
            failure = RecipeFailure('uncaught exception', command_string)
            log.error(failure, exc_info=True)
            raise failure

    def __sequence_logwrapper(self, module, exposures):
        return self.__logwrapper(module, exposures[0].night, [exposure.preprocessed.name for exposure in exposures])

    def __run(self, module, night, *args):
        if self.trace:
            return True
        else:
            sys.argv = [sys.argv[0]]  # Wipe out argv so DRS doesn't rely on CLI arguments instead of what is passed in
            locals = module.main(night, *args)
            qc_passed = locals.get('passed')
            qc_failures = locals.get('fail_msg')
            if qc_failures and not qc_passed:
                raise DRS.__QCFailure(qc_failures)
            return True
