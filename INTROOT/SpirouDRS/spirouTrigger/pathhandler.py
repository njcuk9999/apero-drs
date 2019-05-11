from pathlib import Path
from .constants import ROOT_DATA_DIRECTORIES

class Night:
    root_data_directories = ROOT_DATA_DIRECTORIES

    def __init__(self, night):
        self.night = night

    @property
    def input_directory(self):
        return Path(self.root_data_directories.input, self.night)

    @property
    def temp_directory(self):
        return Path(self.root_data_directories.tmp, self.night)

    @property
    def reduced_directory(self):
        return Path(self.root_data_directories.reduced, self.night)


class Exposure:
    def __init__(self, night, raw_file):
        self.__night = Night(night)
        self.__raw_filename = Path(raw_file).name

    @property
    def night(self):
        return self.__night.night

    @property
    def raw(self):
        return Path(self.input_directory, self.__raw_filename)

    @property
    def preprocessed(self):
        return Path(self.temp_directory, self.raw.name.replace('.fits', '_pp.fits'))

    def s1d(self, fiber):
        return self.extracted_product('s1d', fiber)

    def e2ds(self, fiber, telluric_corrected=False, telluric_reconstruction=False, flat_fielded=False):
        product_name = 'e2dsff' if flat_fielded else 'e2ds'
        assert not (telluric_corrected and telluric_reconstruction)
        if telluric_corrected:
            suffix = 'tellu_corrected'
        elif telluric_reconstruction:
            suffix = 'tellu_recon'
        else:
            suffix = None
        return self.extracted_product(product_name, fiber, suffix)

    def ccf(self, fiber, mask, fp=True, telluric_corrected=False):
        product_name = 'ccf_' + ('fp_' if fp else '') + mask.replace('.mas', '')
        suffix = 'tellu_corrected' if telluric_corrected else None
        return self.extracted_product(product_name, fiber, suffix)

    def extracted_product(self, product, fiber, suffix=None):
        suffix = '_' + suffix if suffix else ''
        return self.reduced(product + '_' + fiber + suffix)

    def reduced(self, product):
        return Path(self.reduced_directory, self.preprocessed.name.replace('.fits', '_' + product + '.fits'))

    def final_product(self, letter):
        return Path(self.reduced_directory, self.raw.name.replace('o.fits', letter + '.fits'))

    @property
    def input_directory(self):
        return self.__night.input_directory

    @property
    def temp_directory(self):
        return self.__night.temp_directory

    @property
    def reduced_directory(self):
        return self.__night.reduced_directory

    @property
    def obsid(self):
        return self.raw.stem

    @property
    def odometer(self):
        return int(self.obsid[:-1])
