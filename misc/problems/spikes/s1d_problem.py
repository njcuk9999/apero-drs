import numpy as np
import warnings
from scipy.interpolate import InterpolatedUnivariateSpline

from astropy.table import Table
from astropy.io import fits

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'e2ds_test'
speed_of_light_kms = 299792.458


# =============================================================================
# Define s1d functions
# =============================================================================
def e2ds_to_s1d(wavemap, e2ds, blaze, fiber=None, wgrid='wave', kind=None,
                **kwargs):
    func_name = __NAME__ + '.e2ds_to_s1d()'
    # get parameters from p
    params = None
    # wavestart = pcheck(params, 'EXT_S1D_WAVESTART', 'wavestart', kwargs,
    #                    func_name)
    wavestart = 965
    # waveend = pcheck(params, 'EXT_S1D_WAVEEND', 'waveend', kwargs,
    #                  func_name)
    waveend = 2500
    # binwave = pcheck(params, 'EXT_S1D_BIN_UWAVE', 'binwave', kwargs,
    #                  func_name)
    binwave = 0.005
    # binvelo = pcheck(params, 'EXT_S1D_BIN_UVELO', 'binvelo', kwargs,
    #                  func_name)
    binvelo = 1.0
    # smooth_size = pcheck(params, 'EXT_S1D_EDGE_SMOOTH_SIZE', 'smooth_size',
    #                      kwargs, func_name)
    smooth_size = 20
    # blazethres = pcheck(params, 'TELLU_CUT_BLAZE_NORM', 'blazethres', kwargs,
    #                     func_name)
    blazethres = 0.2

    # get size from e2ds
    nord, npix = e2ds.shape

    # log progress: calculating s1d (wavegrid)
    WLOG(params, '', TextEntry('40-016-00009', args=[wgrid]))

    # -------------------------------------------------------------------------
    # Decide on output wavelength grid
    # -------------------------------------------------------------------------
    if wgrid == 'wave':
        wavegrid = np.arange(wavestart, waveend + binwave / 2.0, binwave)
    else:
        # work out number of wavelength points
        flambda = np.log(waveend / wavestart)
        nlambda = np.round((speed_of_light_kms / binvelo) * flambda)
        # updating end wavelength slightly to have exactly 'step' km/s
        waveend = np.exp(nlambda * (binvelo / speed_of_light_kms)) * wavestart
        # get the wavegrid
        index = np.arange(nlambda) / nlambda
        wavegrid = wavestart * np.exp(index * np.log(waveend / wavestart))

    # -------------------------------------------------------------------------
    # define a smooth transition mask at the edges of the image
    # this ensures that the s1d has no discontinuity when going from one order
    # to the next. We define a scale for this mask
    # smoothing scale
    # -------------------------------------------------------------------------
    # define a kernal that goes from -3 to +3 smooth_sizes of the mask
    xker = np.arange(-smooth_size * 3, smooth_size * 3, 1)
    ker = np.exp(-0.5 * (xker / smooth_size) ** 2)
    # set up the edge vector
    edges = np.ones(npix, dtype=bool)
    # set edges of the image to 0 so that  we get a sloping weight
    edges[:int(3 * smooth_size)] = False
    edges[-int(3 * smooth_size):] = False
    # define the weighting for the edges (slopevector)
    slopevector = np.zeros_like(blaze)
    # for each order find the sloping weight vector
    for order_num in range(nord):
        # get the blaze for this order
        oblaze = np.array(blaze[order_num])
        # find the valid pixels
        cond1 = np.isfinite(oblaze) & np.isfinite(e2ds[order_num])
        with warnings.catch_warnings(record=True) as _:
            cond2 = oblaze > (blazethres * np.nanmax(oblaze))
        valid = cond1 & cond2 & edges
        # convolve with the edge kernel
        oweight = np.convolve(valid, ker, mode='same')
        # normalise to the maximum
        with warnings.catch_warnings(record=True) as _:
            oweight = oweight - np.nanmin(oweight)
            oweight = oweight / np.nanmax(oweight)
        # append to sloping vector storage
        slopevector[order_num] = oweight

    # multiple the spectrum and blaze by the sloping vector
    sblaze = np.array(blaze) * slopevector
    se2ds = np.array(e2ds) * slopevector

    # -------------------------------------------------------------------------
    # Perform a weighted mean of overlapping orders
    # by performing a spline of both the blaze and the spectrum
    # -------------------------------------------------------------------------
    out_spec = np.zeros_like(wavegrid)
    weight = np.zeros_like(wavegrid)

    # loop around all orders
    for order_num in range(nord):
        # identify the valid pixels
        valid = np.isfinite(se2ds[order_num]) & np.isfinite(sblaze[order_num])
        valid_float = valid.astype(float)
        # if we have no valid points we need to skip
        if np.sum(valid) == 0:
            continue
        # get this orders vectors
        owave = wavemap[order_num]
        oe2ds = se2ds[order_num, valid]
        oblaze = sblaze[order_num, valid]
        # create the splines for this order
        spline_sp = iuv_spline(owave[valid], oe2ds, k=5, ext=1)
        spline_bl = iuv_spline(owave[valid], oblaze, k=5, ext=1)
        spline_valid = iuv_spline(owave, valid_float, k=1, ext=1)
        # can only spline in domain of the wave
        useful_range = (wavegrid > np.nanmin(owave[valid]))
        useful_range &= (wavegrid < np.nanmax(owave[valid]))
        # finding pixels where we have immediate neighbours that are
        #   considered valid in the spline (to avoid interpolating over large
        #   gaps in validity)
        maskvalid = np.zeros_like(wavegrid, dtype=bool)
        maskvalid[useful_range] = spline_valid(wavegrid[useful_range]) > 0.9
        useful_range &= maskvalid
        # get splines and add to outputs
        weight[useful_range] += spline_bl(wavegrid[useful_range])
        out_spec[useful_range] += spline_sp(wavegrid[useful_range])

    # need to deal with zero weight --> set them to NaNs
    zeroweights = weight == 0
    weight[zeroweights] = np.nan

    # plot the s1d weight/before/after plot
    # recipe.plot('EXTRACT_S1D_WEIGHT', params=params, wave=wavegrid,
    #             flux=out_spec, weight=weight, kind=wgrid, fiber=fiber,
    #             stype=kind)
    # work out the weighted spectrum
    with warnings.catch_warnings(record=True) as _:
        w_out_spec = out_spec / weight

    # TODO: propagate errors
    ew_out_spec = np.zeros_like(w_out_spec)

    # construct the s1d table (for output)
    s1dtable = Table()
    s1dtable['wavelength'] = wavegrid
    s1dtable['flux'] = w_out_spec
    s1dtable['eflux'] = ew_out_spec
    s1dtable['weight'] = weight

    # set up return dictionary
    # props = ParamDict()
    props = dict()
    # add data
    props['WAVEGRID'] = wavegrid
    props['S1D'] = w_out_spec
    props['S1D_ERROR'] = ew_out_spec
    props['WEIGHT'] = weight
    # add astropy table
    props['S1DTABLE'] = s1dtable
    # add constants
    props['WAVESTART'] = wavestart
    props['WAVEEND'] = waveend
    props['WAVEKIND'] = wgrid
    if wgrid == 'wave':
        props['BIN_WAVE'] = binwave
        props['BIN_VELO'] = 'None'
    else:
        props['BIN_WAVE'] = 'None'
        props['BIN_VELO'] = binvelo
    props['SMOOTH_SIZE'] = smooth_size
    props['BLAZE_THRES'] = blazethres
    # add source
    # keys = ['WAVEGRID', 'S1D', 'WEIGHT', 'S1D_ERROR', 'S1DTABLE',
    #         'WAVESTART', 'WAVEEND', 'WAVEKIND', 'BIN_WAVE',
    #         'BIN_VELO', 'SMOOTH_SIZE', 'BLAZE_THRES']
    # props.set_sources(keys, func_name)
    # return properties
    return props


# proxy WLOG function
def WLOG(params, level, message):
    if level == '':
        print(message)
    else:
        print('{0}: {1}'.format(level, message))


# proxy TextEntry function
def TextEntry(code, args=None):
    return 'CODE[{0}]'.format(code)


# iuv spline from math.general.py
def iuv_spline(x, y, **kwargs):
    # deal with dimensions error (on k)
    #   otherwise get   dfitpack.error: (m>k) failed for hidden m
    if kwargs.get('k', None) is not None:
        if len(x) < (kwargs['k'] + 1):
            # raise exception if len(x) is bad
            emsg = ('IUV Spline len(x) < k+1 '
                    '\n\tk={0}\n\tlen(x) = {1}'
                    '\n\tx={2}\n\ty={3}')
            eargs = [kwargs['k'], len(x), str(x)[:70], str(y)[:70]]
            # raise DrsMathException(emsg.format(*eargs))
            raise ValueError(emsg.format(*eargs))
    # copy x and y
    x, y = np.array(x), np.array(y)
    # find all NaN values
    nanmask = ~np.isfinite(y)

    if np.sum(~nanmask) < 2:
        y = np.zeros_like(x)
    elif np.sum(nanmask) == 0:
        pass
    else:
        # replace all NaN's with linear interpolation
        badspline = InterpolatedUnivariateSpline(x[~nanmask], y[~nanmask],
                                                 k=1, ext=1)
        y[nanmask] = badspline(x[nanmask])
    # return spline
    return InterpolatedUnivariateSpline(x, y, **kwargs)


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # TODO: get wavemap
    wavemap = None
    # TODO: get e2ds file or telluric corrected
    e2ds = None
    # TODO: set the kind
    kind = 'E2DSFF'
    # kind = 'TCORR'
    # TODO: set the fiber
    fiber = 'AB'
    # TODO: get blaze file
    blaze = None
    # ----------------------------------------------------------------------
    # create 1d spectra (s1d) of the e2ds file
    swprops = e2ds_to_s1d(wavemap, e2ds, blaze, wgrid='wave', fiber=fiber,
                          kind=kind)
    svprops = e2ds_to_s1d(wavemap, e2ds, blaze, wgrid='velocity', fiber=fiber,
                          kind=kind)
    # ----------------------------------------------------------------------
    # TODO: save files



# =============================================================================
# End of code
# =============================================================================