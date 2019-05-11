from abc import ABC, abstractmethod

from .drswrapper import RecipeFailure
from .exposureconfig import ExposureConfig
from .headerchecker import HeaderChecker
from .log import log
from .pathhandler import Exposure
from .processor import Processor


class AbstractCustomHandler(ABC):
    @abstractmethod
    def handle_recipe_failure(self, exposure_or_sequence, error):
        pass

    @abstractmethod
    def exposure_post_process(self, exposure, result):
        pass

    @abstractmethod
    def sequence_post_process(self, sequence, result):
        pass


class BaseDrsTrigger:
    def __init__(self, steps, realtime=False, trace=False, ccf_params=None):
        self.realtime = realtime
        self.steps = steps
        self.processor = Processor(self.steps, trace, realtime, ccf_params)
        self.custom_handler = None

    def set_custom_handler(self, handler):
        self.custom_handler = handler

    def reduce(self, night, files_in_order):
        if self.realtime:
            raise RuntimeError('Realtime mode not meant for reducing entire fileset!')
        current_sequence = []
        for file in files_in_order:
            if not self.preprocess(night, file):
                continue
            try:
                self.process_file(night, file)
                completed_sequences = self.sequence_checker(night, current_sequence, file)
                for completed_sequence in completed_sequences:
                    if completed_sequence:
                        self.process_sequence(night, completed_sequence)
            except:
                log.error('Critical failure processing %s, skipping', file, exc_info=True)

    def preprocess(self, night, file):
        exposure = Exposure(night, file)
        try:
            return self.processor.preprocess_exposure(exposure)
        except RecipeFailure as e:
            if self.custom_handler:
                self.custom_handler.handle_recipe_failure(exposure, e)
            else:
                raise

    def process_file(self, night, file):
        exposure = Exposure(night, file)
        exposure_config = ExposureConfig.from_file(exposure.preprocessed)
        try:
            result = self.processor.process_exposure(exposure_config, exposure)
        except RecipeFailure as e:
            if self.custom_handler:
                self.custom_handler.handle_recipe_failure(exposure, e)
            else:
                raise
        else:
            if self.custom_handler:
                self.custom_handler.exposure_post_process(exposure, result)

    def process_sequence(self, night, files):
        exposures = [Exposure(night, file) for file in files]
        sequence_config = ExposureConfig.from_file(exposures[0].preprocessed)
        for exposure in exposures:
            exposure_config = ExposureConfig.from_file(exposure.preprocessed)
            assert exposure_config.is_matching_type(sequence_config), 'Exposure type changed mid-sequence'
        try:
            result = self.processor.process_sequence(sequence_config, exposures)
        except RecipeFailure as e:
            if self.custom_handler:
                self.custom_handler.handle_recipe_failure(exposures, e)
            else:
                raise
        else:
            if self.custom_handler:
                self.custom_handler.sequence_post_process(exposures, result)

    # Appends file to current_sequence, and if sequence is now complete, returns it and clears current_sequence.
    @staticmethod
    def sequence_checker(night, current_sequence, file):
        exposure = Exposure(night, file)
        finished_sequences = []
        header = HeaderChecker(exposure.raw)
        exp_index, exp_total = header.get_exposure_index_and_total()
        if len(current_sequence) > 0 and exp_index == 1:
            log.warning('Exposure number reset mid-sequence, ending previous sequence early: %s', current_sequence)
            finished_sequences.append(current_sequence.copy())
            current_sequence.clear()
        current_sequence.append(exposure.raw.name)
        if exp_index == exp_total:
            finished_sequences.append(current_sequence.copy())
            current_sequence.clear()
        return finished_sequences
