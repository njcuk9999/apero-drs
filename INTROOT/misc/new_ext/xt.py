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

from SpirouDRS import *
from SpirouDRS import spirouDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup
from debanananificator import *
from scipy.optimize import curve_fit
from get_offset_sp import *




# FP file for tilt/dx determination

date = 1

if date ==0:
	# 2018-08-03
	slope_file = '2295305a_pp.fits'
	hc_file    = '2295196c_pp.fits'
	cal_loc_param_file = "2295305a_pp_e2dsff_AB.fits"

if date ==1:
	# 2018-05-28
	slope_file = '2279725a_pp.fits'
	hc_file = '2279808c_pp.fits'
	cal_loc_param_file = "2279725a_pp_e2dsff_AB.fits"


if date ==2:
	# 2018-05-28
	slope_file = '2279725a_pp.fits'
	hc_file = '2279808c_pp.fits'
	cal_loc_param_file = "2279725a_pp_e2dsff_AB.fits"



outname = (slope_file.split('_'))[0]+'_dxmap.fits' 

hdr_extract_params = pyfits.getheader(cal_loc_param_file)
# width of the ABC fibres.
wpix = 60

__NAME__= 'anything'
p = spirouStartup.Begin(recipe=__NAME__)
p = spirouStartup.LoadArguments(p)

n_ord = hdr_extract_params["LONBO"]//2
n_coeff = len(hdr_extract_params['LOFW[0-9]*'])//(n_ord*2)

ordfit=5
poly_c = np.zeros( [n_coeff,n_ord*2] )
LOCTR = hdr_extract_params['LOCTR*']
for ord in range(0,n_ord*2,2):
	for coeff in range(ordfit):
		i = (ord*n_coeff)+coeff
		poly_c[i % n_coeff,i//n_coeff] = hdr_extract_params["LOCTR"+str(i)]

poly_c = poly_c[:,poly_c[0,:]!=0]

datac = (pyfits.getdata(slope_file))
hdr = pyfits.getheader(slope_file)
p = spirouImage.GetSigdet(p, hdr, name='sigdet')
# get exposure time
p = spirouImage.GetExpTime(p, hdr, name='exptime')
# get gain
p = spirouImage.GetGain(p, hdr, name='gain')

data = spirouImage.ConvertToE(spirouImage.FlipImage(p, datac), p=p)
# convert NaN to zeros
data0 = np.where(~np.isfinite(data), np.zeros_like(data), data)
# resize image
bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],getshape=False)
data1 = spirouImage.ResizeImage(p, data0, **bkwargs)




###################### reading and handling the 2D HC image ############
data_hc = (pyfits.getdata(hc_file))

data_hc = spirouImage.ConvertToE(spirouImage.FlipImage(p, data_hc), p=p)
# convert NaN to zeros
data0_hc = np.where(~np.isfinite(data_hc), np.zeros_like(data_hc), data_hc)
# resize image
data1_hc = spirouImage.ResizeImage(p, data0_hc, **bkwargs)
########################################################################



doplot = True
idplot = 35
force = True

# dxmap that will contain the dx per pixel
# if the file does not exist, we fill the map
# with zeros


if (glob.glob(outname) != []) & (force==False):
	print(outname+' exists... we use its values as a starting point')
	master_dxmap = pyfits.getdata(outname)
	master_dxmap[~np.isfinite(master_dxmap)]=0
	# number of banana iterations, = 1 if file exists
	nbanana = 4
else:
	master_dxmap=np.zeros_like(data1)#+np.nan
	# number of banana iterations, = 3 if file does not exists
	nbanana = 4

map_orders = np.zeros_like(data1)-1
order_overlap = np.zeros_like(data1)

# iterating the correction, from coarser to finer
for ite_banana in range(nbanana):
	# we use the code that will be used by the extraction to ensure that slice
	# images are as straight as can be

	# if the map is not zeros, we use it as a starting point
	if np.nansum(master_dxmap!=0)!=0:
		data2 = debanananificator(data1,master_dxmap)
		data2_hc = debanananificator(data1_hc,master_dxmap)
		flag_start_slope=False
	else:
		data2 = np.array(data1)
		data2_hc = np.array(data1_hc)
		flag_start_slope=True

	sz=np.shape(data2)

	if flag_start_slope:
		# starting point for slope exploration
		range_slopes_deg = [-12.0,0.0]
	else:
		# if this is not the first iteration, then we must be really close
		# to a slope of 0
		range_slopes_deg = [-1.0,1.0]

	# expressed in pixels, not degrees
	range_slopes=np.tan(np.array(range_slopes_deg)/180*np.pi)

	# looping through orders
	for iord in range(30,31): #n_ord):

		#if iord == idplot:
		#	doplot=True
		#else:
		#	doplot=False

		#doplot=False
		#if iord == 35:
		#	doplot=True


		print()
		print('Nth order : ',iord+1,'/',n_ord,' || banana iteration : ',ite_banana+1,'/',nbanana)

		# x pixel vecctor that is used with polynomials to 
		# find the order center
		xpix=np.array(range(4088))
		# y order center
		ypix=np.polyval( (poly_c[:,iord])[::-1],xpix)

		# defining a ribbon that will contain the straightened order
		ribbon=np.zeros([wpix,4088])
		ribbon_hc=np.zeros([wpix,4088])

		# spling the original image onto the ribbon
		for i in range(4088):
			bot = int(ypix[i]-wpix/2-2)
			top = int(ypix[i]+wpix/2+2)
			if bot >0:
				spline=InterpolatedUnivariateSpline(np.arange(bot,top),data2[bot:top,i],ext=1,k=3)
				ribbon[:,i]=spline(ypix[i]+np.arange(wpix)-wpix/2.)
				# handling of the HC
				spline_hc=InterpolatedUnivariateSpline(np.arange(bot,top),data2_hc[bot:top,i],ext=1,k=3)
				ribbon_hc[:,i]=spline_hc(ypix[i]+np.arange(wpix)-wpix/2.)
		#
		# normalizing ribbon stripes to their median abs dev
		for i in range(wpix):
			amp_corr = np.nanmedian(np.abs(ribbon[i,:]))
			ribbon[i,:]/=amp_corr
			ribbon_hc[i,:]/=amp_corr

		# range explored in slopes
		slopes = np.array(range(0,9))*(range_slopes[1]-range_slopes[0])/8.0+range_slopes[0]

		print('range slope exploration : ',range_slopes_deg[0],' -> ',range_slopes_deg[1],' deg')
		xpix=np.arange(4088)

		# the domain is sliced into a number of sections, then we find the tilt that
		# maximizes the RV content
		nsections = 32
		xsection=4088*(np.arange(nsections)+0.5)/nsections
		dxsection=np.zeros_like(xsection)+np.nan

		# rv content per slice and per slope
		rvcontent=np.zeros([len(slopes),nsections])

		islope=0
		for slope in slopes:
			ribbon2=np.array(ribbon)
			for i in range(wpix):
				ddx=(i-wpix/2.)*slope
				spline=InterpolatedUnivariateSpline(xpix,ribbon[i,:],ext=1)
				ribbon2[i,:]=spline(xpix+ddx)
			profil=np.nanmedian(ribbon2,axis=0)

			for k in range(nsections):
				# sum of integral of derivatives == RV content. This should be maximal
				# when the angle is right
				rvcontent[islope,k]=np.nansum(np.gradient(profil[k*4088//nsections:(k+1)*4088//nsections])**2)
			islope+=1
		#
		# we find the peak of RV content and fit a parabola to that peak
		for k in range(nsections):
			# we must have some RV content (i.e., !=0)
			if np.nanmax(rvcontent[:,k])!=0:
				v=np.ones_like(slopes)
				v[0]=0
				v[-1]=0
				maxpix=np.nanargmax(rvcontent[:,k]*v)
				# max RV and fit on the neighbouring pixels
				fit = np.polyfit(slopes[maxpix-1:maxpix+2],rvcontent[maxpix-1:maxpix+2,k],2)
				# if peak within range, then its fine
				if (np.abs(-.5*fit[1]/fit[0])<1):
					dxsection[k]=-.5*fit[1]/fit[0]
		#
		# we sigma-clip the dx[x] values relative to a linear fit
			keep=np.isfinite(dxsection)
		sigmax=99
		while sigmax>4:
			fit=np.polyfit(xsection[keep],dxsection[keep],2)
			res=(dxsection-np.polyval(fit,xsection))
			res-=np.nanmedian(res[keep])
			res/=np.nanmedian(np.abs(res[keep]))
			sigmax=np.nanmax(np.abs(res[keep]))
			keep &= (np.abs(res)<4)
		#
		# we fit a 2nd order polynomial to the slope vx position along order
		fit=np.polyfit(xsection[keep],dxsection[keep],2)
		print('slope at pixel 2044 : ',np.arctan(np.polyval(fit,2044))*180/np.pi,' deg')
		slope = np.polyval(fit,np.arange(4088))
		#
		# some plots to show that the slope is well behaved
		#plt.subplot(1,2,1)

		if doplot:
			slope_deg=np.arctan(dxsection[keep])*180/np.pi
			plt.plot(xsection[keep],slope_deg,'go')
			plt.plot(np.arange(4088),np.arctan(slope)*180/np.pi)
			ylim=[np.nanmin(slope_deg)-.2,np.nanmax(slope_deg)+.2]
			plt.ylim(ylim)
			plt.xlabel('x pixel')
			plt.ylabel('slope (deg)')
			plt.show()
			plt.clf()
		#
		# correct for the slope the ribbons and look for the slicer profile
		for i in range(wpix):
			ddx=(i-wpix/2.)*np.polyval(fit,xpix)
			spline=InterpolatedUnivariateSpline(xpix,ribbon[i,:],ext=1)
			ribbon2[i,:]=spline(xpix+ddx)

		# correct for the slope the ribbons and look for the slicer profile
		ribbon2_hc=np.array(ribbon_hc)
		for i in range(wpix):
			ddx=(i-wpix/2.)*np.polyval(fit,xpix)
			spline_hc=InterpolatedUnivariateSpline(xpix,ribbon_hc[i,:],ext=1)
			ribbon2_hc[i,:]=spline_hc(xpix+ddx)

		sp_fp = np.nanmedian(ribbon2,axis=0)
		sp_hc = np.nanmedian(ribbon2_hc,axis=0)

		corr_dx_from_fp = get_offset_sp(sp_fp,sp_hc,iord,doplot=doplot)

		# median FP peak profile. We will cross-correlate each row of the
		# ribbon with this
		profil = np.nanmedian(ribbon2,axis=0)
		profil -= scipy.ndimage.filters.median_filter(profil,51)

		dx=np.zeros(wpix)+np.nan
		ddx=np.arange(-3,4)

		# cross-correlation peaks of median profile VS position along ribbon
		cc=np.zeros([wpix,len(ddx)],dtype=float)
		for i in range(wpix):
			for j in range(len(ddx)):
				cc[i,j] = (pearsonr(ribbon2[i,:],np.roll(profil,ddx[j])))[0]
			# fit a gaussian to the CC peak
			g,gg=gaussfit(ddx,cc[i,:],4)
			if np.nanmax(cc[i,:])>(0.1):
				dx[i]=g[1]

		#
		dypix=np.arange(len(dx))
		keep=np.abs(dx-np.nanmedian(dx))<1
		keep &= np.isfinite(dx)

		# if the first pixel is nan and the second is OK, then for continuity, pad
		if keep[0]==0 and keep[1]==1:
			keep[0]=True
			dx[0]=dx[1]

		# same at the other end
		if keep[-1]==0 and keep[-2]==1:
			keep[-1]=True
			dx[-1]=dx[-2]

		# some more graphs
		#plt.subplot(1,2,2)
		if doplot:
			plt.imshow(cc,aspect=.2)
			plt.ylim([0,wpix-1])
			plt.xlim([0,len(ddx)-1])
			plt.plot(dx-np.min(ddx),dypix,'ro')
			plt.plot(dx[keep]-np.min(ddx),dypix[keep],'go')
			plt.show()
			plt.clf()

		# spline everything onto the master DX map
		# ext=3 forces that out-of-range values are set to boundary value
		# this simply uses the last reliable dx measurement for the neighbouring slit position
		spline=InterpolatedUnivariateSpline(dypix[keep],dx[keep],ext=3)

		maxcc = np.nanmax(cc,axis=1) # we find the pixels where the correlation with median profile is >0.3 and add 1 pixel of buffer
		start_good_cc = np.min(np.where(maxcc >0.3))-1
		if start_good_cc ==(-1):
			start_good_cc = 0
		end_good_cc = np.max(np.where(maxcc >0.3))+2
		if end_good_cc ==(wpix):
			end_good_cc = (wpix-1)

		good_cc_mask = np.zeros_like(maxcc)
		good_cc_mask[start_good_cc:end_good_cc]=1

		print('start of good data along slice : ',start_good_cc)
		print('end of good data along slice : ',end_good_cc)

		#stop
		# for all field positions along the order, we determine the dx+rotation
		# values and update the master DX map
		for i in range(4088):
			frac=(ypix[i]-np.fix(ypix[i]))
			dx0=(np.array(range(wpix))-wpix//2.+(1-frac))*slope[i]
			ypix2=int(ypix[i])+np.array(range(-wpix//2,wpix//2))
			ddx=spline(np.array(range(wpix))-frac )
			ddx[ddx==0]=np.nan

			g=(ypix2>=0) & (good_cc_mask == 1)
			
			if np.nansum(g)!=0:
				if ite_banana ==0:
					order_overlap[ypix2[g],i] += (map_orders[ypix2[g],i] != (-1) )
					map_orders[ypix2[g],i]=iord

				master_dxmap[ypix2[g],i]+=((ddx+dx0)[g]-corr_dx_from_fp[i])

# setting to 0 pixels that are NaNs
master_dxmap[~np.isfinite(master_dxmap)]=0
master_dxmap[order_overlap !=0 ]=0

# applying the very last update of the debanananificator
data2 = debanananificator(data1,master_dxmap)
data2_hc = debanananificator(data1_hc,master_dxmap)

# distortions where there is some overlap between orders will be wrong
master_dxmap[order_overlap != 0]=0

# all sorts of outputs for sanity check
pyfits.writeto('starting_'+slope_file,data1,clobber=True)
pyfits.writeto('corrected_'+slope_file,data2,clobber=True)
pyfits.writeto('starting_'+hc_file,data1_hc,clobber=True)
pyfits.writeto('corrected_'+hc_file,data2_hc,clobber=True)
pyfits.writeto('order_overlap_'+slope_file,order_overlap,clobber=True)

# necessary output if we want to update the wavelenght solution
# to minimize the shape correction
pyfits.writeto('map_orders'+slope_file,map_orders,clobber=True)

pyfits.writeto(outname,master_dxmap,clobber=True)



