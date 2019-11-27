from scipy import ndimage
from scipy.signal import convolve2d
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
    
wx_ker = 1
wy_ker = 9
sig_ker = 3




def scattered1(image1, wx_ker, wy_ker, sig_ker):
    print('method # 1')
    sz = image1.shape
    
    sz_small = [sz[1]//largest_divisor_below(sz[1],wy_ker),sz[0]//largest_divisor_below(sz[0],wx_ker) ]
    
    shape = (sz_small[0], image1.shape[0] // sz_small[0],
             sz_small[1], image1.shape[1] // sz_small[1])
    image2 = np.array(image1).reshape(shape).mean(-1).mean(1)
    
    downsize_ratio = np.array(sz)/np.array(sz_small)

    ker_sigx = int((wx_ker * sig_ker * 2) / downsize_ratio[1] + 1)
    ker_sigy = int((wy_ker * sig_ker * 2) / downsize_ratio[0] + 1)
    kery, kerx = np.indices([ker_sigy, ker_sigx], dtype=float)
    # this normalises kernal x and y between +1 and -1
    kery = kery - np.mean(kery)
    kerx = kerx - np.mean(kerx)
    # calculate 2D gaussian kernel
    ker = np.exp(-0.5 * ((kerx / wx_ker *  downsize_ratio[1])**2 + (kery / wy_ker *  downsize_ratio[0])**2))
    # we normalize the integral of the kernel to 1 so that the AMP factor
    #    corresponds to the fraction of scattered light and therefore has a
    #    physical meaning.
    ker = ker / np.sum(ker)
    # we need to remove NaNs from image

    scattered_light = convolve2d(image2, ker, mode='same')
    output = ndimage.zoom(scattered_light, np.array(image1.shape)/np.array(image2.shape), output=None, order=1, mode='constant', cval=0.0)
    
    return output


def scattered2(image1, wx_ker, wy_ker, sig_ker):
    print('method # 2')
    ker_sigx = int((wx_ker * sig_ker * 2) + 1)
    ker_sigy = int((wy_ker * sig_ker * 2) + 1)
    kery, kerx = np.indices([ker_sigy, ker_sigx], dtype=float)
    # this normalises kernal x and y between +1 and -1
    kery = kery - np.mean(kery)
    kerx = kerx - np.mean(kerx)
    # calculate 2D gaussian kernel
    ker = np.exp(-0.5 * ((kerx / wx_ker)**2 + (kery / wy_ker)**2))
    # we normalize the integral of the kernel to 1 so that the AMP factor
    #    corresponds to the fraction of scattered light and therefore has a
    #    physical meaning.
    ker = ker / np.sum(ker)
    # we need to remove NaNs from image
    # we determine the scattered light image by convolving our image by
    #    the kernel
    scattered_light = convolve2d(image1, ker, mode='same')

    return scattered_light


image1 = fits.getdata('dark_dark_02_001d.fits')
image1[np.isfinite(image1) != True] = 0
sz = image1.shape


scat1 = scattered1(image1, wx_ker, wy_ker, sig_ker)
scat2 = scattered2(image1, wx_ker, wy_ker, sig_ker)








def largest_divisor_below(n1,n2):
    # finds the largets divisor of a large number below a certain limit
    # for 4088 and 9, we would get 8 (511*8 = 4088)
    # Useful to downsize images.
    for i in range(n2,0,-1):
        if n1 % i == 0:
            return i

def correct_local_background(params, image, **kwargs):
    func_name = __NAME__ + '.correct_local_background()'
    # get constants from parameter dictionary
    wx_ker = pcheck(params, 'BKGR_KER_WX', 'wx_ker', kwargs, func_name)
    wy_ker = pcheck(params, 'BKGR_KER_WY', 'wy_ker', kwargs, func_name)
    sig_ker = pcheck(params, 'BKGR_KER_SIG', 'sig_ker', kwargs, func_name)
    # log process
    WLOG(params, '', TextEntry('40-012-00010'))
    
    # determine the scattering from an imput image. To speed up the code,
    # do the following steps rather than a simple convolution with the 
    # scattering kernel.
    #
    # Logical (slow) steps -->
    #
    # -- create a kernel of a 2D gaussian with a width in X and Y defined
    # from the BKGR_KER_WX and BKGR_KER_WY keywords
    # this kernel is typically much larger on one axis than on the other
    # (typically 1 vs 9 pixels 1/e width)
    # -- convolve the image by the kernel
    #
    # Faster (but less intuitive) steps that we do -->
    #
    # - Downsize (simple binning) the image to dimensions for which the
    # convolution kernel is (barely) Nyquist. These dimensions are selected
    # to be the smallest integer dimensions where there are integer pixel 
    # bins while remaining above Nyquist. If we have a 9 pixel 1/e width,
    # then we bin by a factor of 8 an 4088 image to a 511 pixel size, and
    # the 1/e width in that new reference frame becomes 9/8 ~ 1.1
    # - Convolve the binned-down image with the kernel in the down-sized
    # reference frame. Here, a 1x9 1/e 2-D gaussian becomes a 1x1.1 1/e
    # gaussian. The kernel is smaller and the input image is also similarly
    # smaller, so there is a N^2 gain.
    # - Upscale the convolved image to the input dimensions
    #
    
    # Remove NaNs from image
    image1 = mp.nanpad(image)

    # size if input image
    sz = image1.shape
    # size of the smaller image. It is an integer divider of the input image
    # 4088 on an axis and wN_ker = 9 would lead to an 8x scale-down (8*511)
    sz_small = [sz[1]//largest_divisor_below(sz[1],wy_ker),
                sz[0]//largest_divisor_below(sz[0],wx_ker) ]
    

    # downsizing image prior to convolution
    # bins an image from its shape down to a smaller shape, say 4096x4096 to 
    # 512x512. Before/after axis ratio must be integers in all dims.
    #
    shape = (sz_small[0], image1.shape[0] // sz_small[0],
             sz_small[1], image1.shape[1] // sz_small[1])
    image2 = np.array(image1).reshape(shape).mean(-1).mean(1)

        
    # downsizing ratio to properly scale convolution kernel
    downsize_ratio = np.array(sz)/np.array(sz_small)

    # convolution kernel in the downsized domain
    ker_sigx = int((wx_ker * sig_ker * 2) / downsize_ratio[1] + 1)
    ker_sigy = int((wy_ker * sig_ker * 2) / downsize_ratio[0] + 1)
    kery, kerx = np.indices([ker_sigy, ker_sigx], dtype=float)
    # this normalises kernal x and y between +1 and -1
    kery = kery - np.mean(kery)
    kerx = kerx - np.mean(kerx)
    # calculate 2D gaussian kernel
    ker = np.exp(-0.5 * ((kerx / wx_ker *  downsize_ratio[1])**2 
                         + (kery / wy_ker *  downsize_ratio[0])**2))
    
    # we normalize the integral of the kernel to 1 so that the AMP factor
    #    corresponds to the fraction of scattered light and therefore has a
    #    physical meaning.
    ker = ker / np.sum(ker)

    # upscale image back to original dimensions
    image3 = convolve2d(image2, ker, mode='same')
    scattered_light = ndimage.zoom(image3, 
                          np.array(image1.shape)/np.array(image2.shape), 
                          output=None, order=1, mode='constant', cval=0.0)

    # returned the scattered light
    return scattered_light

