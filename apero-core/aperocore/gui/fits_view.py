#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FITS viewing helpers for browser guis

    - fits_info: the HDU list (name, type, shape, columns) and the headers
    - image_png: a png preview of an image HDU (2D, or one plane of a
      cube) with zscale / percentile / minmax scaling
    - table_rows: a page of rows of a table HDU

astropy and matplotlib are imported lazily (only when a FITS file is
viewed) so importing the gui stays fast.

Created on 2026-11-26

@author: cook
"""
import io
import math
from typing import Any, Dict, List

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.gui.fits_view.py'
# maximum preview size (pixels) along either axis (larger images binned)
PREVIEW_MAX = 1024
# maximum number of table rows per request
TABLE_MAX_ROWS = 1000
# allowed colour maps
CMAPS = ['gray', 'viridis', 'magma', 'inferno', 'plasma', 'cividis']
# allowed scalings
SCALES = ['zscale', 'p99', 'p95', 'minmax', 'log']


# =============================================================================
# Define classes
# =============================================================================
class FitsViewError(Exception):
    """Raised when a FITS preview cannot be produced"""


# =============================================================================
# Define functions
# =============================================================================
def _card_value(value: Any) -> Any:
    """
    Convert a header value to something json can hold

    :param value: Any, the header value

    :return: Any, a bool/int/float/str value
    """
    if isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else str(value)
    return str(value)


def fits_info(path: str) -> Dict[str, Any]:
    """
    Get the HDU list and headers of a FITS file

    :param path: str, the FITS file

    :return: dict(path, hdus=list, error) - each hdu is dict(index, name,
             type, shape, dtype, columns, header=list of [key, value,
             comment], image=bool, table=bool)
    """
    out: Dict[str, Any] = dict(path=path, hdus=[], error=None)
    try:
        from astropy.io import fits
    except ImportError as error:
        out['error'] = 'astropy is not available: {0}'.format(error)
        return out
    try:
        with fits.open(path, memmap=True, lazy_load_hdus=False) as hdulist:
            for index, hdu in enumerate(hdulist):
                header = [[card.keyword, _card_value(card.value),
                           str(card.comment)] for card in hdu.header.cards]
                is_table = isinstance(hdu, (fits.BinTableHDU,
                                            fits.TableHDU))
                shape = None
                dtype = None
                columns: List[Dict[str, Any]] = []
                if is_table:
                    shape = [int(hdu.header.get('NAXIS2', 0))]
                    columns = [dict(name=col.name, format=str(col.format),
                                    unit=str(col.unit or ''))
                               for col in hdu.columns]
                elif hdu.header.get('NAXIS', 0) > 0:
                    # shape from the header (no data read)
                    naxis = int(hdu.header['NAXIS'])
                    shape = [int(hdu.header.get('NAXIS{0}'.format(it), 0))
                             for it in range(naxis, 0, -1)]
                    dtype = 'BITPIX={0}'.format(hdu.header.get('BITPIX'))
                is_image = (not is_table and shape is not None
                            and len(shape) >= 2)
                out['hdus'].append(dict(index=index, name=hdu.name,
                                        type=type(hdu).__name__,
                                        shape=shape, dtype=dtype,
                                        columns=columns, header=header,
                                        image=is_image, table=is_table))
    except Exception as error:
        out['error'] = '{0}: {1}'.format(type(error).__name__, error)
    return out


def _limits(data: Any, scale: str) -> List[float]:
    """
    Get the display limits of an image

    :param data: numpy array, the finite pixel values (1D)
    :param scale: str, one of SCALES

    :return: list, [vmin, vmax]
    """
    # deferred import (only needed when an image is viewed)
    from aperocore import math as mp
    if scale == 'zscale':
        try:
            from astropy.visualization import ZScaleInterval
            vmin, vmax = ZScaleInterval().get_limits(data)
            return [float(vmin), float(vmax)]
        except Exception as _:
            scale = 'p99'
    if scale == 'p95':
        return [float(v) for v in mp.nanpercentile(data, [2.5, 97.5])]
    if scale == 'minmax':
        return [float(mp.nanmin(data)), float(mp.nanmax(data))]
    # p99 and log
    return [float(v) for v in mp.nanpercentile(data, [0.5, 99.5])]


def image_png(path: str, hdu: int = 0, plane: int = 0,
              scale: str = 'zscale', cmap: str = 'gray') -> bytes:
    """
    Render a png preview of an image HDU

    :param path: str, the FITS file
    :param hdu: int, the HDU index
    :param plane: int, the plane of a cube (first axes beyond 2D are
                  flattened into planes)
    :param scale: str, one of SCALES
    :param cmap: str, one of CMAPS

    :raises FitsViewError: if the HDU is not an image or cannot be read

    :return: bytes, the png image
    """
    # deferred imports (only needed when an image is viewed)
    import numpy as np
    from astropy.io import fits
    import matplotlib
    from aperocore import math as mp
    matplotlib.use('Agg')
    from matplotlib import pyplot as plt
    if scale not in SCALES:
        scale = 'zscale'
    if cmap not in CMAPS:
        cmap = 'gray'
    try:
        with fits.open(path, memmap=True) as hdulist:
            if not 0 <= hdu < len(hdulist):
                raise FitsViewError('no HDU {0}'.format(hdu))
            data = hdulist[hdu].data
            if data is None or getattr(data, 'ndim', 0) < 2:
                raise FitsViewError('HDU {0} is not an image'.format(hdu))
            if isinstance(hdulist[hdu], (fits.BinTableHDU, fits.TableHDU)):
                raise FitsViewError('HDU {0} is a table'.format(hdu))
            # cubes: flatten leading axes into planes
            if data.ndim > 2:
                cube = data.reshape((-1,) + data.shape[-2:])
                plane = min(max(0, plane), cube.shape[0] - 1)
                image = np.array(cube[plane], dtype=float)
                nplanes = cube.shape[0]
            else:
                image = np.array(data, dtype=float)
                nplanes = 1
    except FitsViewError:
        raise
    except Exception as error:
        raise FitsViewError('{0}: {1}'.format(type(error).__name__, error))
    # bin large images down (block mean, each axis on its own) so the
    #   preview stays small
    fy = int(math.ceil(image.shape[0] / PREVIEW_MAX))
    fx = int(math.ceil(image.shape[1] / PREVIEW_MAX))
    factor = max(fy, fx)
    if factor > 1:
        ny = (image.shape[0] // fy) * fy
        nx = (image.shape[1] // fx) * fx
        block = image[:ny, :nx].reshape(ny // fy, fy, nx // fx, fx)
        with np.errstate(invalid='ignore'):
            image = mp.nanmean(mp.nanmean(block, axis=3), axis=1)
    finite = image[np.isfinite(image)]
    if finite.size == 0:
        raise FitsViewError('image has no finite values')
    if scale == 'log':
        # shift to positive values before the log
        offset = mp.nanmin(finite)
        image = np.log10(image - offset + 1.0)
        finite = image[np.isfinite(image)]
    vmin, vmax = _limits(finite, scale)
    # draw the image with a colour bar
    height, width = image.shape
    aspect = height / max(width, 1)
    fig_width = 8.0
    fig_height = min(max(2.5, fig_width * aspect * 0.9), 12.0)
    fig = plt.figure(figsize=(fig_width, fig_height), dpi=100)
    try:
        frame = fig.add_subplot(111)
        shown = frame.imshow(image, origin='lower', cmap=cmap, vmin=vmin,
                             vmax=vmax, aspect='auto',
                             interpolation='nearest')
        fig.colorbar(shown, ax=frame, fraction=0.04, pad=0.02)
        title = 'HDU {0}'.format(hdu)
        if nplanes > 1:
            title += '  plane {0}/{1}'.format(plane + 1, nplanes)
        if factor > 1:
            title += '  (binned {0}x{1})'.format(fx, fy)
        frame.set_title(title + '  [{0}]'.format(scale), fontsize=10)
        fig.tight_layout()
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png')
    finally:
        plt.close(fig)
    return buffer.getvalue()


def table_rows(path: str, hdu: int = 1, start: int = 0,
               nrows: int = 100) -> Dict[str, Any]:
    """
    Get a page of rows of a table HDU

    :param path: str, the FITS file
    :param hdu: int, the HDU index
    :param start: int, the first row
    :param nrows: int, the number of rows (at most TABLE_MAX_ROWS)

    :raises FitsViewError: if the HDU is not a table

    :return: dict(columns, rows, start, total)
    """
    import numpy as np
    from astropy.io import fits
    nrows = min(max(1, nrows), TABLE_MAX_ROWS)
    try:
        with fits.open(path, memmap=True) as hdulist:
            if not 0 <= hdu < len(hdulist):
                raise FitsViewError('no HDU {0}'.format(hdu))
            table = hdulist[hdu]
            if not isinstance(table, (fits.BinTableHDU, fits.TableHDU)):
                raise FitsViewError('HDU {0} is not a table'.format(hdu))
            total = len(table.data)
            start = min(max(0, start), max(0, total - 1))
            chunk = table.data[start:start + nrows]
            columns = list(table.columns.names)
            rows = []
            for record in chunk:
                row = []
                for value in record:
                    # arrays in a cell are summarised
                    if isinstance(value, np.ndarray):
                        row.append('array{0}'.format(list(value.shape)))
                    elif isinstance(value, (bytes, np.bytes_)):
                        row.append(value.decode(errors='replace'))
                    elif isinstance(value, (np.floating, float)):
                        fvalue = float(value)
                        row.append(fvalue if math.isfinite(fvalue)
                                   else str(fvalue))
                    elif isinstance(value, (np.integer, int)):
                        row.append(int(value))
                    else:
                        row.append(str(value))
                rows.append(row)
    except FitsViewError:
        raise
    except Exception as error:
        raise FitsViewError('{0}: {1}'.format(type(error).__name__, error))
    return dict(columns=columns, rows=rows, start=start, total=total)


# =============================================================================
# End of code
# =============================================================================
