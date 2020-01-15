from astropy.io import fits
from scipy import signal
import bottleneck as mp  
import warnings as warnings    
import numpy as np
import time   
from lin_mini import lin_mini

def fit2dpoly(x, y, z):
    # fit a 2nd order polynomial in 2d over x/y/z pixel points
    ones = np.ones_like(x)
    a = np.array([ones, x, y, x**2, y**2, x*y]).T
    b = z.flatten()
    # perform a least squares fit on a and b
    coeff, r, rank, s = np.linalg.lstsq(a, b,rcond=None)
    # return the coefficients
    return coeff


image = fits.getdata('dark_dark_02_001d.fits')
badpix = np.isfinite(image) == False

def clean_hotpix1(image, badpix):
    #
    # Cleans an image by finding pixels that are high-sigma (positive or negative)
    # outliers compared to their immediate neighbours. Bad pixels are
    # interpolated with a 2D surface fit by using valid pixels within the
    # 3x3 pixel box centered on the bad pix.
    #
    # Pixels in big clusters of bad pix (more than 3 bad neighbours)
    # are left as they are.
    #
    image_rms_measurement = np.array(image)
    #
    # First we construct a 'flattened' image
    # We perform a low-pass filter along the x axis
    # filtering the image so that only pixel-to-pixel structures
    # remain. This is use to find big outliers in RMS.
    # First we apply a median filtering, which removes big outliers
    # and then we smooth the image to avoid big regions filled with zeros.
    # Regions filled with zeros in the low-pass image happen when the local
    # median is equal to the pixel value in the input image.
    #
    # We apply a 5-pix median boxcar in X and a 5-pix boxcar smoothing
    # in x. This blurs along the dispersion over a scale of ~7 pixels.

    # perform a [1,5] median filtering by rolling axis of a 2D image 
    # and constructing a 5*N*M cube, then taking a big median along axis=0
    # analoguous to, but faster than :
    #     low_pass = signal.medfilt(image_rms_measurement, [1, 5])

    tmp = []
    for d in range(-2,3):
        tmp.append(np.roll(image,d))
    tmp = np.array(tmp) 

    tmp = mp.nanmedian(tmp,axis = 0)  

    # same trick but for convolution with a [1,5] boxcar
    low_pass = np.zeros_like(tmp)

    for d in range(-2,3):
        low_pass += np.roll(tmp,d)
    low_pass /= 5

    # residual image showing pixel-to-pixel noise
    # the image is now centered on zero, so we can
    # determine the RMS around a given pixel
    image_rms_measurement -= low_pass

    abs_image_rms_measurement = np.abs(image_rms_measurement)
    # same as a [3,3] median filtering with signal.medfilt but faster
    
    tmp = []
    for dx in range(-1,2):
        for dy in range(-1,2):
            tmp.append(np.roll(abs_image_rms_measurement,[dx,dy],
                               axis = [0,1]))
    tmp = np.array(tmp) 
    rms = mp.nanmedian(tmp,axis = 0)          
    
    # the RMS cannot be arbitrarily small, so  we set
    # a lower limit to the local RMS at 0.5x the median
    # rms
    with warnings.catch_warnings(record=True) as _:
        rms[rms < (0.5 * mp.nanmedian(rms))] = 0.5 * mp.nanmedian(rms)
        # determining a proxy of N sigma
        nsig = image_rms_measurement / rms
        bad = np.array((np.abs(nsig) > 10), dtype=bool)
        
        

    # known bad pixels are also considered bad even if they are
    # within the +-N sigma rejection
    badpix = badpix | bad | ~np.isfinite(image)
    
    # we remove bad pixels at the periphery of the image
    badpix[0,:] = False
    badpix[-1,:] = False
    badpix[:,0] = False
    badpix[:,-1] = False
    
    # find the pixel locations where we have bad pixels
    x, y = np.where(badpix)
    
    box3d = np.zeros([len(x),3,3])
    keep3d = np.zeros([len(x),3,3],dtype = bool)
    
    # centering on zero
    yy, xx = np.indices([3, 3]) - 1

    for ix in range(-1,2):
        for iy in range(-1,2):
            box3d[:,ix+1,iy+1] = image[x+ix,y+iy]
            keep3d[:,ix+1,iy+1] = ~badpix[x+ix,y+iy]

    nvalid = np.sum(np.sum(keep3d,axis=1),axis=1)
    # keep only points with >5 valid neighbours
    box3d = box3d[nvalid>5]
    keep3d = keep3d[nvalid>5]
    x = x[nvalid>5]
    y = y[nvalid>5]
    nvalid = nvalid[nvalid>5]

    # copy the original iamge
    image1 = np.array(image)
    # correcting bad pixels with a 2D fit to valid neighbours

    # pre-computing some values that are needed below
    xx2 = xx**2
    yy2 = yy**2
    xy = xx*yy
    ones = np.ones_like(xx)
    
    for i in range(len(x)):
        keep = keep3d[i]
        box = box3d[i]

        if nvalid[i] ==8:
            # we fall in a special case where there is only a central pixel
            # that is bad surrounded by valid pixel. The central value is 
            # straightfward to compute by using the means of 4 immediate
            # neighbours and the 4 corner neighbours.
            
            m1 = np.mean(box[[0,1,1,2],[1,0,2,1]])
            m2 = np.mean(box[[0,0,2,2],[2,0,2,0]])

            image1[x[i], y[i]] = 2*m1-m2
            
        else:
            # fitting a 2D 2nd order polynomial surface. As the xx=0, yy=0
            # corresponds to the bad pixel, then the first coefficient
            # of the fit (its zero point) corresponds to the value that
            # must be given to the pixel
                    
            a = np.array([ones[keep], xx[keep], yy[keep], xx2[keep], yy2[keep], xy[keep]])
            b = box[keep]
            # perform a least squares fit on a and b
            coeff,_ = lin_mini(b,a, no_recon = True)
            
            # this is equivalent to the slower command :
            #coeff = fit2dpoly(xx[keep], yy[keep], box[keep])
            image1[x[i], y[i]] = coeff[0]
 
    # return the cleaned image
    return image1
    

# STAND-ALONE  OLD FUNCTION to compare speed
def clean_hotpix2(image, badpix):
    # Cleans an image by finding pixels that are high-sigma (positive or negative)
    # outliers compared to their immediate neighbours. Bad pixels are
    # interpolated with a 2D surface fit by using valid pixels within the
    # 3x3 pixel box centered on the bad pix.
    #
    # Pixels in big clusters of bad pix (more than 3 bad neighbours)
    # are left as is
    image_rms_measurement = np.array(image)
    # First we construct a 'flattened' image
    # We perform a low-pass filter along the x axis
    # filtering the image so that only pixel-to-pixel structures
    # remain. This is use to find big outliers in RMS.
    # First we apply a median filtering, which removes big outliers
    # and then we smooth the image to avoid big regions filled with zeros.
    # Regions filled with zeros in the low-pass image happen when the local
    # median is equal to the pixel value in the input image.
    #
    # We apply a 5-pix median boxcar in X and a 5-pix boxcar smoothing
    # in x. This blurs along the dispersion over a scale of ~7 pixels.
    box = np.ones([1, 5])
    box /= mp.nansum(box)
    low_pass = signal.medfilt(image_rms_measurement, [1, 5])
    low_pass = signal.convolve2d(low_pass, box, mode='same')



    # residual image showing pixel-to-pixel noise
    # the image is now centered on zero, so we can
    # determine the RMS around a given pixel
    image_rms_measurement -= low_pass
    # smooth the abs(image) with a 3x3 kernel
    rms = signal.medfilt(np.abs(image_rms_measurement), [3, 3])

    #fits.writeto('med2.fits',rms, overwrite = True)


    # the RMS cannot be arbitrarily small, so  we set
    # a lower limit to the local RMS at 0.5x the median
    # rms
    with warnings.catch_warnings(record=True) as _:
        rms[rms < (0.5 * mp.nanmedian(rms))] = 0.5 * mp.nanmedian(rms)
        # determining a proxy of N sigma
        nsig = image_rms_measurement / rms
        bad = np.array((np.abs(nsig) > 10), dtype=bool)
    # known bad pixels are also considered bad even if they are
    # within the +-N sigma rejection
    badpix = badpix | bad | ~np.isfinite(image)
    # find the pixel locations where we have bad pixels
    x, y = np.where(badpix)
    # centering on zero
    yy, xx = np.indices([3, 3]) - 1
    # copy the original iamge
    image1 = np.array(image)
    # correcting bad pixels with a 2D fit to valid neighbours
    for i in range(len(x)):
        keep = ~badpix[x[i] - 1:x[i] + 2, y[i] - 1:y[i] + 2]
        if mp.nansum(keep*1.0) < 6:
            continue
        box = image[x[i] - 1:x[i] + 2, y[i] - 1:y[i] + 2]
        # fitting a 2D 2nd order polynomial surface. As the xx=0, yy=0
        # corresponds to the bad pixel, then the first coefficient
        # of the fit (its zero point) corresponds to the value that
        # must be given to the pixel
        coeff = fit2dpoly(xx[keep], yy[keep], box[keep])
        image1[x[i], y[i]] = coeff[0]

    # return the cleaned image
    return image1


