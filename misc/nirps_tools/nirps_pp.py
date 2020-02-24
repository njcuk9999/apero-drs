import numpy as np
from astropy.io import fits
#import matplotlib.pyplot as plt
import os
from scipy.ndimage import zoom
import glob

def rot8(im,nrot):
    """
    Rotation of a 2d image with the 8 possible geometries. Rotation 0-3
    do not flip the image, 4-7 perform a flip

    nrot = 0 -> same as input
    nrot = 1 -> 90deg counter-clock-wise
    nrot = 2 -> 180deg
    nrot = 3 -> 90deg clock-wise
    nrot = 4 -> flip top-bottom
    nrot = 5 -> flip top-bottom and rotate 90 deg counter-clock-wise
    nrot = 6 -> flip top-bottom and rotate 180 deg
    nrot = 7 -> flip top-bottom and rotate 90 deg clock-wise
    nrot >=8 -> performs a modulo 8 anyway

    :param im: input image
    :param nrot: integer between 0 and 7
    :return: rotated and/or flipped image
    """
    nrot = int(nrot % 8)
    return np.rot90( im[::1-2*(nrot//4)],nrot % 4 )

def med32(im):
    # input image MUST be 4096x4096
    # and have 32 amplifiers with a mirror
    # odd/even symmetry. We fold the image
    # into a 32x4096x128 cube where odd amplifiers
    # are flipped left/right. The median
    # amplifier structure is then re-padded
    # in an image that maps amp x-talk.
    # We expect the orders to be masked with NaNs
    # and the image to be high-passed so that only
    # high-frequency structures are left here.

    # cube to contain ordres in an easily
    # managed form
    cube = np.zeros([32, 4096, 128])
    for i in range(32):
        if (i % 2) == 0: # for left/right flipping
            i1 = i * 128
            i2 = i * 128 + 128
            sig = 1
        else:
            i1 = i * 128 + 127
            i2 = i * 128 -1
            sig = -1

        cube[i, :, :] = im[:, i1:i2:sig]
    # derive median amplifier structure
    med = np.nanmedian(cube, axis=0)


    # pad back onto the output image
    im2 = np.zeros_like(im)
    for i in range(32): # unflip
        if (i % 2) == 0: # for left/right flipping
            i1 = i * 128
            i2 = i * 128 + 128
            sig = 1
        else:
            i1 = i * 128 + 127
            i2 = i * 128 -1
            sig = -1

        im2[:, i1:i2:sig] = med
    return im2

def medbin(im,bx,by):
    # median-bin an image to a given size through
    # some funny np.reshape. To be used for low-pass
    # filterning of an image.
    sz = np.shape(im)
    # TODO: Question: bx, sz0/bx, by, sz1/bx    ---- shouldn't it be sz1/by
    # TODO: Question: are "bx" and "by" the right way around?
    out = np.nanmedian(np.nanmedian(im.reshape([bx,sz[0]//bx,by, sz[1]//bx]), axis=1), axis=2)
    return out

def mk_mask():
    # creation of the mask image
    im_flat = 'SIMU_NIRPS_HA_3f(flat_flat).fits'
    im = fits.getdata(im_flat)
    # find pixel that are more than 10 absolute deviations
    # from the image median
    im -= np.nanmedian(im)

    sig = np.nanmedian(np.abs(im))

    # generate a first estimate of the mask
    mask = im>10*sig
    # now apply a proper filtering of the image
    im2 = np.array(im)
    im2[mask] = np.nan

    ################################################
    # Same code as for an individual science frame #
    ################################################

    # median-bin and expand back to original size
    binsize = 32
    lowf = zoom(medbin(im2, binsize, binsize), 4096 // binsize)

    # subtract low-frequency from masked image
    im2 -= lowf
    # find the amplifier x-talk map
    xtalk = med32(im2)

    # subtract both low-frequency and x-talk from input image
    im -= (lowf + xtalk)

    # generate a better estimate of the mask
    # TODO: Question: Why are we not re-calculating sig after correction
    mask = im>10*sig

    fits.writeto('mask.fits',np.array(mask,dtype = int), overwrite = True)

    return []

def nirps_pp(files):

    ref_hdr = fits.getheader('ref_hdr.fits')

    if type(files) == str:
        files = glob.glob(files)

    for file in files:
        outname = '_pp.'.join(file.split('.'))

        if '_pp.' in file:
            print(file+' is a _pp file')
            continue

        if os.path.isfile(outname):
            print('File : '+outname +' exists')
            continue
        else:
            print('We pre-process '+file)

            hdr = fits.getheader(file)
            im = fits.getdata(file)

            # TODO: Question: Do we have to generate one of these every night
            # TODO: Question: Or how often
            # TODO: Question:    This will change how we access/create this file
            mask = np.array(fits.getdata('mask.fits'),dtype = bool)

            im2 = np.array(im)
            im2[mask] = np.nan

            # we find the low level frequencies
            # we bin in regions of 32x32 pixels. This CANNOT be
            # smaller than the order footprint on the array
            # as it would lead to a set of NaNs in the downsized
            # image and chaos afterward
            binsize = 32 # pixels


            # TODO: Question: Why don't we test for corrupt files?

            # TODO: Question: Why don't we do ref_top_bottom

            # median-bin and expand back to original size
            lowf = zoom(medbin(im2,binsize,binsize),4096//binsize)

            # subtract low-frequency from masked image
            im2 -= lowf

            # find the amplifier x-talk map
            xtalk = med32(im2)
            im2 -= xtalk

            # subtract both low-frequency and x-talk from input image
            im -= (lowf+xtalk)

            tmp = np.nanmedian(im2,axis=0)

            im -= np.tile(tmp, 4096).reshape(4096, 4096)

            # rotates the image so that it matches the order geometry of SPIRou and HARPS
            # redder orders at the bottom and redder wavelength within each order on the left

            # NIRPS = 5
            # SPIROU = 3
            im = rot8(im,5)

            #DPRTYPE
            """
            MJDMID  =    58875.10336167315 / Mid Observation time [mjd]                     
            BERVOBSM= 'header  '           / BERV method used to calc observation time      
            DPRTYPE = 'FP_FP   '           / The type of file (from pre-process)            
            PVERSION= '0.6.029 '           / DRS Pre-Processing version                     
            DRSVDATE= '2020-01-27'         / DRS Release date                               
            DRSPDATE= '2020-01-30 22:16:00.344' / DRS Processed date                        
            DRSPID  = 'PID-00015804225603440424-JKBM' / The process ID that outputted this f
            INF1000 = '2466774a.fits'      / Input file used to create output infile=0      
            QCC001N = 'snr_hotpix'         / All quality control passed                     
            QCC001V =    876.2474157597072 / All quality control passed                     
            QCC001L = 'snr_hotpix < 1.00000e+01' / All quality control passed               
            QCC001P =                    1 / All quality control passed                     
            QCC002N = 'max(rms_list)'      / All quality control passed                     
            QCC002V = 0.002373232122258537 / All quality control passed                     
            QCC002L = 'max(rms_list) > 1.5000e-01' / All quality control passed             
            QCC002P =                    1 / All quality control passed                     
            QCC_ALL =                    T                                                  
            DETOFFDX=                    0 / Pixel offset in x from readout lag             
            DETOFFDY=                    0 / Pixel offset in y from readout lag    

            """

            if 'MJDEND' not in hdr:
                hdr['MJDEND'] = 0.00
                hdr['EXPTIME'] = 5.57*len(hdr['INTT*'])

            hdr['MJDMID'] = hdr['MJDEND'] - hdr['EXPTIME']/2.0/86400.0

            hdr['INF1000'] = file
            DPRTYPES = ['DARK_DARK','DARK_FP','FLAT_FLAT','DARK_FLAT',
                        'FLAT_DARK','HC_FP','FP_HC','FP_FP','OBJ_DARK','OBJ_FP','HC_DARK','DARK_HC','HC_HC']

            if 'STAR_DARK' in file:
                hdr['DPRTYPE'] = 'OBJ_DARK'

            if 'STAR_FP' in file:
                hdr['DPRTYPE'] = 'OBJ_FP'


            for DPRTYPE in DPRTYPES:
                if DPRTYPE in file:
                    if DPRTYPE == 'DARK_DARK':
                        hdr['DPRTYPE'] = 'DARK_DARK_TEL'
                    elif DPRTYPE == 'HC_HC':
                        hdr['DPRTYPE'] = 'HCONE_HCONE'
                    elif DPRTYPE == 'FP_HC':
                        hdr['DPRTYPE'] = 'FP_HCONE'
                    elif DPRTYPE == 'HC_FP':
                        hdr['DPRTYPE'] = 'HCONE_FP'
                    elif DPRTYPE == 'DARK_HC':
                        hdr['DPRTYPE'] = 'DARK_HCONE'
                    elif DPRTYPE == 'HC_DARK':
                        hdr['DPRTYPE'] = 'HCONE_DARK'
                    else:
                        hdr['DPRTYPE '] = DPRTYPE


            if 'DPRTYPE' not in hdr:
                print('error, with DPRTYPE for ',file)
                return


            if 'OBJECT' not in hdr:
                hdr['OBJECT'] = 'none'

            if 'RDNOISE' not in hdr:
                hdr['RDNOISE']= 10.0,'rdnoise *not* provided, added by _pp'

            if 'GAIN' not in hdr:
                hdr['GAIN']= 1.000,'gain *not* provided, added by _pp'

            if 'SATURATE' not in hdr:
                hdr['SATURATE']= 60000,'saturate *not* provided, added by _pp'

            if 'PVERSION' not in hdr:
                hdr['PVERSION'] = 'NIRPS_SIMU_PP'

            if 'OBSTYPE' not in hdr:
                if hdr['DPRTYPE'][0:4] == 'FLAT':
                    hdr['OBSTYPE'] = 'FLAT'

                if hdr['DPRTYPE'][0:4] == 'DARK':
                    hdr['OBSTYPE'] = 'DARK'

                if hdr['DPRTYPE'][0:2] == 'FP':
                    hdr['OBSTYPE'] = 'ALIGN'

                if hdr['DPRTYPE'][0:2] == 'HC':
                    hdr['OBSTYPE'] = 'COMPARISON'

                if hdr['DPRTYPE'][0:3] == 'OBJ':
                    hdr['OBSTYPE'] = 'OBJECT'

            if hdr['DPRTYPE'][0:3] == 'OBJ':
                hdr['TRG_TYPE'] = 'TARGET'
            else:
                hdr['TRG_TYPE'] = ''

            necessary_kwrd = ['OBSTYPE','TRG_TYPE','OBJECT','OBJRA','OBJDEC','OBJECT','OBJEQUIN','OBJRAPM','OBJDECPM','AIRMASS','RELHUMID','OBJTEMP','GAIA_ID','OBJPLX','OBSRV','GAIN','RDNOISE','FRMTIME','EXPTIME','PI_NAME','CMPLTEXP','NEXP','MJDATE','MJDEND','SBCREF_P','SBCCAS_P','SBCALI_P','SBCDEN_P','DATE-OBS','UTC-OBS','SATURATE','TEMPERAT','SB_POL_T']

            missing = False
            for key in necessary_kwrd:
                if key not in hdr:
                    print('missing keyword : {0}'.format(key))
                    missing = True

                    if key in ref_hdr:
                        hdr[key] = ref_hdr[key]

            fits.writeto(outname,im,hdr,overwrite = True)

    return []
