#from lin_mini import *
#import os
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
from scipy.optimize import curve_fit
from astropy.io import ascii
from scipy import *
from scipy.signal import *


def gauss(x, amp, x0, w, zp, slope):
        return amp*np.exp(-0.5*(x-x0)**2/w**2) + zp + slope*(x-x0)


def get_offset_sp(sp_fp,sp_hc,iord,doplot=False):

	bottom = np.zeros_like(sp_fp)
	top = np.zeros_like(sp_fp)
	for i in range(4088):
		start = i-30
		end = i+30
		if start<0:
			start=0
		if end>4087:
			end=4087

		segment=sp_fp[start:end]
		bottom[i] = np.nanpercentile(segment,10)
		top[i] = np.nanpercentile(segment,95)

	top[top<=(0.1*np.max(top))]=(0.1*np.max(top))

	sp_fp-=bottom
	sp_fp/=(top-bottom)
	sp_fp[~np.isfinite(sp_fp)]=0

	#plt.plot(sp_fp)
	#plt.plot(bottom)
	#plt.plot(top)
	#plt.show()

	# The HC spectrum is high-passed. We are just interested to know if
	# a given expected line from the catalog falls at the position of a 
	# >3-sigma peak relative to the continuum
	sp_hc -= medfilt(sp_hc,15)
	# we normalized the HC to its absolute deviation 
	sp_hc/=np.nanmedian(np.abs(sp_hc[sp_hc!=0]))

	# The reference solution. All FP peaks will be anchored to this
	# wavelength solution
	hdr_wave = pyfits.getheader("MASTER_WAVE.fits")

	# getting the polynomials for the wavelength solution
	# in the end, we'll only keep the ones corresponding to the iord (corrent order)
	poly_wave_hdr = hdr_wave["TH_LC*"]
	poly_wave_ref = np.zeros([len(poly_wave_hdr)//5,5])
	for i in range(len(poly_wave_hdr)):
		poly_wave_ref[i//5,i % 5] = poly_wave_hdr[i]

	# Reading the UNe line list
	UNe_lines = ((ascii.read('catalogue_UNe.dat',format='basic')))[0][:]

	# Reading the polynomial terms for the cavity length
	output_cavity = (ascii.read('cavity_length.dat',format='basic'))
	# some re-formatting into a well-behaved array
	ncoeff = len(output_cavity)
	poly_cavity = np.zeros(ncoeff)
	for i in range(ncoeff):
		poly_cavity[i]= output_cavity[:][i][1]
	poly_cavity = poly_cavity[::-1]

	# fpindex is a variable that contains the index of the FP peak interference
	# this is expected to range from ~10000 to ~25000
	fpindex=np.arange(30000)+1

	# We find the exact wavelength of each FP peak in fpindex
	# considering the cavity length

	# The cavity length is very slightly wavelength dependent (hence the
	# polynomial read earlier). First we find the length in the middle of the 
	# expected wavelength domain from the reference file

	# just to cut the number of peaks so that they are 
	# all contained within the relevant domain
	wave_start_med_end = np.polyval(poly_wave_ref[iord][::-1],[0,2044,4088])

	wave_fp = np.polyval(poly_cavity,wave_start_med_end[1])*2/fpindex
	g = wave_fp>(wave_start_med_end[0]-20) # we give a 20 nm marging on either side... who knows, maybe SPIRou has drifted
	g &= wave_fp<(wave_start_med_end[2]+20)

	# keeping only the relevant FPs
	fpindex = fpindex[g]
	wave_fp = wave_fp[g]

	# a numerical trick so that we don't have to invert the poly_cavity polynomial
	# wave_fp depends on the cavity length, which in turns depends (very slightly) on
	# wave_fp again. This iteration fixes the problem
	for ite in range(5):
		wave_fp = np.polyval(poly_cavity,wave_fp)*2/fpindex

	# pixel position along the spectrum
	xpix=np.arange(len(sp_fp))

	# vectors to be appended
	xpeak = [] # x position of the FP peak
	peakval = [] # peak value. Could be used for quality check
	ewval = [] # e-width of the line. Could be used for quality check

	maxmax = np.max(sp_fp) # peak value of the FP spectrum
	maxi=maxmax # current maximum value after masking
	mask=np.ones_like(sp_fp) # 
	mask[0:30]=0
	mask[len(sp_fp)-30:]=0

	# looping while FP peaks are at least 20% of the max peak value
	while maxi > (maxmax*.4):
		pos=np.argmax(sp_fp*mask)
		maxi=sp_fp[pos]
		mask[pos-3:pos+4]=0
		ww=5
		# extracting a +-5 pixel window in the spectrum
		yy=sp_fp[pos-ww:pos+ww+1]
		xx=xpix[pos-ww:pos+ww+1]
		# finding the domain between the minima before and the minima after the peak value
		mask1=np.ones_like(yy)
		mask1[0:ww]=0
		mask2=np.ones_like(yy)
		mask2[ww:]=0
		y0=np.argmin(yy/np.max(yy)+mask1)
		y1=np.argmin(yy/np.max(yy)+mask2)

		xx=xx[y0:y1+1]+0.0
		yy=yy[y0:y1+1]

		# the FP must be at least 5 pixels long to be valid
		if len(xx)>5:
			# amp, x0, w, zp
			p0=[np.max(yy)-np.min(yy),xx[np.argmax(yy)],1,np.min(yy),0]
			goodfit = False

			try:
				# we try fitting a Gaussian
				a0, pcov = curve_fit(gauss, xx, yy,p0=p0)
				goodfit = True
			except: 
				print("One FP peak was bad... don't worry and keep reducing data!")

			if goodfit==True:
				xpeakpos=a0[1]				
				xpeak=np.append(xpeak,xpeakpos)
				peakval = np.append(peakval,a0[0])
				ewval = np.append(ewval,a0[2])

	# TODO: =======================================================
	# TODO: GOT TO HERE
	# TODO: =======================================================

	# we sort the FP peaks by their x pixel position
	index = np.argsort(xpeak)

	# we have new vectors that will contain the sorted peaks
	xpeak2 = np.zeros_like(xpeak)
	peakval2 = np.zeros_like(peakval)
	ewval2 = np.zeros_like(ewval)

	# we sort
	for i in range(len(index)):
		xpeak2[i]=xpeak[index[i]]
		peakval2[i]=peakval[index[i]]
		ewval2[i]=ewval[index[i]]

	# we  "count" the FP peaks and determine their number in the 
	# FP interference

	# we determine the distance between consecutive peaks

	xpeak2b=(xpeak2[1:]+xpeak2[:-1])/2
	dxpeak = xpeak2[1:]-xpeak2[:-1]

	# we clip the most deviant peaks
	g=(dxpeak>np.nanpercentile(dxpeak,5)) & (dxpeak<np.nanpercentile(dxpeak,95))
	fit_peak_separation = np.polyfit(xpeak2b[g],dxpeak[g],2)


	# Looping through peaks and counting the number of meddx between peaks
	# we know that peaks will be at integer multiple or medds (in the overwhelming
	# majority, they will be at 1 x meddx)
	ipeak = np.zeros(len(xpeak2),dtype=int)
	for i in range(1,len(xpeak2)):	
		dx=xpeak2[i]-xpeak2[i-1]
		dx_estimate = np.polyval(fit_peak_separation,xpeak2[i])
		ipeak[i]=ipeak[i-1]+np.round(dx/dx_estimate)
		if np.round(dx/dx_estimate) !=1:
			print('dx= ',dx,', dx/estimate = ',dx/dx_estimate,', estimate =',dx_estimate)

	# Trusting the wavelength solution, this is the wavelength of FP peaks
	wave_from_hdr = np.polyval(poly_wave_ref[iord][::-1],xpeak2)

	# We estimate the FP order of the first FP peak. This integer value
	# should be good to within a few units
	print('->',poly_cavity)
	print('---->',wave_from_hdr[0])
	fp_peak0_estimate = int( (np.polyval(poly_cavity,wave_from_hdr[0])*2)/wave_from_hdr[0])

	# we scan "zp", which is the FP order of the first FP peak that we've found
	# we assume that the error in FP order assignment could range form -50 to +50
	# in practice, it is -1, 0 or +1 for the cases we've tested to date
	bestzp = fp_peak0_estimate

	maxgood=0
	for zp in range(fp_peak0_estimate-fpindex[0]-50,fp_peak0_estimate-fpindex[0]+50):
		# we take a trial solution between wave (from the theoretical FP solution) and the
		# x position of measured peaks
		fit = np.polyfit(wave_fp[zp-ipeak],xpeak2,3)

		# we predict an X position for the known U Ne lines
		xpos_predic = np.polyval(fit,UNe_lines)

		g=xpos_predic>0
		g &= xpos_predic<4087
		xpos_predic = xpos_predic[g]

		# we check how many of these lines indeed fall on a >3sigma 
		# excursion of the HC spectrum

		xpos_predic_int = np.zeros(len(xpos_predic),dtype=int)
		for i in range(len(xpos_predic_int)):
			xpos_predic_int[i]= xpos_predic[i]

		# the FP order number that produces the most HC matches
		# is taken to be the right wavelength solution
		frac_good = np.mean(sp_hc[xpos_predic_int] >3)

		if frac_good > maxgood:
			maxgood = frac_good
			bestzp = zp


	print("Predicted FP peak # : ",fp_peak0_estimate)
	print("Measured FP peak # : ",fpindex[bestzp])

	# we find the actual wavelength of our IDed peaks
	wave_xpeak2 = wave_fp[bestzp-ipeak]

	# we find the corresponding offset
	poly = poly_wave_ref[iord]#[::-1]
	deriv_poly = [poly[i] * i for i in range(1, len(poly))]


	err_wave = wave_xpeak2-np.polyval( poly_wave_ref[iord][::-1],xpeak2)
	err_pix = err_wave/np.polyval(deriv_poly[::-1],xpeak2)

	maxabsdev = 999

	g=np.isfinite(err_pix)

	#first we perform a thresholding with a 1st order polynomial
	while maxabsdev>5:
		fit_err_xpix = np.polyfit(xpeak2[g],err_pix[g],1)
		dev = err_pix - np.polyval(fit_err_xpix,xpeak2)
		absdev = np.nanmedian(np.abs( dev ))
		maxabsdev = np.nanmax(np.abs(dev[g]/absdev))
		g &= np.abs(dev/absdev) < 5

	maxabsdev = 999
	#then we perform a thresholding with a 5th order polynomial
	while maxabsdev>5:
		fit_err_xpix = np.polyfit(xpeak2[g],err_pix[g],5)
		dev = err_pix - np.polyval(fit_err_xpix,xpeak2)
		absdev = np.nanmedian(np.abs( dev ))
		maxabsdev = np.nanmax(np.abs(dev[g]/absdev))
		g &= np.abs(dev/absdev) < 5

	# this relation is the (sigma-clipped) fit between the xpix error
	# and xpix along the order. The corresponding correction vector will
	# be sent back to the dx grid
	corr_err_xpix = np.polyval(fit_err_xpix,np.arange(4088))


	# all sorts of stats
	print('stddev pixel error relative to fit : ',np.std(dev),' pix')
	print('absdev pixel error relative to fit : ',absdev,' pix')
	print('median pixel error relative to zero : ',np.nanmedian(err_pix),' pix')

	print('stddev applied correction : ',np.std(corr_err_xpix[xpos_predic_int]),' pix')
	print('med applied correction : ',np.nanmedian(corr_err_xpix[xpos_predic_int]),' pix')

	print('Nth FP peak at center of order',np.polyval(np.polyfit(xpeak2[g],fpindex[zp-ipeak[g]],5),2044))

	# a plot just to see that the code behaved
	if doplot ==True:
		plt.clf()
		plt.plot(xpeak2,err_pix,'r.',label='err pixel')
		plt.plot(xpeak2[g],err_pix[g],'g.',label='err pixel (for fit)')
		plt.plot(np.arange(4088),corr_err_xpix,'k',label='fit to err pix')
		plt.xlabel('Pixel')
		plt.ylabel('Err Pixel')
		sig = np.nanmedian(np.abs(err_pix-np.nanmedian(err_pix)))
		zp = np.nanmedian(err_pix)
		#plt.ylim([-40*sig+zp,40*sig+zp])
		plt.legend()
		plt.show()

	return corr_err_xpix

