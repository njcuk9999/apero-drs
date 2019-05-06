import numpy as np
import glob
import pyfits
import matplotlib.pyplot as plt
from scipy.interpolate import InterpolatedUnivariateSpline
import scipy
from gaussfit import *
import warnings
from scipy.stats.stats import pearsonr
# =============================================================================
# Define variables
# =============================================================================
# Name of program
from scipy.interpolate import griddata

from SpirouDRS import *
from SpirouDRS import spirouDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup
from debanananificator import *
from scipy.optimize import curve_fit
from get_offset_sp import *


wave_file = 'MASTER_WAVE.fits'
map_order_file = 'map_orders.fits' 
map_dx_file = '2295305a_dxmap.fits'

hdr_wave = pyfits.getheader(wave_file)
im_wave = pyfits.getdata(wave_file)

map_orders = pyfits.getdata(map_order_file)
map_dx = pyfits.getdata(map_dx_file)

for iord in range(49):
	w = np.nansum( map_orders == iord ,axis=0)
	dx = np.nansum( (map_orders == iord)*map_dx ,axis=0)/w

	xpix = np.arange(4088)
	gg=np.isfinite(dx)  & (dx !=0)

	fit = np.polyfit(xpix[gg],dx[gg],5)

	new_fit_wave = np.polyfit(xpix+np.polyval(fit,xpix),im_wave[iord,:],4)
	

	for npoly in range(5):
		print()
		print('IORD = ',iord+1)
		print('Keyword : ','TH_LC'+str(iord*5+npoly))
		print('Previous value : ',hdr_wave['TH_LC'+str(iord*5+npoly)])
		print('Corrected value : ',new_fit_wave[::-1][npoly])
		hdr_wave['TH_LC'+str(iord*5+npoly)] = new_fit_wave[::-1][npoly]

	im_wave[iord,:] = np.polyval(new_fit_wave,xpix)

	plt.plot(xpix[gg],dx[gg],'g.',label='per-pixel dx corr')
	plt.plot(xpix,np.polyval(fit,xpix),'k',label='fit to dx')

	plt.xlabel('x pixel')
	plt.ylabel('input correction (pixel)')
	plt.legend()
	plt.show()

pyfits.writeto('MASTER_WAVE.fits',im_wave,hdr_wave,clobber=True)

