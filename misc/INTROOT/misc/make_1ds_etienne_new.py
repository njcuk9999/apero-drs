from astropy.io import fits 
import numpy as np
#from scipy import optimize
#from numpy import *
#from math import *
#from lmfit import Parameters,minimize,report_fit
from tqdm import tqdm
import matplotlib.pyplot as plt
from scipy.interpolate import InterpolatedUnivariateSpline as IUS

bl = fits.getdata('20180526_2279321f_pp_blaze_AB.fits')
#sp = fits.getdata('2279682o_pp_e2dsff_AB.fits')
sp = fits.getdata('2279682o_pp_e2dsff_AB_tellu_corrected.fits')
wa = fits.getdata('20180526_2279327a_pp_2279330c_pp_wave_ea_AB.fits')
nord = 49 # number of orders


# set to NaN pixels that should be NaNs
bl[bl == 1] = np.nan

# smart/simple wavelength vector
simple = False

if simple:
    # uniform wavelength vector
    l1 = 950 # min wavelength
    l2 = 2500 # max wavelength
    # in equal walength bins
    step = 0.01 # step size of the wavelength grid in nm
    wn = np.arange(l1,l2+step/2.0,step)
else:
    # uniform wavelength vector in velocity space
    step = 1.0 # step in km/s
    l1 = 950.0 # min wavelength
    l2 = 2500.0 # max wavelength
    c =  299792.4580 # speed of light
    
    nlambda = np.round(c/step*np.log(l2/l1))
    
    # updating slightly the wavelength to have exactly 'step' km/s
    l2 = np.exp(nlambda*step/c)*l1 

    index=np.arange(nlambda)/nlambda
    wn=l1*np.exp(index*np.log(l2/l1))


# define a smooth transition mask at the edges of the image
# this ensures that the s1d has no discontinuity when going from one order
# to the next. We define a scale for this mask
# smoothing scale
eW_mask = 40
ww = np.zeros_like(bl)
# define a convonlution kernel that goes from -3 to +3 e width of the mask
ker = np.exp( -(np.arange(-int(eW_mask*3),int(eW_mask*3),1)/eW_mask)**2)

edges = np.ones(4088,dtype=bool)
# set edges of the image to 0 so that  we get a sloping weight
edges[0:int(eW_mask*3)] = False
edges[-int(eW_mask*3):] = False

    



for iord in tqdm(range(nord)):
    # find the sloping weight vector for all orders
    valid = np.isfinite(bl[iord,:]) & (bl[iord,:] > np.nanmax(bl[iord,:])*.05) & edges
    
    if np.max(valid) == True:
        w2 = np.convolve(valid,ker,mode='same')
        w2/=np.nanmax(w2)
        ww[iord,:] = w2
    
# multiply both the spectrum and the blaze by the sloping vector
bl*=ww
sp*=ww




weight = np.zeros_like(wn)
out_sp = np.zeros_like(wn)
nanmask1 = np.zeros_like(wn)
nanmask2 = np.zeros_like(wn)
# Perform a weighted mean of overlapping orders
# by performing a spline of both the blaze and the spectrum
for iord in tqdm(range(nord)):
    valid = np.isfinite(sp[iord,:]) & np.isfinite(bl[iord,:]) 
    
    if np.max(valid) == True:
        spline_sp = IUS(wa[iord,valid],sp[iord,valid],k=5,ext=1)
        spline_bl = IUS(wa[iord,valid],bl[iord,valid],k=5,ext=1)
        
        spline_nan = IUS(wa[iord,:],np.isfinite(sp[iord,:]),k=1,ext=1)

        useful_range = (wn>np.nanmin(wa[iord,valid])) & (wn<np.nanmax(wa[iord,valid]))
        
        nanmask1[useful_range] += spline_nan(wn[useful_range])
        nanmask2[useful_range] +=1
        weight[useful_range] += spline_bl(wn[useful_range])
        out_sp[useful_range] += spline_sp(wn[useful_range])
    
nanmask = nanmask1/nanmask2

bad = nanmask<0.99
out_sp[bad] = np.nan

plt.ylim([-.2,4.0])
plt.plot(wn,nanmask,'m-',label='nan mask')
plt.plot(wn,out_sp/np.nanmedian(out_sp),'r-',label = 'prior to division')
plt.plot(wn,weight/np.nanmedian(weight),'c-',label = 'weight vector')

# normalize the spectrum by the weight vector so that a constant
# spectrum ends up being flat

out_sp/=weight
plt.plot(wn,out_sp/np.nanmedian(out_sp),'k-',label = 'after to division')
plt.legend(loc=0)
plt.show()