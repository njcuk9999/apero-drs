import textwrap
from collections import defaultdict, OrderedDict
from pathlib import Path

import numpy as np
from astropy.io import fits

from .drswrapper import FIBER_LIST
from .log import log


class BinTableConfig:
    def __init__(self, **kwargs):
        self.column_names = kwargs.get('column_names')
        self.column_units = kwargs.get('column_units')
        self.column_formats = kwargs.get('column_formats')
        self.transpose = bool(kwargs.get('transpose'))

    def convert_image_to_binary_table(self, image_hdu):
        header = image_hdu.header.copy()
        default_unit = header.get('BUNIT')
        if 'BUNIT' in header:
            header.remove('BUNIT')
        bitpix_format_map = {16: 'I', 32: 'J', 64: 'K', -32: 'E', -64: 'D'}
        default_format = bitpix_format_map.get(header.get('BITPIX'))
        data = image_hdu.data if not self.transpose else image_hdu.data.T
        names = self.column_names
        units = self.column_units if self.column_units else [default_unit] * len(names)
        formats = self.column_formats if self.column_formats else [default_format] * len(names)
        assert len(names) == len(data)
        columns = [fits.Column(name=name, format=format, unit=unit, array=column)
                   for name, format, unit, column in zip(names, formats, units, data)]
        return fits.BinTableHDU.from_columns(columns, header=header)


class HDUConfig:
    def __init__(self, ext_name, path, extension=0, **kwargs):
        self.ext_name = ext_name
        self.path = path
        self.extension = extension
        self.primary_header_only = kwargs.get('primary_header_only')
        self.header_operation = kwargs.get('header_operation')
        self.data_operation = kwargs.get('data_operation')
        self.hdu_operation = kwargs.get('hdu_operation')
        self.bin_table = kwargs.get('bin_table')

    def is_bin_table(self):
        return bool(self.bin_table)

    def set_bin_table_config(self, bin_table):
        self.bin_table = bin_table

    def open_hdu_and_update(self):
        hdu = self.open_hdu()
        if self.ext_name:
            if 'XTENSION' in hdu.header:
                hdu.header.insert('GCOUNT', ('EXTNAME', self.ext_name), after=True)
            else:
                hdu.header.insert(0, ('EXTNAME', self.ext_name))
        if self.primary_header_only:
            hdu = fits.PrimaryHDU(header=hdu.header)
        if self.hdu_operation:
            self.hdu_operation(hdu)
        if self.header_operation:
            self.header_operation(hdu.header)
        if self.data_operation:
            self.data_operation(hdu.data)
        if self.bin_table:
            hdu = self.bin_table.convert_image_to_binary_table(hdu)
        return hdu

    def open_hdu(self):
        hdu_list = fits.open(self.path)
        hdu = hdu_list[self.extension]
        return hdu


class MEFConfig:
    def __init__(self, extension_configs, hdulist_operation=None):
        self.hdu_configs = extension_configs
        self.hdulist_operation = hdulist_operation

    def create_hdu_list(self):
        hdu_list = fits.HDUList()
        for hdu_config in self.hdu_configs:
            source_hdu = hdu_config.open_hdu_and_update()
            if len(hdu_list) == 0:
                source_hdu.header['NEXTEND'] = len(self.hdu_configs) - 1
            else:
                source_hdu.header.remove('NEXTEND', ignore_missing=True)
            self.wcs_clean(source_hdu.header)
            hdu_list.append(source_hdu)
        if self.hdulist_operation:
            self.hdulist_operation(hdu_list)
        return hdu_list

    @staticmethod
    def wcs_clean(header):
        if header['NAXIS'] < 2 or header.get('XTENSION') == 'BINTABLE':
            remove_keys(header, ('CTYPE2', 'CUNIT2', 'CRPIX2', 'CRVAL2', 'CDELT2'))
        if header['NAXIS'] < 1 or header.get('XTENSION') == 'BINTABLE':
            remove_keys(header, ('CTYPE1', 'CUNIT1', 'CRPIX1', 'CRVAL1', 'CDELT1'))


class ProductPackager:
    def __init__(self, trace, create):
        self.create = create and not trace

    def create_spec_product(self, exposure):
        self.create_1d_spectra_product(exposure)
        self.create_2d_spectra_product(exposure)

    def create_1d_spectra_product(self, exposure):
        def update_hdu(hdu):
            flux = hdu.data
            errs = np.full(len(flux), np.nan)
            wavelengths = self.resample_wcs_to_data(hdu.header, flux)
            hdu.data = np.row_stack((flux, errs, wavelengths))

        def config_builder():
            bin_table_config = BinTableConfig(column_names=['Flux', 'FluxErr', 'Wave'],
                                              column_units=['Relative Flux', 'Relative Flux', 'nm'])
            extensions = [HDUConfig(fiber, exposure.s1d(fiber), hdu_operation=update_hdu, bin_table=bin_table_config)
                          for fiber in FIBER_LIST]
            return [
                self.get_primary_header(exposure),
                *extensions
            ]

        product_1d = exposure.final_product('s')
        self.produce(product_1d, config_builder)

    def create_2d_spectra_product(self, exposure):
        def config_builder():
            flux_extensions = [HDUConfig('Flux' + fiber, exposure.e2ds(fiber, flat_fielded=True))
                               for fiber in FIBER_LIST]
            try:
                cal_extensions = self.get_cal_extensions(exposure)
            except:
                log.error('Failed to find calibration files in header, cannot create %s', product_2d.filename)
            else:
                return [
                    self.get_primary_header(exposure),
                    *flux_extensions,
                    *cal_extensions
                ]

        product_2d = exposure.final_product('e')
        self.produce(product_2d, config_builder)

    def create_pol_product(self, exposure):
        def wipe_snr(header):
            for i in range(0, 49):
                key = 'SNR' + str(i)
                header[key] = 'Unknown'

        def update_then_copy_input_files_to_primary(hdulist):
            self.product_header_update(hdulist)
            primary_header = hdulist[0].header
            pol_header = hdulist[1].header
            in_file_cards = [card for card in pol_header.cards if card[0].startswith('FILENAM')]
            for card in in_file_cards:
                primary_header.insert('FILENAME', card)
            primary_header.remove('FILENAME', ignore_missing=True)

        def config_builder():
            try:
                cal_extensions = self.get_cal_extensions(exposure, 'WaveAB', 'BlazeAB')
            except:
                log.error('Failed to find calibration files in header, cannot create %s', product_pol.filename)
            else:
                return [
                    self.get_primary_header(exposure),
                    HDUConfig('Pol', exposure.reduced('e2ds_pol'), header_operation=wipe_snr),
                    HDUConfig('PolErr', exposure.reduced('e2ds_pol'), extension=1),
                    HDUConfig('StokesI', exposure.reduced('e2ds_AB_StokesI'), header_operation=wipe_snr),
                    HDUConfig('StokesIErr', exposure.reduced('e2ds_AB_StokesI'), extension=1),
                    HDUConfig('Null1', exposure.reduced('e2ds_null1_pol'), header_operation=wipe_snr),
                    HDUConfig('Null2', exposure.reduced('e2ds_null2_pol'), header_operation=wipe_snr),
                    *cal_extensions
                ]

        product_pol = exposure.final_product('p')
        self.produce_generalized(product_pol, config_builder, update_then_copy_input_files_to_primary)

    def create_tell_product(self, exposure):
        def config_builder():
            try:
                cal_extensions = self.get_cal_extensions(exposure, 'WaveAB', 'BlazeAB')
            except:
                log.error('Failed to find calibration files in header, cannot create %s', product_tell.filename)
            else:
                return [
                    self.get_primary_header(exposure),
                    HDUConfig('FluxAB', exposure.e2ds('AB', telluric_corrected=True, flat_fielded=True)),
                    *cal_extensions,
                    HDUConfig('Recon', exposure.e2ds('AB', telluric_reconstruction=True, flat_fielded=True))
                ]

        product_tell = exposure.final_product('t')
        self.produce(product_tell, config_builder)

    def create_ccf_product(self, exposure, ccf_mask, telluric_corrected, fp):
        def fix_header(header):
            header.insert('CRVAL1', ('CRPIX1', 0))

        def update_primary_header(header):
            fix_header(header)

        def update_hdu(hdu):
            existing = hdu.data
            velocities = self.resample_wcs_to_data(hdu.header, existing[0])
            hdu.data = np.row_stack((velocities, existing))
            fix_header(hdu.header)

        def config_builder():
            ccf_path = exposure.ccf('AB', ccf_mask, telluric_corrected=telluric_corrected, fp=fp)
            bin_table_config = BinTableConfig(column_names=['Velocity'] + self.get_default_columns() + ['Combined'],
                                              column_units=['km/s'] + [None] * 50)
            return [
                HDUConfig(None, ccf_path, header_operation=update_primary_header, primary_header_only=True),
                HDUConfig('CCF', ccf_path, hdu_operation=update_hdu, bin_table=bin_table_config)
            ]

        product_ccf = exposure.final_product('v')
        self.produce_generalized(product_ccf, config_builder, None)

    def produce(self, path, config_builder):
        self.produce_generalized(path, config_builder, hdulist_operation=self.product_header_update)

    def produce_generalized(self, path, config_builder, hdulist_operation=None):
        if self.create:
            hdu_configs = config_builder()
            mef_config = MEFConfig(hdu_configs, hdulist_operation=hdulist_operation)
            self.create_mef(mef_config, path.fullpath)

    def get_primary_header(self, exposure):
        def remove_new_keys(header):
            remove_keys(header, ('DRSPID', 'INF1000', 'QCC', 'QCC000N',
                                 'QCC001N', 'QCC001V', 'QCC001L', 'QCC001P',
                                 'QCC002N', 'QCC002V', 'QCC002L', 'QCC002P'))

        return HDUConfig(None, exposure.preprocessed, primary_header_only=True, header_operation=remove_new_keys)

    def get_default_columns(self):
        return ['Order' + str(i) for i in range(0, 49)]

    def product_header_update(self, hdulist):
        if len(hdulist) <= 1:
            log.error('Trying to create product primary HDU with no extensions')
            return
        primary_header = hdulist[0].header
        ext_header = hdulist[1].header
        primary_header.insert('PVERSION', get_card(ext_header, 'VERSION'), after=True)
        remove_keys(primary_header, ('BITPIX', 'NAXIS', 'NAXIS1', 'NAXIS2'))
        if ext_header.get('EXTNAME') == 'Pol':
            primary_header['EXPTIME'] = (ext_header['EXPTIME'], '[sec] total integration time of 4 exposures')
            primary_header['MJDATE'] = (ext_header['MJDATE'], 'Modified Julian Date at middle of sequence')
        for extension in hdulist[1:]:
            extname = extension.header.get('EXTNAME')
            if extname.startswith('Wave') or extname.startswith('Blaze') or extname.endswith('Err'):
                continue
            dupe_keys = verify_duplicate_cards(extension.header, primary_header.items())
            remove_keys(extension.header, dupe_keys)
        self.add_extension_description(hdulist)

    @staticmethod
    def add_extension_description(hdulist):
        ext_names = [hdu.header.get('EXTNAME') for hdu in hdulist[1:]]
        description = 'This file contains the following extensions: ' + ', '.join(ext_names)
        for line in textwrap.wrap(description, 71):
            hdulist[0].header.insert('FILENAME', ('COMMENT', line))

    def get_cal_extensions(self, exposure, *args):
        def keep_key(key):
            return key in ('EXTNAME', 'NAXIS', 'NAXIS1', 'NAXIS2') or key.startswith('INF') or key.startswith('CDB')

        def cleanup_keys(header):
            remove_keys(header, [key for key in header.keys() if not keep_key(key)])

        def extension_operation(ext_name):
            if ext_name.startswith('Wave') or ext_name.startswith('Blaze'):
                return cleanup_keys
            return None

        cal_path_dict = self.get_cal_paths(exposure)
        ext_names = args if args else cal_path_dict.keys()
        return [HDUConfig(name, cal_path_dict[name], header_operation=extension_operation(name)) for name in ext_names]

    def get_cal_paths(self, exposure):
        headers_per_fiber = defaultdict(OrderedDict)
        for fiber in FIBER_LIST:
            source_file = exposure.e2ds(fiber, flat_fielded=True)
            source_header = fits.open(source_file)[0].header
            for keyword in ['CDBWAVE', 'CDBBLAZE']:
                headers_per_fiber[keyword][fiber] = source_header[keyword]
        extensions = OrderedDict()
        reduced_directory = exposure.reduced_directory
        for fiber in FIBER_LIST:
            filename = headers_per_fiber['CDBWAVE'][fiber]
            extensions['Wave' + fiber] = Path(reduced_directory, filename)
        for fiber in FIBER_LIST:
            filename = headers_per_fiber['CDBBLAZE'][fiber]
            extensions['Blaze' + fiber] = Path(reduced_directory, filename)
        return extensions

    @classmethod
    def resample_wcs_to_data(cls, header, data):
        c_start = float(header['CRVAL1'])
        c_delta = float(header['CDELT1'])
        num_bins = len(data)
        return cls.steps(c_start, c_delta, num_bins)

    @staticmethod
    def steps(start, step, n):
        end = start + step * n
        return np.linspace(start, end, num=n, endpoint=False)

    def create_mef(self, mef_config, output_file):
        log.info('Creating MEF %s', output_file)
        try:
            hdu_list = mef_config.create_hdu_list()
        except FileNotFoundError as err:
            log.error('Creation of %s failed: unable to open file %s', output_file, err.filename)
        except:
            log.error('Creation of %s failed', output_file, exc_info=True)
        else:
            hdu_list.writeto(output_file, overwrite=True)


def get_card(header, keyword):
    return (keyword, header[keyword], header.comments[keyword])


def remove_keys(header, keys):
    for key in keys:
        header.remove(key, ignore_missing=True)


def verify_duplicate_cards(header, cards):
    dupe_keys = []
    for card in cards:
        key, value = card[0], card[1]  # Split up so it still works if len(card) is 3
        if key in ('SIMPLE', 'EXTEND', 'NEXTEND'):
            continue
        if header.get(key) == value:
            dupe_keys.append(key)
        else:
            extname = header.get('EXTNAME')
            log.warning('Header key %s expected to be duplicate in extension %s but was not', key, extname)
    return dupe_keys
