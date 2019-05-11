from enum import Enum

from .constants import TELLURIC_STANDARDS
from .headerchecker import HeaderChecker
from .log import log


class FiberType(Enum):
    DARK = 'DARK'
    FLAT = 'FLAT'
    FP = 'FP'
    HCONE = 'HCONE'
    OBJ = 'OBJ'

    @staticmethod
    def from_dpr_type(dpr_type):
        science, reference = dpr_type.split('_', 1)
        return FiberType(science), FiberType(reference)

    @staticmethod
    def to_dpr_type(science, reference):
        return science.value + '_' + reference.value


class CalibrationType(Enum):
    DARK_DARK = (FiberType.DARK, FiberType.DARK)
    DARK_FLAT = (FiberType.DARK, FiberType.FLAT)
    FLAT_DARK = (FiberType.FLAT, FiberType.DARK)
    FLAT_FLAT = (FiberType.FLAT, FiberType.FLAT)
    FP_FP = (FiberType.FP, FiberType.FP)
    HCONE_HCONE = (FiberType.HCONE, FiberType.HCONE)
    FP_HCONE = (FiberType.FP, FiberType.HCONE)
    HCONE_FP = (FiberType.HCONE, FiberType.FP)

    @classmethod
    def from_dpr_type(cls, dpr_type):
        return CalibrationType(FiberType.from_dpr_type(dpr_type))

    @property
    def science_fiber(self):
        return self.value[0]

    @property
    def reference_fiber(self):
        return self.value[1]

    def to_dpr_type(self):
        return FiberType.to_dpr_type(self.science_fiber, self.reference_fiber)


class InstrumentMode(Enum):
    SPECTROSCOPY = ('P16', 'P16')
    POLAR1 = ('P14', 'P16')
    POLAR2 = ('P2', 'P16')
    POLAR3 = ('P2', 'P4')
    POLAR4 = ('P14', 'P4')

    @staticmethod
    def from_rhombs(rhomb1, rhomb2):
        return InstrumentMode((rhomb1, rhomb2))

    def is_polarimetry(self):
        return self != self.SPECTROSCOPY


class TargetType(Enum):
    STAR = 0
    SKY = 1
    TELLURIC_STANDARD = 2


class ObjectLite():
    def __init__(self, instrument_mode, target):
        self.instrument_mode = instrument_mode
        self.target = target


class Object(ObjectLite):
    def __init__(self, instrument_mode, target, reference_fiber):
        super().__init__(instrument_mode, target)
        self.reference_fiber = reference_fiber


class ExposureConfigLite():
    def __init__(self, object=None):
        self.object = object

    @classmethod
    def from_header_checker(cls, header_checker):
        if header_checker.is_object():
            instrument_mode = InstrumentMode(header_checker.get_rhomb_positions())
            if header_checker.is_sky():
                target = TargetType.SKY
            elif header_checker.get_object_name() in TELLURIC_STANDARDS:
                target = TargetType.TELLURIC_STANDARD
            else:
                target = TargetType.STAR
            object = ObjectLite(instrument_mode, target)
            return cls(object=object)
        else:
            raise ValueError('ExposureConfigLite meant for use with object exposures')


class ExposureConfig():
    def __init__(self, calibration=None, object=None):
        if calibration is None and object is None:
            raise ValueError('Exposure must be calibration or object')
        if calibration is not None and object is not None:
            raise ValueError('Exposure cannot be both calibration and object')
        self.calibration = calibration
        self.object = object

    def is_matching_type(self, exposure_config):
        return self.is_matching_calibration(exposure_config) or self.is_matching_object(exposure_config)

    def is_matching_calibration(self, exposure_config):
        return self.calibration and exposure_config.calibration and self.calibration == exposure_config.calibration

    def is_matching_object(self, exposure_config):
        a = self.object
        b = exposure_config.object
        return (a and b and a.reference_fiber == b.reference_fiber and a.target == a.target
                and a.instrument_mode.is_polarimetry() == b.instrument_mode.is_polarimetry())

    @classmethod
    def from_file(cls, file):
        header_checker = HeaderChecker(file)
        return cls.from_header_checker(header_checker)

    @classmethod
    def from_header_checker(cls, header_checker):
        dpr_type = header_checker.get_dpr_type()
        if header_checker.is_object():
            instrument_mode = InstrumentMode(header_checker.get_rhomb_positions())
            if header_checker.is_sky():
                target = TargetType.SKY
            elif header_checker.get_object_name() in TELLURIC_STANDARDS:
                target = TargetType.TELLURIC_STANDARD
            else:
                target = TargetType.STAR
            object_fiber, reference_fiber = FiberType.from_dpr_type(dpr_type)
            if object_fiber != FiberType.OBJ:
                log.warning('Object exposure %s has DPRTYPE %s instead of OBJ', header_checker.file, dpr_type)
            object = Object(instrument_mode, target, reference_fiber)
            return cls(object=object)
        else:
            calibration = CalibrationType.from_dpr_type(dpr_type)
            return cls(calibration=calibration)
