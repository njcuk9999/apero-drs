import numpy as np
import glob
import matplotlib.pyplot as plt
from scipy.interpolate import InterpolatedUnivariateSpline as ius
import os
from astropy.io import fits
from astropy.table import Table


def fast_med(vect,w):
    #
    # inputs : vect -> vector to be median-filtered
    #             w -> width of the filtering. Needs to be much shorter than 
    #                  the length of vect
    # 
    # performs a fast median filter for a box width that is too long to
    # be used with the normal numpy median filter. 
    # The code performs a 'true' median with numpy, but does not
    # shift by 1 pixel as would be done with a true boxcar.
    # It moves by 1/2 of the width and splines in between.
    #
    
    # index of points along vector
    index = np.arange(len(vect),dtype=float)
    # index only on non-nans, all others are set to nans.
    # this ensures that the splining is properly centered if there is a 
    # big bunch of NaNs on a width close to w
    index[np.isfinite(vect)==False]=np.nan
    
    # reshaping the vector in a form so that we can use the axis
    # keyword to do the job of a running boxcar. For a 1000-long vect and w=10
    # this would be equivalent to reformating into a 100x10 array and then taking
    # the median with axis=1.
    # This is the same a taking a running median with a size of 10, and getting
    # the value every 10 pixels
    y1 = np.nanmedian(np.reshape( vect[0:w*(len(vect)//w)],[len(vect)//w,w]),axis=1)
    # same but with an offset of 0.5*w
    y2 = np.nanmedian(np.reshape( (np.roll(vect,w//2))[0:w*(len(vect)//w)],[len(vect)//w,w]),axis=1)
    
    # same median as for the vect value, but for the position along vect
    x1 = np.nanmedian(np.reshape( index[0:w*(len(vect)//w)],[len(vect)//w,w]),axis=1)
    x2 = np.nanmedian(np.reshape( (np.roll(index,w//2))[0:w*(len(vect)//w)],[len(vect)//w,w]),axis=1)
    
    # append the median-binned at each w*integer with w*(integer+0.5)
    x=np.append(x1,x2)
    y=np.append(y1,y2)
    ind = np.argsort(x)
    # get the binned vectors in order of index
    x=x[ind]
    y=y[ind]
    # remove NaNs. There may be stretches of vect larger than w that are full
    # of NaNs. We also use np.roll to remove points of identical x
    keep = np.isfinite(x) & (x != np.roll(x,1)) & np.isfinite(y)
    x=x[keep]
    y=y[keep]
    
    # spline the whole thing onto the vect grid
    spline = ius(x,y,k=2,ext=1)
    med_filt_vect = spline( np.arange(len(vect),dtype=float))
    med_filt_vect[np.isfinite(vect) == False]=np.nan
    
    #output median-filtered vector
    return med_filt_vect

obj = 'Gl699'
# all s1d files MUST be located in a directory with the name of the
# target and _AB as a suffix
all_AB = np.sort(glob.glob(obj+'_AB/2[2-9]*AB*_tellu_corrected.fits'))

rms_threshold = 0.015
# widh=th of high-pass filtering to match 
# the SED of all input files
width_high_pass = 501

# width of CCF lines in the mask
width_ccf = 1.0 # km/s

# systemic velocity of the star
systemic_velocity = -110.0


c = 299792.458 # speed of light in km/s


# we expect the RMS telluric vector file to be provided
# it serves to mask bad wavelength domains and will be used to 
# mask poor regions
tbl = Table.read('tellu_rms.csv')

wave = np.array(tbl['wavelength'])

if os.path.exists('all_'+obj+'.fits') == False:
    # sort all files in increasing wavelength order
    all_AB.sort()
    
    # we mask the domain between 1300 and 1450 as we know it is always bad
    rms_tellu = np.array(tbl['rms'])
    rms_tellu[np.isfinite(rms_tellu) == False]=1.0
    # rms_tellu[(wave>1300) & (wave<1450)] = 1.0
    
    # create a 2d matrix to hold all spectra with and without BERV shift
    all_flux_no_shift = np.zeros([len(wave),len(all_AB)])+np.nan
    all_flux = np.zeros([len(wave),len(all_AB)])
    index = np.arange(len(wave),dtype=float)
    
    # rms in tellurics is smaller than threshold
    g = rms_tellu<rms_threshold
    i=0
    h=fits.Header()
    
    # loop through the files and pad them into the appropriate matrices
    # also keep track of some relevant keywords
    # we set to NaN all values in regions where the RMS of tellurics above
    # RMS threshold
    for fic in all_AB:
        print(i,len(all_AB),fic)
        # looping through input files
        tbl,hdr = fits.getdata(fic,ext=1,header=True)
        berv = np.float(hdr['BERV'])
    
    
        stri = str(i+1)
        if len(stri) !=4:
            stri='0'*(4-len(stri))+stri
            
        h['FILE'+stri] = (((fic.split('_pp_'))[0]).split('/'))[1]
        h['BERV'+stri] = berv,'BERV of input file '+h['FILE'+stri]
        h['DATE'+stri] = hdr['DATE'],'DATE of input file '+h['FILE'+stri]
        h['MJDA'+stri] = float(hdr['MJDATE']),'MJDATE of input file '+h['FILE'+stri]
        
        flux = tbl['flux']
        #normalize by median
        flux/=np.nanmedian(flux)
        # spline valid values onto the final grid after BERV
        spline = ius(index[g],flux[g],k=3,ext=1)
        # spline a weight mask onto the final grid 
        spline_mask = ius(index,np.array(g,dtype=float),k=3,ext=1)
        
        # no BERV correction
        all_flux_no_shift[g,i] = flux[g]
        
        # spline to BERV
        # as we are using a wavelength grid that is in 1 km/s steps, we just
        # spline the indices and add berv as if it were a pixel offset
        tmp1=spline(index-berv)
        tmp2=spline_mask(index-berv)
        
        # Mask bits with <0.7 mask throughput
        tmp1[tmp2<0.7] = np.nan
        all_flux[:,i] = tmp1
    
        i+=1
    # save big matrices before and after BERV correction
    fits.writeto('all_no_shift_'+obj+'.fits',all_flux_no_shift,h,overwrite=True)
    fits.writeto('all_'+obj+'.fits',all_flux,h,overwrite=True)

# correct the big matrix for low-frequencies
if os.path.exists('all_'+obj+'_corr_lowfreq.fits') == False:
    all_flux,h = fits.getdata('all_'+obj+'.fits',header=True)
    
    # 
    for ite in range(2):
        med = np.nanmedian(all_flux,axis=1)
        for i in range((np.shape(all_flux))[1]):
            print(i,ite)
            all_flux[:,i] /= fast_med(all_flux[:,i]/med,width_high_pass)
 
    fits.writeto('all_'+obj+'_corr_lowfreq.fits',all_flux,h,overwrite=True)
  

# save ouput to CSV
# csv has 3 columns, one for wavelength, one for flux, one for RMS
if os.path.exists('template_'+obj+'.csv') == False:

    all_flux = fits.getdata('all_'+obj+'_corr_lowfreq.fits')
        
    med = np.nanmedian(all_flux,axis=1)
    for i in range((np.shape(all_flux))[1]):
        all_flux[:,i] -= med
    
    rms = np.nanmedian(np.abs(all_flux),axis=1)
    bad = ~((rms<0.1) & (med>0))
    med[bad] = np.nan  
    rms[bad] = np.nan  
    
    tbl_out = Table()
    tbl_out['wavelength'] = wave 
    tbl_out['flux'] = med
    tbl_out['rms'] = rms

    tbl_out.write('template_'+obj+'.csv',format='ascii.csv',overwrite=True)





# create a mask for CCF computation from the template
tbl_out = Table.read('template_'+obj+'.csv',format='csv')
wave = np.array(tbl_out['wavelength'])
flux = np.array(tbl_out['flux'])

# find the gradient of the spectrum. All lines will be found as points where
# the gradient is zero.
grad = np.gradient(flux,edge_order=2)

# find points where the gradient goes from negative to positive or the other
# way around. 
g=(np.sign(grad[1:]) != np.sign(grad[:-1])) & (np.isfinite(grad[1:])) & (np.isfinite(grad[:-1]))

# find lines within 1 pixel
line = (np.where(g))[0]

# this is the local slope of the derivative. 
slope = -grad[line+1]-grad[line] 
# this is the local slope change (i.e. second derivative). Used as an 
# indication of line strength
slope_wave = (grad[line+1]-grad[line] ) / (wave[line+1]-wave[line])
wave_line = wave[line]+grad[line]/slope_wave


tbl= Table()
tbl['WAVE_START'] = wave_line*(1-0.5*width_ccf/c)
tbl['WAVE_END'] = wave_line*(1+0.5*width_ccf/c)
tbl['STRENGTH'] = slope_wave

tbl.write('lines_'+obj+'.csv',format='csv')


plt.plot(wave ,flux)
plt.show()

    