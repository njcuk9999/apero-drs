from .exposureconfig import TargetType, ExposureConfigLite
from .headerchecker import HeaderChecker
from .log import log


def sort_and_filter_files(files, steps, runid=None):
    checkers = [HeaderChecker(file) for file in files]
    filtered = filter(lambda checker: is_desired_file(checker, steps)
                                      and not checker.is_aborted()
                                      and is_desired_runid(checker, runid),
                      checkers)
    return sort_files_by_observation_date(filtered)


def is_desired_file(checker, steps):
    return (steps.preprocess and has_useable_extension(checker.file) or
            steps.calibrations and has_calibration_extension(checker.file) or
            steps.objects and has_object_extension(checker.file) and is_desired_object(checker, steps.objects))


def has_useable_extension(file):
    return has_object_extension(file) or has_calibration_extension(file)


def has_object_extension(file):
    return file.name.endswith('o.fits')


def has_calibration_extension(file):
    return file.name.endswith(('a.fits', 'c.fits', 'd.fits', 'f.fits'))


def is_desired_object(checker, object_steps):
    object_config = ExposureConfigLite.from_header_checker(checker).object
    return (object_steps.extract or
            object_steps.pol and object_config.instrument_mode.is_polarimetry() or
            object_steps.mktellu and object_config.target == TargetType.TELLURIC_STANDARD or
            object_steps.fittellu and object_config.target == TargetType.STAR or
            object_steps.ccf and object_config.target == TargetType.STAR or
            object_steps.products or
            object_steps.distribute or
            object_steps.database)


def is_desired_runid(checker, runid_filter=None):
    run_id = checker.get_runid()
    if runid_filter and not run_id:
        log.warning('File %s missing RUNID keyword, skipping.', checker.file)
        return False
    elif runid_filter and run_id != runid_filter:
        return False
    return True


def sort_files_by_observation_date(checkers):
    file_times = {}
    for checker in checkers:
        obs_date = checker.get_obs_date()
        if not obs_date:
            log.warning('File %s missing observation date info, skipping.', checker.file)
        else:
            file_times[checker.file] = obs_date
    return sorted(file_times, key=file_times.get)
