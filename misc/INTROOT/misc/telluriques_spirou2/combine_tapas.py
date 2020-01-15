import numpy as np
from astropy.table import Table
import matplotlib.pyplot as plt
from astropy.io import fits as pyfits
from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.ndimage.filters import median_filter
from scipy.optimize import curve_fit
import sys
import numpy as np
from matplotlib import pyplot as plt
import os

# sp_tapas2 = np.load('/spirou/cfht_nights/cfht/telluDB_EA/MASTER_WAVE_tapas_convolved.npy')
sp_tapas2 = np.load('MASTER_WAVE_tapas_convolved.npy')

sp_h2o = sp_tapas2[1, :]
sp_others = np.prod(sp_tapas2[2:, :], axis=0)


def tellu(keep,tau_h2o,tau_others):
	#
	# generates a Tapas spectrum from the saved temporary .npy 
	# structure and scales with the given optical depth for 
	# water and all other absorbers
	#
	# as an input, we give a "keep" vector, values set to keep=0
	# will be set to zero and not taken into account in the fitting
	# algorithm
	#
	# line-of-sight optical depth for water cannot be negative
	#
	if tau_h2o<0:
		tau_h2o=0

	if tau_h2o>99:
		tau_h2o=99

	# line-of-sight optical depth for other absorbers cannot be less than one (that's zenith)
	# keep the limit at 0.2 just so that the value gets propagated to header and leaves
	# open the possibility that during the convergence of the algorithm, values 
	# go slightly below 1.0
	if tau_others<0.2:
		tau_others=0.2

	# line-of-sight optical depth for other absorbers cannot be greater than 5
	# ... that would be an airmass of 5 and SPIRou cannot observe there
	if tau_others>5:
		tau_others=5

	# we will set to a fractional exponent, we cannot have values below zero
	sp_h2o[sp_h2o<0]=0
	sp_others[sp_others<0]=0

	sp=(sp_h2o**tau_h2o)*(sp_others**tau_others)

	# values not to be kept are set to a very low value
	sp[~np.ravel(keep)]=1e-9

	# to avoid divisons by 0, we set values that are very low to 1e-9
	sp[sp<1e-9]=1e-9


	return sp




##### inputs #####

file = '2305648o_pp_e2dsff_AB.fits'
outname = (file.split('.fits'))[0]+'_trans.fits'

wave = pyfits.getdata('MASTER_WAVE.fits')
bla = pyfits.getdata('18AQ18-Jul28_2294614f_pp_blaze_AB.fits')

# reading science file
sp = pyfits.getdata(file)
hdr = pyfits.getheader(file)

# value below which the blaze in considered too low to be useful
# for all blaze profiles, we normalize to the 95th percentile. That's pretty
# much the peak value, but it is resistent to eventual outliers
blaze_threshold =.1 
blaze_norm_percentile = 95

# number of orders
norders = 49

# max number of iterations, normally converges in about 12 iterations
nite_max=50


# per-order kernel convolution witdth 
# if we use a template, then all orders can use a very large kernel size
# this avoids introducing big RV features
wconv = np.zeros(norders)+900

# If we do NOT have a template, then some orders will use a finer kernel
# this fits stellar lines, but when using a template, it may
# induce spurious featues

wconv_no_template = np.array(wconv)
wconv_no_template[[2,3,5,6,7,8,9,15,19,20,29,30,31,32,33,34,35,43,44]]=50


# threshold in absorbance where we will stop iterating the absorption
# model fit
dparam_threshold = 0.001

# minimum transmission required for use of a given pixel in the TAPAS and SED
# fitting
threshold_transmission_fit = 0.3

# sigma-clipping of the residuals of the difference between the
# spectrum divided by the fitted TAPAS absorption and the 
# best guess of the SED
nsigclip = 8.0

# speed of light in km/s
c = 2.99792458e5

airmass = hdr['airmass']

# loop through blaze orders, normalize blaze by its peak amplitude 
for iord in range(norders):
	sp[iord,:]/=np.nanpercentile(sp[iord,:],blaze_norm_percentile)
	bla[iord,:]/=np.nanpercentile(bla[iord,:],blaze_norm_percentile)
bla[bla<blaze_threshold]=np.nan

# set to nan values where spectrum is zero
sp[sp==0]=np.nan
sp/=bla

# check if template exists
obj=hdr["OBJECT"]
template_file = "Template_"+obj+".fits"
print('Template : ',template_file)

# if the template exists, then read it an shift it to the correct BERV
if os.path.isfile(template_file):
	template=pyfits.getdata(template_file)
	berv = hdr["BERV"]

	# wavelength offset from BERV
	relativistic_doppler = np.sqrt((1-berv/c)/(1+berv/c))

	for iord in range(49):
		# median-filter the template. we know that stellar features
		# are very broad. this avoids having spurious noise in
		# our templates
		g=np.isfinite(template[iord,:])
		template[iord,g] = median_filter(template[iord,g],15)

	for iord in range(49):
		g=np.isfinite(template[iord,:])

		if np.nansum(g)>2044:
			# spline the template to the correct velocity
			spline=InterpolatedUnivariateSpline(wave[iord,g]*relativistic_doppler,template[iord,g],k=1,ext=3)
			template[iord,:]=spline(wave[iord,:])
		else:
			# if less than 50% of the order is considered valid, then set template value to 1
			# this only apply to the really contaminated orders
			template[iord,:]=1

	# divide observed spectrum by template. This gets us close to the
	# actual sky transmission. We will iterate on the exact shape of the SED
	# by finding offsets of sp relative to 1 (after correcting form the TAPAS).
	sp/=template
else:
	# if we don't have a template, we assume that its 1 all over
	template = np.ones_like(sp)

	# if we don't have a template, then we use a small kernel on 
	# relatively "clean" orders
	wconv = np.array(wconv_no_template)

# starting point for the optical depth of water and other gasses
guess=[airmass,airmass]

# first estimate of the absorption spectrum
tau1 = tellu(np.isfinite(wave),guess[0],guess[1])

# Spectral energy distribution estimate for the hot star
# we start with a spectrum full of 1
sed = np.ones_like(wave)

# flag to see if we converged
# this is the quadratic sum of the change in airmass and water column
# when the change in the sum of these two values is very small between
# two steps, we assume that the code has converges
dparam = 99

# counting the number of iterations
ite=0

# plot some quality checks
doplot=True

# if the code goes out-of-bound, then we'll get out of the loop
# with this keyword
fail=False

while (dparam>dparam_threshold) & (ite < nite_max) & (fail==False):
	# previous guess
	prev_guess = guess

	# we have an estimate of the absorption spectrum
	fit_sp=(sp/sed)

	# some masking of NaN regions
	fit_sp[~np.isfinite(fit_sp)]=0

	# vector used to mask invalid regions
	keep = (fit_sp !=0)
	keep &= (np.isfinite(fit_sp))
	# only fitted where the transmission is greated than a certain value
	keep &= (np.reshape(tau1,[49,4088])>threshold_transmission_fit)
	# considered bad if the spectrum is larger than 1.1. This is 
	# likely an OH line or a cosmic ray
	keep &= (fit_sp < 1.1)

	# fit telluric absorption of the spectrum corrected for the SED
	popt,pcov = curve_fit(tellu,keep,np.ravel(fit_sp),guess)

	guess=popt

	if (guess[0]<0.2) or (guess[0]>99):
		print('recovered water vapor optical depth not between 0.3 and 99 : ',guess[0])
		fail=True

	# we will use a stricter condition later, but for all steps
	# we expect an agreement within an airmass difference of 1
	if np.abs(guess[1]-airmass) > 1:
		print('airmass : ',airmass)
		print('recovered airmass : ',guess[1])
		fail=True

	# how much did the optical depth params changed
	dparam=np.sqrt(np.nansum((guess-prev_guess)**2))

	print('ite = ',ite,'/',nite_max,', H2O depth : ',guess[0],', ','other gases depth : ',guess[1],', airmass',airmass)
	print('Convergence parameter : ',dparam)

	# current best-fit spectrum
	tau1 = tellu(np.isfinite(wave),guess[0],guess[1])

	# for each order, we fit the SED after correcting for absorption
	for iord in range(norders):

		# sp2 is the per-order spectrum divided by the best guess for absorption
		sp2=sp[iord,:]/tau1[iord*4088:iord*4088+4088]

		# we assume that points are valid if they are close or above the
		# median local transmission.

		g=keep[iord,:]

		if np.nansum(g)>100:
			# if we have enough valid points, we normalized the domain by its median
			best_trans = (tau1[iord*4088:iord*4088+4088]>np.nanpercentile((tau1[iord*4088:iord*4088+4088])[g],95))
			norm = np.nanmedian(sp2[best_trans])
		else:
			norm=1.0
		sp[iord,:]/=norm
		sp2/=norm
		sed[iord,:]/=norm		

		# find far outliers to SED for sigma-clipping
		res=sp2-sed[iord,:]
		res-=np.nanmedian(res)
		res/=np.nanmedian(np.abs(res))

		# sigma clipping of residuals
		res[np.isfinite(res) == False]=99
		g &= (np.abs(res)<nsigclip)
		g &= (sed[iord,:]>0.5*np.nanmedian(sed[iord,:]))
		g &= (tau1[iord*4088:iord*4088+4088]>0.3)
		sp2[~g]=np.nan
		
		# sp3 is a median-filtered version of sp2 where pixels that have a transmission
		# that is too low are clipped.
		sp3=median_filter(sp2-sed[iord,:],31)+sed[iord,:]
		sp3[~np.isfinite(sp3)]=0
		g[sp3==0]=0

		# we smooth sp3 with a kernel. This kernel has to be small enough to 
		# preserve stellar features and large enough to subtract noise
		# this is why we have an order-dependent width.
		# the stellar lines are expected to be larger than 200km/s, so a kernel
		# much smaller than this value does not make sense

		ew=wconv[iord]/2.2/2.35
		xx=np.arange(-np.int(wconv[iord]*2),np.int(wconv[iord]*2))
		#ker=1/(1+(xx/(wconv[iord]/16))**2)
		ker=np.exp(-0.5*(xx/ew)**2)
		ker/=np.nansum(ker)

		# update of the SED
		ww1=np.convolve(g,ker,mode='same')

		spconv = np.convolve(sp3*g,ker,mode='same')
		sed_update=spconv/ww1

		sed_update[ww1<0.01]=np.nan

		# if np.max(ww1)>0.01:
		# 	g=(np.where(np.isfinite(sed_update_1)))[0]
		# 	spline=InterpolatedUnivariateSpline(g,sed_update_1[g],ext=3)
		# 	sed_update=spline(np.arange(4088))
		# else:
		# 	sed_update=sed_update_1

		# if we have lots of very strong absorption, we subtract the median value
		# of pixels where the transmission is expected to be smaller than 1%. This 
		# improves things in the stronger absorptions
		pedestal=tau1[iord*4088:iord*4088+4088]<0.01
		nlow=np.nansum(pedestal)
		if nlow >100:
			zp=np.nanmedian(sp[iord,pedestal])
			if np.isfinite(zp):
				sp[iord,:]-=zp


		sed[iord,:] = sed_update

		if (ite==10) & doplot:
			print('iord = ',iord)
			g=keep[iord,:]
			if np.nansum(g)>100:
				plt.title('Order : '+str(iord))
				plt.plot(wave[iord,:],tau1[iord*4088:iord*4088+4088],'c-',label = 'tapas fit')
				plt.plot(wave[iord,:],sp[iord,:],'k-',label='input SP')
				plt.plot(wave[iord,:],sp[iord,:]/sed[iord,:],'b-',label='measured transmission')
				plt.plot(wave[iord,g],sp3[g],'r.',label='tentative SED')
				plt.plot(wave[iord,:],sed_update,'g--',label='SED best guess')
				plt.legend()
				plt.xlim([np.min(wave[iord,g]),np.max(wave[iord,g])])
				plt.show()
	ite+=1



# some quality checks
if np.abs(guess[1]-airmass) > 0.1:
	print('airmass : ',airmass)
	print('recovered airmass : ',guess[1])
	fail=True

if (guess[0]<0.2) or (guess[0]>99):
	print('recovered water vapor optical depth not between 0.3 and 99 : ',guess[0])
	fail=True

if not fail:
	# adding some goodies to the header
	hdr['TAU_H2O'] = guess[0],'TAPAS tau H2O'
	hdr['TAU_OTHE'] = guess[1],'TAPAS tau for O2,O3, CH4, N2O, CO2'
	pyfits.writeto(outname,sp/sed,hdr,clobber='True')

