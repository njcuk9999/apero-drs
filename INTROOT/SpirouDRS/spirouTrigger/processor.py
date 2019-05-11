import pickle
from collections import namedtuple

from .drswrapper import DRS, FIBER_LIST, CcfParams
from .exposureconfig import TargetType, FiberType, CalibrationType
from .log import log
from .pathhandler import Exposure
from .productpackager import ProductPackager


class Steps(namedtuple('Steps', ('preprocess', 'calibrations', 'objects'))):
    @classmethod
    def all(cls):
        return cls(True, True, ObjectSteps.all())

    @classmethod
    def from_keys(cls, keys):
        return cls('preprocess' in keys, 'calibrations' in keys, ObjectSteps.from_keys(keys))


class ObjectSteps(namedtuple('ObjectSteps', ('extract', 'pol', 'mktellu', 'fittellu', 'ccf',
                                             'products', 'distribute', 'database'))):
    @classmethod
    def all(cls):
        return cls(True, True, True, True, True, True, True, True)

    @classmethod
    def from_keys(cls, keys):
        temp_dict = {field: field in keys for field in cls._fields}
        return cls(**temp_dict)


class Processor:
    def __init__(self, steps, trace, realtime, ccf_params=None):
        self.steps = steps
        self.trace = trace
        self.realtime = realtime
        self.drs = DRS(trace)
        self.packager = ProductPackager(trace, steps.objects.products)
        self.calibration_processor = CalibrationProcessor(self.steps, self.drs)
        self.object_processor = ObjectProcessor(self.steps, self.drs, self.packager, ccf_params)

    def preprocess_exposure(self, exposure):
        if self.steps.preprocess:
            return self.drs.cal_preprocess(exposure)
        else:
            return exposure.preprocessed.exists()

    def process_exposure(self, config, exposure):
        if config.object:
            return self.object_processor.process_object_exposure(config, exposure)

    def process_sequence(self, config, exposures):
        if config.calibration:
            calibration = config.calibration
            if calibration == CalibrationType.DARK_DARK:
                return self.calibration_processor.dark(exposures)
            elif calibration == CalibrationType.DARK_FLAT:
                return self.calibration_processor.dark_flat(exposures)
            elif calibration == CalibrationType.FLAT_DARK:
                return self.calibration_processor.flat_dark(exposures)
            elif calibration == CalibrationType.FLAT_FLAT:
                return self.calibration_processor.flat(exposures)
            elif calibration == CalibrationType.FP_FP:
                return self.calibration_processor.fabry_perot(exposures)
            elif calibration == CalibrationType.HCONE_HCONE:
                return self.calibration_processor.hc_one(exposures)
        elif config.object.instrument_mode.is_polarimetry():
            return self.object_processor.process_polar_seqeunce(exposures)


class ObjectProcessor():
    def __init__(self, steps, drs, packger, ccf_params=None):
        self.steps = steps
        self.drs = drs
        self.packager = packger
        self.ccf_params = ccf_params
        if self.ccf_params is None:
            self.ccf_params = CcfParams('masque_sept18_andres_trans50.mas', 0, 200, 1)

    def process_object_exposure(self, config, exposure):
        extracted_path = self.extract_object(exposure)
        if config.object.target == TargetType.STAR:
            is_telluric_corrected = self.telluric_correction(exposure)
            is_obj_fp = config.object.reference_fiber == FiberType.FP
            ccf_path = self.ccf(exposure, is_telluric_corrected, is_obj_fp)
            return {
                'extracted_path': extracted_path,
                'ccf_path': ccf_path,
                'is_ccf_calculated': True,
                'is_telluric_corrected': is_telluric_corrected,
            }
        else:
            if config.object.target == TargetType.TELLURIC_STANDARD:
                # TODO: need to update this to work with new creation model
                pass
                # if self.steps.objects.mktellu:
                #     self.drs.obj_mk_tellu(exposure)
        return {'extracted_path': extracted_path}

    def process_polar_seqeunce(self, exposures):
        if len(exposures) < 2:
            return {'is_polar_done': False}
        if self.steps.objects.pol:
            self.drs.pol(exposures)
        if self.steps.objects.products:
            self.packager.create_pol_product(exposures[0])
        return {'is_polar_done': True}

    def extract_object(self, exposure):
        if self.steps.objects.extract:
            self.drs.cal_extract_RAW(exposure)
        if self.steps.objects.products:
            self.packager.create_spec_product(exposure)
        return exposure.e2ds('AB')

    def telluric_correction(self, exposure):
        if self.steps.objects.fittellu:
            try:
                result = self.drs.obj_fit_tellu(exposure)
                telluric_corrected = bool(result)
            except:
                telluric_corrected = False
        else:
            expected_telluric_path = exposure.e2ds('AB', telluric_corrected=True, flat_fielded=True)
            telluric_corrected = expected_telluric_path.exists()
        if self.steps.objects.products:
            self.packager.create_tell_product(exposure)
        return telluric_corrected

    def ccf(self, exposure, telluric_corrected, fp):
        if self.steps.objects.ccf:
            self.drs.cal_CCF_E2DS(exposure, self.ccf_params, telluric_corrected, fp)
        mask = self.ccf_params.mask
        if self.steps.objects.products:
            self.packager.create_ccf_product(exposure, mask, telluric_corrected=telluric_corrected, fp=fp)
        return exposure.ccf('AB', mask, telluric_corrected=telluric_corrected, fp=fp)


class ExposureAndSequenceCache():
    CACHE_FILE = '.drstrigger.cache'

    def __init__(self):
        self.__load_cache()

    def set_last_exposure(self, exposure, calibration_type):
        self._set_cached_exposure(exposure, self._last_key(calibration_type))

    def get_last_exposure(self, night, calibration_type):
        return self._get_cached_exposure(night, self._last_key(calibration_type))

    def set_queued_sequence(self, exposures, calibration_type):
        self._set_cached_sequence(exposures, self._queue_key(calibration_type))

    def get_queued_sequence(self, night, calibration_type):
        return self._get_cached_sequence(night, self._queue_key(calibration_type))

    def _set_cached_exposure(self, exposure, key):
        self.__trigger_cache[key] = exposure.raw.name
        self.__save_cache()

    def _get_cached_exposure(self, night, key):
        return Exposure(night, self.__trigger_cache[key])

    def _set_cached_sequence(self, exposures, key):
        self.__trigger_cache[key] = [exposure.raw.name for exposure in exposures]
        self.__save_cache()

    def _get_cached_sequence(self, night, key):
        return [Exposure(night, filename) for filename in self.__trigger_cache[key]]

    @staticmethod
    def _queue_key(calibration_type):
        return calibration_type.to_dpr_type() + '_QUEUE'

    @staticmethod
    def _last_key(calibration_type):
        return 'LAST_' + calibration_type.to_dpr_type()

    def __save_cache(self):
        try:
            pickle.dump(self.__trigger_cache, open(self.CACHE_FILE, 'wb'))
        except (OSError, IOError) as e:
            log.error('Failed to serialize trigger cache, this will probably cause errors later on')

    def __load_cache(self):
        try:
            self.__trigger_cache = pickle.load(open(self.CACHE_FILE, 'rb'))
        except (OSError, IOError):
            self.__trigger_cache = {}


class CalibrationProcessor():
    def __init__(self, steps, drs):
        super().__init__()
        self.steps = steps
        self.drs = drs
        self.cache = ExposureAndSequenceCache()

    def dark(self, exposures):
        if self.steps.calibrations:
            result = self.drs.cal_DARK(exposures)
            last_dark = exposures[-1]
            self.cache.set_last_exposure(last_dark, CalibrationType.DARK_DARK)
            return result

    def dark_flat(self, exposures):
        if self.steps.calibrations:
            self.cache.set_queued_sequence(exposures, CalibrationType.DARK_FLAT)

    def flat_dark(self, exposures):
        if self.steps.calibrations:
            self.cache.set_queued_sequence(exposures, CalibrationType.FLAT_DARK)

    def flat(self, exposures):
        if self.steps.calibrations:
            self.cache.set_queued_sequence(exposures, CalibrationType.FLAT_FLAT)
            # Generate bad pixel mask using last flat and last dark
            last_flat = exposures[-1]
            night = last_flat.night
            last_dark = self.cache.get_last_exposure(night, CalibrationType.DARK_DARK)
            assert last_dark is not None, 'Need a known DARK file for cal_BADPIX'
            self.drs.cal_BADPIX(last_flat, last_dark)
            # Process remaining loc queues
            self.__process_cached_loc_queue(night, CalibrationType.DARK_FLAT)
            self.__process_cached_loc_queue(night, CalibrationType.FLAT_DARK)

    def __process_cached_loc_queue(self, night, calibration_type):
        exposures = self.cache.get_queued_sequence(night, calibration_type)
        if exposures:
            self.drs.cal_loc_RAW(exposures)
            self.cache.set_queued_sequence([], calibration_type)
        return exposures

    def __process_cached_flat_queue(self, night):
        if self.steps.calibrations:
            flat_exposures = self.cache.get_queued_sequence(night, CalibrationType.FLAT_FLAT)
            if flat_exposures:
                self.drs.cal_FF_RAW(flat_exposures)
                self.cache.set_queued_sequence([], CalibrationType.FLAT_FLAT)
                return flat_exposures

    def fabry_perot(self, exposures):
        if self.steps.calibrations:
            self.cache.set_queued_sequence(exposures, CalibrationType.FP_FP)

    def __process_cached_fp_queue(self, hc_exposure):
        if self.steps.calibrations:
            fp_exposures = self.cache.get_queued_sequence(hc_exposure.night, CalibrationType.FP_FP)
            if fp_exposures:
                self.drs.cal_SLIT(fp_exposures)
                self.drs.cal_SHAPE(hc_exposure, fp_exposures)
                self.__process_cached_flat_queue(fp_exposures[0].night)  # Can finally flat field once we have the tilt
                # for fp_exposure in fp_exposures:
                #     self.drs.cal_extract_RAW(fp_exposure)
                self.drs.cal_extract_RAW(fp_exposures[-1])
                self.cache.set_queued_sequence([], CalibrationType.FP_FP)
            return fp_exposures

    def hc_one(self, exposures):
        if self.steps.calibrations:
            last_hc = exposures[-1]
            fp_exposures = self.__process_cached_fp_queue(last_hc)
            if fp_exposures:
                last_fp = fp_exposures[-1]
                self.drs.cal_extract_RAW(last_hc)
                self.__wave(last_hc, last_fp)

    def __wave(self, hc_exposure, fp_exposure):
        if self.steps.calibrations:
            assert fp_exposure is not None, 'Need an extracted FP file for cal_WAVE'
            for fiber in FIBER_LIST:
                self.drs.cal_HC_E2DS(hc_exposure, fiber)
                self.drs.cal_WAVE_E2DS(fp_exposure, hc_exposure, fiber)
