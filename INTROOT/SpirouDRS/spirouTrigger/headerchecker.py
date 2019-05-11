from astropy.io import fits

from .log import log

class HeaderChecker:
    def __init__(self, file):
        self.file = file
        self.__header = None

    @property
    def header(self):
        self.__lazy_loading()
        return self.__header

    def __lazy_loading(self):
        if not self.__header:
            try:
                hdulist = fits.open(self.file)
            except:
                raise RuntimeError('Failed to open', self.file)
            self.__header = hdulist[0].header

    def is_object(self):
        return self.header.get('OBSTYPE') == 'OBJECT'

    def get_object_name(self):
        name_keyword = 'OBJECT'
        if name_keyword not in self.header:
            name_keyword = 'OBJNAME'
            if name_keyword not in self.header:
                raise RuntimeError('Object file missing OBJECT and OBJNAME keywords', self.file)
        return self.header[name_keyword]

    def is_sky(self):
        object_name = self.get_object_name()
        return (self.header.get('TRGTYPE') == 'SKY'
                or object_name.lower() == 'sky'
                or object_name.startswith('sky_')
                or object_name.endswith('_sky'))

    def get_dpr_type(self):
        if 'DPRTYPE' not in self.header or self.header['DPRTYPE'] == 'None':
            raise RuntimeError('File missing DPRTYPE keyword', self.file)
        return self.header['DPRTYPE']

    def get_exposure_index_and_total(self):
        if 'CMPLTEXP' not in self.header or 'NEXP' not in self.header:
            log.warning('%s missing CMPLTEXP/NEXP in header, treating sequence as single exposure', self.file)
            return 1, 1
        else:
            return self.header['CMPLTEXP'], self.header['NEXP']

    def get_rhomb_positions(self):
        if 'SBRHB1_P' not in self.header:
            raise RuntimeError('Object file missing SBRHB1_P keyword', self.file)
        if 'SBRHB2_P' not in self.header:
            raise RuntimeError('Object file missing SBRHB2_P keyword', self.file)
        return self.header.get('SBRHB1_P'), self.header.get('SBRHB2_P')

    def get_obs_date(self):
        return self.header.get('MJDATE')

    def get_runid(self):
        return self.header.get('RUNID')

    def is_aborted(self):
        MIN_EXP_TIME_RATIO_THRESHOLD = 0.1
        if 'EXPTIME' not in self.header or 'EXPREQ' not in self.header:
            log.warning('%s missing EXPTIME/EXPREQ in header, assuming not an aborted exposure', self.file)
        return self.header['EXPTIME'] / self.header['EXPREQ'] < MIN_EXP_TIME_RATIO_THRESHOLD
