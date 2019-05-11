from SpirouDRS import spirouConfig, spirouTelluric


class DataDirectories:
    def __init__(self):
        self.config, _warnings = spirouConfig.ReadConfigFile()

    @property
    def input(self):
        return self.config['DRS_DATA_RAW']

    @property
    def reduced(self):
        return self.config['DRS_DATA_REDUC']

    @property
    def tmp(self):
        return self.config['DRS_DATA_WORKING']


DRS_VERSION = spirouConfig.Constants.VERSION()
TELLURIC_STANDARDS = spirouTelluric.GetWhiteList()
ROOT_DATA_DIRECTORIES = DataDirectories()
