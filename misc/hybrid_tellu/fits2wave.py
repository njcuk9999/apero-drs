import numpy as np
from astropy.io import fits


def fits2wave(file_or_header):
    info = """
        Provide a fits header or a fits file
        and get the corresponding wavelength
        grid from the header.
        
        Usage :
          wave = fits2wave(hdr)
                  or
          wave = fits2wave('my_e2ds.fits')
        
        Output has the same size as the input
        grid. This is derived from NAXIS 
        values in the header
    """


    # check that we have either a fits file or an astropy header
    if type(file_or_header) == str:
        hdr = fits.getheader(file_or_header)
    elif str(type(file_or_header)) == "<class 'astropy.io.fits.header.Header'>":
        hdr = file_or_header
    else:
        print()
        print('~~~~ wrong type of input ~~~~')
        print()

        print(info)
        return []

    # get the keys with the wavelength polynomials
    wave_hdr = hdr['WAVE0*']
    # concatenate into a numpy array
    wave_poly = np.array([wave_hdr[i] for i in range(len(wave_hdr))])

    # get the number of orders
    nord = hdr['WAVEORDN']

    # get the per-order wavelength solution
    wave_poly = wave_poly.reshape(nord, len(wave_poly) // nord)

    # get the length of each order (normally that's 4088 pix)
    npix = hdr['NAXIS1']

    # project polynomial coefficiels
    wavesol = [np.polyval(wave_poly[i][::-1],np.arange(npix)) for i in range(nord) ]

    # return wave grid
    return np.array(wavesol)
