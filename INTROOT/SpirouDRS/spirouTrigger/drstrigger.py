from .basedrstrigger import BaseDrsTrigger
from .constants import DRS_VERSION
from .fileselector import sort_and_filter_files
from .log import log
from .pathhandler import Night

TRIGGER_VERSION = '017'


class DrsTrigger(BaseDrsTrigger):
    @staticmethod
    def drs_version():
        return DRS_VERSION

    @staticmethod
    def trigger_version():
        return TRIGGER_VERSION

    def reduce_night(self, night, runid=None):
        if self.realtime:
            raise RuntimeError('Realtime mode not meant for reducing entire night!')
        files = self.__find_files(night, runid)
        self.reduce(night, files)

    def reduce_range(self, night, start_file, end_file):
        if self.realtime:
            raise RuntimeError('Realtime mode not meant for reducing entire fileset!')
        files = self.__find_files(night)
        subrange = self.__get_subrange(files, start_file, end_file)
        if subrange:
            self.reduce(night, subrange)

    def __find_files(self, night, runid=None):
        night_directory = Night(night).input_directory
        all_files = [file for file in night_directory.glob('*.fits') if file.exists()]  # filter out broken symlinks
        files = sort_and_filter_files(all_files, self.steps, runid)  # Filter out unused input files ahead of time
        return files

    def __get_subrange(self, files, start_file, end_file):
        start_index, end_index = None, None
        for i, file in enumerate(files):
            if file.name == start_file:
                start_index = i
            if file.name == end_file:
                end_index = i + 1
        if start_index is not None and end_index is not None:
            return files[start_index:end_index]
        if start_index is None:
            log.error('Did not find range start file %s', start_file)
        if end_index is None:
            log.error('Did not find range end file %s', end_file)
