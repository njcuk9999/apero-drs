#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for FileObjectConst (local / MAST / POGOS server file constants)

No network access: MAST is replaced by a fake Observations class and the
POGOS server by a local mirror directory.
"""
import os
import pickle

import pytest
from astropy.table import Table

from aperocore.constants import custom_const_classes as ccc
from aperocore.constants import file_sources
from aperocore.constants import load_functions
from aperocore.constants.constant_functions import ConstantsDict


# =============================================================================
# Define helpers
# =============================================================================
def make_cdict() -> ConstantsDict:
    """Constants dictionary with a list, a single and a wave-like file."""
    cdict = ConstantsDict('test')
    cdict.title = 'test yaml'
    cdict.add('RAWPATH', value=None, dtype=str, source='test',
              group='PATHS', user=True, active=True)
    cdict.add('CALIBPATH', value=None, dtype=str, source='test',
              group='PATHS', user=True, active=True)
    cdict.addc('FILES', value=None, dtype=list, dtypei=str, source='test',
               group='GENERAL', user=True, active=True,
               description='Files', const_class=ccc.FileObjectConst,
               path_key='PATHS.RAWPATH', product='rateints')
    cdict.addc('FLATFILE', value=None, dtype=str, source='test',
               group='GENERAL', user=True, active=True,
               description='Flat', const_class=ccc.FileObjectConst,
               path_key='PATHS.CALIBPATH')
    extras = dict(type=dict(dtype=str, options=['ext1d', 'fits'],
                            description='file type'))
    cdict.addc('WAVE_FILE', value=None, dtype=str, source='test',
               group='GENERAL', user=True, active=True, allow_list=True,
               description='Wave', const_class=ccc.FileObjectConst,
               path_key='PATHS.CALIBPATH', extras=extras)
    return cdict


def load_yaml_text(tmp_path, text):
    """Write text to a yaml and load it into params."""
    yaml_file = tmp_path / 'config.yaml'
    yaml_file.write_text(text)
    cdict = make_cdict()
    params = load_functions.load_parameters([cdict])
    params = load_functions.load_from_yaml([str(yaml_file)], params)
    return cdict, params, yaml_file


class FakeObservations:
    """Minimal stand-in for astroquery.mast.Observations."""

    def __init__(self, filenames, sizes=None):
        self.filenames = filenames
        self.sizes = sizes or [5e6] * len(filenames)
        self.downloaded = []
        self.token = None

    def login(self, token=None):
        self.token = token

    def query_criteria(self, obs_collection=None, proposal_id=None):
        assert obs_collection == 'JWST'
        assert proposal_id == '01366'
        return Table(dict(obs_id=['jw01366-o001_t001_niriss',
                                  'jw01366-o002_t001_niriss']))

    def get_product_list(self, observations):
        assert len(observations) == 1
        return Table(dict(productFilename=self.filenames,
                          size=self.sizes))

    def download_products(self, products, download_dir=None, flat=False):
        status, paths = [], []
        for name in products['productFilename']:
            path = os.path.join(download_dir, str(name))
            with open(path, 'w') as handle:
                handle.write('data')
            self.downloaded.append(str(name))
            status.append('COMPLETE')
            paths.append(path)
        return Table({'Local Path': paths, 'Status': status})


# =============================================================================
# Validation
# =============================================================================
def test_plain_values_stay_plain():
    cdict = make_cdict()
    files = cdict.get('GENERAL.FILES')
    flat = cdict.get('GENERAL.FLATFILE')
    assert files.validate(['a.fits', 'b.fits']) == ['a.fits', 'b.fits']
    assert type(files.validate(['a.fits'])) is list
    assert type(flat.validate('flat.fits')) is str
    # a single name for a list constant becomes a list
    assert files.validate('a.fits') == ['a.fits']


@pytest.mark.parametrize('value', ['', [], [None], [1], dict(NRS1='w.fits'),
                                   dict(filelist='w.fits', source='ftp'),
                                   dict(filelist=None, source='local'),
                                   dict(filelist=None, source='mast',
                                        pid=1),
                                   dict(filelist=None, source='pogos',
                                        url='http://x/'),
                                   dict(filelist='w.fits', source='local',
                                        pid=1)])
def test_invalid_values_raise(value):
    wave = make_cdict().get('GENERAL.WAVE_FILE')
    with pytest.raises(ccc.AperoConstantError, match='WAVE_FILE'):
        wave.validate(value)


def test_custom_exception_class():
    class MyError(Exception):
        pass
    cdict = ConstantsDict('test')
    cdict.addc('FILE', value=None, dtype=str, source='test',
               const_class=ccc.FileObjectConst, exception=MyError)
    with pytest.raises(MyError):
        cdict.get('FILE').validate('')


def test_mast_mapping_carries_fileobj():
    files = make_cdict().get('GENERAL.FILES')
    value = files.validate({'filelist': None, 'source': 'mast', 'pid': 1366,
                            'obsnumber': '1', 'always-download': False})
    assert isinstance(value, ccc.FileList) and value == []
    assert value.fileobj.pid == 1366 and value.fileobj.obsnumber == 1
    # product defaults to the constant's product
    assert value.fileobj.product == 'rateints'
    # copies / pickles keep the source information
    assert value.copy().fileobj.pid == 1366
    assert pickle.loads(pickle.dumps(value)).fileobj.pid == 1366
    # re-validating a value keeps the source information
    assert files.validate(value).fileobj.source == 'mast'


def test_wave_extras():
    wave = make_cdict().get('GENERAL.WAVE_FILE')
    value = wave.validate(dict(filelist=['w1.fits', 'w2.fits'], type='ext1d'))
    params = {'GENERAL.WAVE_FILE': value}
    assert ccc.get_file_extra(params, 'GENERAL.WAVE_FILE', 'type') == 'ext1d'
    assert wave.yaml_value(value) == dict(filelist=['w1.fits', 'w2.fits'],
                                          type='ext1d', source='local')
    # set an extra on a plain value
    params = {'GENERAL.WAVE_FILE': 'w.fits'}
    ccc.set_file_extra(params, 'GENERAL.WAVE_FILE', 'type', 'fits')
    assert params['GENERAL.WAVE_FILE'] == 'w.fits'
    assert ccc.get_file_extra(params, 'GENERAL.WAVE_FILE', 'type') == 'fits'


def test_description_documents_all_cases():
    desc = make_cdict().get('GENERAL.FILES').description
    for label in ['[A] LOCAL', '[B] MAST', '[C] MAST', '[D] POGOS',
                  '[E] POGOS', 'PATHS.RAWPATH', 'MAST_API_TOKEN']:
        assert label in desc


# =============================================================================
# Yaml round trip
# =============================================================================
def test_yaml_load_and_save_round_trip(tmp_path):
    text = ('GENERAL:\n'
            '  FILES:\n'
            '    filelist:\n'
            '    source: mast\n'
            '    pid: 1366\n'
            '    obsnumber: 1\n'
            '  FLATFILE: flat.fits\n')
    cdict, params, _ = load_yaml_text(tmp_path, text)
    assert params['GENERAL.FILES'].fileobj.source == 'mast'
    assert params['GENERAL.FLATFILE'] == 'flat.fits'
    # save and reload
    out = tmp_path / 'out.yaml'
    cdict.save_yaml(params, outpath=str(out), log=False)
    reloaded = load_functions.load_parameters([make_cdict()])
    reloaded = load_functions.load_from_yaml([str(out)], reloaded)
    assert reloaded['GENERAL.FILES'].fileobj.pid == 1366
    assert reloaded['GENERAL.FLATFILE'] == 'flat.fits'
    assert 'filelist:' in out.read_text()


# =============================================================================
# Resolving files
# =============================================================================
def test_resolve_mast_downloads_and_updates_yaml(tmp_path, monkeypatch):
    raw = tmp_path / 'raw'
    text = ('PATHS:\n'
            f'  RAWPATH: {raw}\n'
            'GENERAL:\n'
            '  # my comment\n'
            '  FILES:\n'
            '    filelist:\n'
            '    source: mast\n'
            '    pid: 1366\n'
            '    obsnumber: 1\n')
    _, params, yaml_file = load_yaml_text(tmp_path, text)
    names = ['jw-seg002_nis_rateints.fits', 'jw-seg001_nis_rateints.fits',
             'jw-seg001_nis_uncal.fits', 'jw_nis_rateints.fits',
             'jw-seg003_nis_rateints.fits']
    sizes = [5e6, 5e6, 5e6, 5e6, 1e3]
    fake = FakeObservations(names, sizes)
    monkeypatch.setattr(file_sources, '_get_mast_observations', lambda: fake)
    monkeypatch.setenv(file_sources.MAST_TOKEN_ENV, 'secret')
    updates = file_sources.resolve_files(params, yaml_file=str(yaml_file))
    # every *_rateints.fits above min_size_mb (with or without -seg)
    expected = ['jw-seg001_nis_rateints.fits', 'jw-seg002_nis_rateints.fits',
                'jw_nis_rateints.fits']
    assert fake.token == 'secret'
    assert sorted(fake.downloaded) == expected
    assert params['GENERAL.FILES'] == expected
    assert updates['GENERAL.FILES']['always_download'] is False
    # yaml rewritten in place, comment kept
    text_out = yaml_file.read_text()
    assert '# my comment' in text_out
    assert 'jw-seg001_nis_rateints.fits' in text_out
    # second pass: files exist so nothing is downloaded
    _, params2, _ = load_yaml_text(tmp_path, text_out)
    fake.downloaded.clear()
    assert file_sources.resolve_files(params2) == dict()
    assert fake.downloaded == []
    # a missing file triggers a download of just that file
    os.remove(raw / expected[0])
    file_sources.resolve_files(params2)
    assert fake.downloaded == [expected[0]]


def test_resolve_skips_chained_and_local(tmp_path, monkeypatch):
    text = ('PATHS:\n'
            f'  RAWPATH: {tmp_path}\n'
            'GENERAL:\n'
            '  FILES:\n'
            '    filelist:\n'
            '    source: mast\n'
            '    pid: 1366\n'
            '    obsnumber: 1\n'
            '  FLATFILE: flat.fits\n')
    _, params, _ = load_yaml_text(tmp_path, text)

    def fail():
        raise AssertionError('MAST should not be used')
    monkeypatch.setattr(file_sources, '_get_mast_observations', fail)
    updates = file_sources.resolve_files(params, skip_keys=['GENERAL.FILES'])
    assert updates == dict()


def test_resolve_pogos_from_local_mirror(tmp_path):
    mirror = tmp_path / 'mirror' / 'soss'
    mirror.mkdir(parents=True)
    (mirror / 'flat.fits').write_text('flat')
    calib = tmp_path / 'calib'
    text = ('PATHS:\n'
            f'  CALIBPATH: {calib}\n'
            'GENERAL:\n'
            '  FLATFILE:\n'
            '    filelist: flat.fits\n'
            '    source: pogos\n'
            '    url: http://example.org/demos/soss/\n')
    _, params, yaml_file = load_yaml_text(tmp_path, text)
    rkwargs = dict(yaml_file=str(yaml_file),
                   demolocal=str(tmp_path / 'mirror'), demosymlink=True)
    updates = file_sources.resolve_files(params, **rkwargs)
    assert os.path.islink(calib / 'flat.fits')
    assert params['GENERAL.FLATFILE'] == 'flat.fits'
    assert params['GENERAL.FLATFILE'].fileobj.source == 'pogos'
    assert updates['GENERAL.FLATFILE']['source'] == 'pogos'


# =============================================================================
# Download cache
# =============================================================================
POGOS_FLAT = ('PATHS:\n'
              '  CALIBPATH: {calib}\n'
              'GENERAL:\n'
              '  FLATFILE:\n'
              '    filelist: flat.fits\n'
              '    source: pogos\n'
              '    url: http://example.org/demos/{subdir}/\n')


def fake_download(calls):
    """A download_url stand-in recording the urls it was asked for."""
    def _download(url, localpath):
        calls.append(url)
        with open(localpath, 'w') as handle:
            handle.write(url)
    return _download


def test_cache_directory_layout(tmp_path):
    pogos = ccc.FileObject(filelist='a.fits', source='pogos',
                           url='http://example.org/demos/soss/')
    mast = ccc.FileObject(source='mast', pid=1366, obsnumber=3)
    local = ccc.FileObject(filelist='a.fits')
    root = str(tmp_path)
    assert file_sources.cache_directory(root, pogos) == os.path.join(
        root, 'pogos', 'example.org', 'demos', 'soss')
    assert file_sources.cache_directory(root, mast) == os.path.join(
        root, 'mast', 'jw01366', 'o003')
    assert file_sources.cache_directory(root, local) is None
    assert file_sources.cache_directory(None, pogos) is None


def test_pogos_download_goes_to_cache_and_is_linked(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(file_sources, 'download_url', fake_download(calls))
    calib = tmp_path / 'calib'
    downloads = tmp_path / 'downloads'
    text = POGOS_FLAT.format(calib=calib, subdir='soss')
    _, params, _ = load_yaml_text(tmp_path, text)
    file_sources.resolve_files(params, download_dir=str(downloads))
    cached = downloads / 'pogos' / 'example.org' / 'demos' / 'soss'
    assert len(calls) == 1
    assert (cached / 'flat.fits').is_file()
    assert os.path.islink(calib / 'flat.fits')
    assert os.path.realpath(calib / 'flat.fits') == str(cached / 'flat.fits')
    # the record knows where it came from and who links to it
    meta = file_sources.read_cache_meta(str(downloads),
                                        str(cached / 'flat.fits'))
    assert meta['source'] == 'pogos'
    assert meta['origin'] == 'http://example.org/demos/soss/flat.fits'
    assert meta['links'] == {str(calib / 'flat.fits'): 'GENERAL.FLATFILE'}


def test_cached_file_is_linked_without_downloading(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(file_sources, 'download_url', fake_download(calls))
    downloads = tmp_path / 'downloads'
    # a first project downloads the file
    text1 = POGOS_FLAT.format(calib=tmp_path / 'p1', subdir='soss')
    _, params1, _ = load_yaml_text(tmp_path, text1)
    file_sources.resolve_files(params1, download_dir=str(downloads))
    # a second project (or a deleted run directory) reuses the cache
    text2 = POGOS_FLAT.format(calib=tmp_path / 'p2', subdir='soss')
    _, params2, _ = load_yaml_text(tmp_path, text2)
    assert file_sources.needs_download(params2['GENERAL.FLATFILE'].fileobj,
                                       str(tmp_path / 'p2'),
                                       str(downloads))
    file_sources.resolve_files(params2, download_dir=str(downloads))
    assert len(calls) == 1
    assert os.path.islink(tmp_path / 'p2' / 'flat.fits')


def test_link_only_never_downloads(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(file_sources, 'download_url', fake_download(calls))
    text = POGOS_FLAT.format(calib=tmp_path / 'calib', subdir='soss')
    _, params, _ = load_yaml_text(tmp_path, text)
    rkwargs = dict(download_dir=str(tmp_path / 'downloads'), link_only=True)
    assert file_sources.resolve_files(params, **rkwargs) == dict()
    assert calls == []
    assert not os.path.lexists(tmp_path / 'calib' / 'flat.fits')


def test_same_name_different_url_never_clash(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(file_sources, 'download_url', fake_download(calls))
    downloads = tmp_path / 'downloads'
    calib = tmp_path / 'calib'
    for subdir in ['soss', 'nirspec']:
        text = POGOS_FLAT.format(calib=calib, subdir=subdir)
        _, params, _ = load_yaml_text(tmp_path, text)
        file_sources.resolve_files(params, download_dir=str(downloads))
    # both are cached separately ...
    base = downloads / 'pogos' / 'example.org' / 'demos'
    assert (base / 'soss' / 'flat.fits').read_text().endswith(
        'soss/flat.fits')
    assert (base / 'nirspec' / 'flat.fits').read_text().endswith(
        'nirspec/flat.fits')
    # ... and the changed url relinked the stale link
    assert os.path.realpath(calib / 'flat.fits') == str(
        base / 'nirspec' / 'flat.fits')


def test_name_clash_between_parameters_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(file_sources, 'download_url', fake_download([]))
    calib = tmp_path / 'calib'
    text = (POGOS_FLAT.format(calib=calib, subdir='soss')
            + '  WAVE_FILE:\n'
              '    filelist: flat.fits\n'
              '    source: pogos\n'
              '    url: http://example.org/demos/other/\n')
    _, params, _ = load_yaml_text(tmp_path, text)
    with pytest.raises(file_sources.FileSourceError, match='clash'):
        file_sources.resolve_files(params,
                                   download_dir=str(tmp_path / 'dl'))


def test_local_mirror_copy_goes_to_cache(tmp_path):
    mirror = tmp_path / 'mirror' / 'soss'
    mirror.mkdir(parents=True)
    (mirror / 'flat.fits').write_text('flat')
    downloads = tmp_path / 'downloads'
    calib = tmp_path / 'calib'
    text = POGOS_FLAT.format(calib=calib, subdir='soss')
    _, params, _ = load_yaml_text(tmp_path, text)
    rkwargs = dict(demolocal=str(tmp_path / 'mirror'),
                   download_dir=str(downloads))
    file_sources.resolve_files(params, **rkwargs)
    cached = downloads / 'pogos' / 'example.org' / 'demos' / 'soss'
    assert (cached / 'flat.fits').read_text() == 'flat'
    assert os.path.realpath(calib / 'flat.fits') == str(cached / 'flat.fits')
    meta = file_sources.read_cache_meta(str(downloads),
                                        str(cached / 'flat.fits'))
    assert meta['source'] == 'local'


def test_local_mirror_symlink_skips_cache(tmp_path):
    mirror = tmp_path / 'mirror' / 'soss'
    mirror.mkdir(parents=True)
    (mirror / 'flat.fits').write_text('flat')
    downloads = tmp_path / 'downloads'
    calib = tmp_path / 'calib'
    text = POGOS_FLAT.format(calib=calib, subdir='soss')
    _, params, _ = load_yaml_text(tmp_path, text)
    rkwargs = dict(demolocal=str(tmp_path / 'mirror'), demosymlink=True,
                   download_dir=str(downloads))
    file_sources.resolve_files(params, **rkwargs)
    assert os.path.realpath(calib / 'flat.fits') == str(mirror / 'flat.fits')
    assert not downloads.exists()


def test_deleted_cache_file_is_downloaded_again(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(file_sources, 'download_url', fake_download(calls))
    downloads = tmp_path / 'downloads'
    calib = tmp_path / 'calib'
    text = POGOS_FLAT.format(calib=calib, subdir='soss')
    _, params, _ = load_yaml_text(tmp_path, text)
    file_sources.resolve_files(params, download_dir=str(downloads))
    os.remove(os.path.realpath(calib / 'flat.fits'))
    file_sources.resolve_files(params, download_dir=str(downloads))
    assert len(calls) == 2
    assert (calib / 'flat.fits').is_file()


def test_mast_uses_cache(tmp_path, monkeypatch):
    raw1, raw2 = tmp_path / 'raw1', tmp_path / 'raw2'
    downloads = tmp_path / 'downloads'
    fake = FakeObservations(['a-seg001_rateints.fits',
                             'a-seg002_rateints.fits'])
    monkeypatch.setattr(file_sources, '_get_mast_observations', lambda: fake)
    for raw in [raw1, raw2]:
        text = ('PATHS:\n'
                f'  RAWPATH: {raw}\n'
                'GENERAL:\n'
                '  FILES:\n'
                '    filelist:\n'
                '    source: mast\n'
                '    pid: 1366\n'
                '    obsnumber: 1\n')
        _, params, _ = load_yaml_text(tmp_path, text)
        file_sources.resolve_files(params, download_dir=str(downloads))
    # downloaded once, linked into both directories
    assert sorted(fake.downloaded) == ['a-seg001_rateints.fits',
                                       'a-seg002_rateints.fits']
    cached = downloads / 'mast' / 'jw01366' / 'o001'
    for raw in [raw1, raw2]:
        assert os.path.realpath(raw / 'a-seg001_rateints.fits') == str(
            cached / 'a-seg001_rateints.fits')
    meta = file_sources.read_cache_meta(
        str(downloads), str(cached / 'a-seg001_rateints.fits'))
    assert meta['source'] == 'mast'
    assert set(meta['links'].values()) == {'GENERAL.FILES'}
    assert len(meta['links']) == 2


def test_single_file_constant_rejects_many_mast_files(tmp_path, monkeypatch):
    text = ('PATHS:\n'
            f'  CALIBPATH: {tmp_path}\n'
            'GENERAL:\n'
            '  FLATFILE:\n'
            '    filelist:\n'
            '    source: mast\n'
            '    pid: 1366\n'
            '    obsnumber: 1\n'
            '    product: x1dints\n')
    _, params, _ = load_yaml_text(tmp_path, text)
    fake = FakeObservations(['a-seg001_x1dints.fits',
                             'a-seg002_x1dints.fits'])
    monkeypatch.setattr(file_sources, '_get_mast_observations', lambda: fake)
    with pytest.raises(file_sources.FileSourceError, match='single file'):
        file_sources.resolve_files(params)


def test_mast_exposure_level_observation_fallback():
    """Observations without level 3 obs_ids match jw{pid}{obs} ids."""
    class ExposureOnly(FakeObservations):
        def query_criteria(self, obs_collection=None, proposal_id=None):
            return Table(dict(obs_id=['jw01366001001_03101_00001-seg001',
                                      'jw01366001001_03101_00001-seg002',
                                      'jw01366002001_03101_00001-seg001']))

        def get_product_list(self, observations):
            assert len(observations) == 2
            return Table(dict(productFilename=self.filenames,
                              size=self.sizes))

    fake = ExposureOnly(['a-seg001_uncal.fits', 'a-seg002_uncal.fits'])
    fileobj = ccc.FileObject(source='mast', pid=1366, obsnumber=1,
                             product='uncal', name='FILES')
    table = file_sources.mast_product_table(fileobj, fake)
    assert len(table) == 2


def test_mast_match_and_min_size_filters():
    """match and min_size_mb (set in the yaml mapping) filter products."""
    fake = FakeObservations(['a_nrs1_rateints.fits', 'a_nrs2_rateints.fits',
                             'small_nrs1_rateints.fits'],
                            sizes=[5e6, 5e6, 5e5])
    files = make_cdict().get('GENERAL.FILES')
    value = files.validate(dict(filelist=None, source='mast', pid=1366,
                                obsnumber=1, match=['nrs1'],
                                min_size_mb=1))
    table = file_sources.mast_product_table(value.fileobj, fake)
    assert list(table['productFilename']) == ['a_nrs1_rateints.fits']
    # without match / min_size_mb: every product above the 1 MB default
    value = files.validate(dict(filelist=None, source='mast', pid=1366,
                                obsnumber=1, min_size_mb=0))
    table = file_sources.mast_product_table(value.fileobj, fake)
    assert len(table) == 3


def test_product_for_every_source():
    """product is the kind of file (any source), checked against options."""
    cdict = ConstantsDict('test')
    cdict.addc('WAVE', value=None, dtype=str, source='test', group='G',
               allow_list=True, const_class=ccc.FileObjectConst,
               product='x1dints', product_options=['x1dints', 'fits'])
    wave = cdict.get('G.WAVE')
    # plain values use the default product (and stay plain in yaml)
    params = {'G.WAVE': wave.validate('w.fits')}
    assert ccc.get_file_product(params, 'G.WAVE', 'x1dints') == 'x1dints'
    assert wave.yaml_value(params['G.WAVE']) == 'w.fits'
    # a non default product is kept (and written in the mapping form)
    value = wave.validate(dict(filelist='w.fits', product='fits'))
    assert ccc.get_file_product({'G.WAVE': value}, 'G.WAVE') == 'fits'
    assert wave.yaml_value(value)['product'] == 'fits'
    value = wave.validate(dict(filelist='w.fits', source='pogos',
                               url='http://x/', product='fits'))
    assert value.fileobj.product == 'fits'
    # set_file_product on a plain value
    params = {'G.WAVE': 'w.fits'}
    ccc.set_file_product(params, 'G.WAVE', 'fits')
    assert params['G.WAVE'] == 'w.fits'
    assert ccc.get_file_product(params, 'G.WAVE') == 'fits'
    # products outside the options are rejected
    with pytest.raises(ccc.AperoConstantError, match='product'):
        wave.validate(dict(filelist='w.fits', product='rateints'))
