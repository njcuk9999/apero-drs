import numpy as np
from astropy.io import fits
from astropy.table import Table
from scipy.interpolate import InterpolatedUnivariateSpline
import matplotlib.pyplot as plt
#from scipy.signal import medfilt

# Your input template
template = 'Template_s1d_Gl699_sc1d_v_file_AB.fits'
# template = 'Template_s1d_Gl15A_sc1d_v_file_AB.fits'
# template = 'Template_s1d_HD189733_sc1d_v_file_AB.fits'

c = 2.99792458e5 # speed of light

# read wavelength and flux. The wavelength is expressed in Ang, we convert to µm
wave_phoenix = fits.getdata('WAVE_PHOENIX-ACES-AGSS-COND-2011.fits') / 10

# bit of code to download goettigen models. Use only you don't have the models locally and change the False to True
if False:
    import os as os

    for temperature in np.arange(3000, 6100, 100):
        temperature = str(np.int(np.round(temperature, -2)))
        print(temperature)
        os.system(
            'wget ftp://phoenix.astro.physik.uni-goettingen.de/HiResFITS/PHOENIX-ACES-AGSS-COND-2011/Z-0.0/lte0' + temperature + '-4.50-0.0.PHOENIX-ACES-AGSS-COND-2011-HiRes.fits')

# read template and header
tbl, hdr = fits.getdata(template, ext=1, header=True)

# round temperature in header to nearest 100 and get the right model
if 'OBJTEMP' in hdr:
    temperature = hdr['OBJTEMP']
    if temperature < 3000:
        temperature = 3000
    if temperature > 6000:
        temperature = 6000

    temperature = str(np.int(np.round(temperature, -2)))
else:
    # if the header does not have a temperature value, assume it is an early-M. This does not really change much
    temperature = '3600'

# tell the user which model you are using
print('Temperature = ', temperature)
model_file = 'lte0' + temperature + '-4.50-0.0.PHOENIX-ACES-AGSS-COND-2011-HiRes.fits'
print('Model file = ', model_file)
flux_phoenix = fits.getdata(model_file)

# get wave and flux vectors for the template
w = np.array(tbl['wavelength'])
f = np.array(tbl['flux'])

# smooth the template with a 7 km/s boxcar. This avoids lines due to spurious noise excursions
f2 = np.array(f)
mask = np.isfinite(f)
f2[~mask] = 0
mask = mask*1.0
# smooth by a boxcar and divide by a weight vector to avoid discontinuities at the edge or regions with NaNs
f = np.convolve(f2,np.ones(7), mode = 'same')/np.convolve(mask,np.ones(7), mode = 'same')

# find the first and second derivative of the flux
df = np.gradient(f)
ddf = np.gradient(np.gradient(f))

# lines are regions there is a sign change in the derivative of the flux
# we also have some checks for NaNs
line = np.where((np.sign(df[1:]) != np.sign(df[:-1])) &
                np.isfinite(ddf[1:])
                & np.isfinite(df[1:])
                & np.isfinite(df[:-1]))[0]

# create the output table
tbl = Table()
tbl['ll_mask_s'] = np.zeros_like(line, dtype=float)
tbl['ll_mask_e'] = np.zeros_like(line, dtype=float)


dv = 0# mask width in km/s. Set to zero, but could be changed
for i in range(len(line)):
    # we perform a linear interpolation to find the exact wavelength
    # where the derivatives goes to zero
    wave_cen = (np.polyfit(df[line[i]:line[i] + 2], w[line[i]:line[i] + 2], 1))[1]

    # historically, masks are defined over a box of a given width (hence the 's' "start" and the 'e' "end" here)
    # here the two values are that same, but one could have a non-zero dv value
    corrv = np.sqrt((1 + (-dv / 2) / c) / (1 - (-dv / 2) / c))
    tbl['ll_mask_s'][i] = wave_cen * corrv

    # same but for the upper bound to the line position
    corrv = np.sqrt((1 + (dv / 2) / c) / (1 - (dv / 2) / c))
    tbl['ll_mask_e'][i] = wave_cen * corrv

# wavelength of lines is the mean of start and end.
wavelines = (tbl['ll_mask_s'] + tbl['ll_mask_e']) / 2.0

# the weight is the second derivative of the flux. The sharper the line,
# the more weight we give it

g = np.isfinite(ddf)
weight = InterpolatedUnivariateSpline(w[g], ddf[g])(wavelines)

# weight will be the second derivative
tbl['w_mask'] = weight

# create a spline of the model
model = InterpolatedUnivariateSpline(wave_phoenix, flux_phoenix)

# assume a 0 velocity and search
dv0 = 0.0 #
scale = 1.0
for ite in range(2):
    dvs = np.arange(400, dtype=float)
    dvs -= np.mean(dvs)

    dvs *= scale
    dvs += dv0

    # loop in velocity space and fill the CCF values for each velocity step
    ccf = np.zeros_like(dvs)

    # this is the line to change if you want to have positive or negative features
    mask = weight>0
    for i in range(len(dvs)):
        corrv = np.sqrt((1 + dvs[i] / c) / (1 - dvs[i] / c))

        # lines that will be used in the CCF mask
        ccf[i] = np.sum(model(wavelines[mask] / corrv))

    # just centering the cc around one and removing low-f trends.
    mini = np.argmin(ccf)
    dv0 = dvs[mini]
    scale /= 10.0


    plt.plot(dvs, ccf)
plt.show()

# find the lowest point in the CCF
minpos = np.argmin(ccf)
# fit a 2nd order polynomial to the bottom pixels (-1 to +1 from bottom) and find minimimum point
fit = np.polyfit(dvs[minpos - 1:minpos + 2], ccf[minpos - 1:minpos + 2], 2)
# minimum of a 2nd order polynomial
systemic_velocity = -.5 * fit[1] / fit[0]

# return systemic velocity measured
print('systemic velocity : ', systemic_velocity, 'km/s')

# generate a nice plot to show positive/negative features
wavelines =tbl['ll_mask_s']

# find flux at sub-pixel position of lines
g = np.isfinite(f)
flux_lines = InterpolatedUnivariateSpline(w[g], f[g])(wavelines)

plt.plot(w,f, 'g-',label = 'spectrum')
pos_lines = np.array(tbl['w_mask'] < 0)
plt.plot(np.array(wavelines[pos_lines]),flux_lines[pos_lines],'r.', label = 'positive features')
neg_lines = np.array(tbl['w_mask'] > 0)
plt.plot(np.array(wavelines[neg_lines]),flux_lines[neg_lines],'b.', label = 'negative features')
plt.legend()
plt.show()

# updating the table to account for systemic velocity of star
corrv = np.sqrt((1 + systemic_velocity / c) / (1 - systemic_velocity / c)) # relativistic Doppler
tbl['ll_mask_s'] = tbl['ll_mask_s'] / corrv
tbl['ll_mask_e'] = tbl['ll_mask_e'] / corrv


# write the output table
fits.writeto(hdr['OBJECT'] + '.fits', tbl, hdr, overwrite=True)

tbl[tbl['w_mask'] < 0].write(hdr['OBJECT'] + '_pos.mas', format='ascii', overwrite=True)
tbl[tbl['w_mask'] > 0].write(hdr['OBJECT'] + '_neg.mas', format='ascii', overwrite=True)
tbl.write(hdr['OBJECT'] + '_full.mas', format='ascii', overwrite=True)




