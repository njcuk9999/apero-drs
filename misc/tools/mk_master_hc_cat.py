import numpy as np
import glob
from astropy.io import fits
from astropy.table import Table
import matplotlib.pyplot as plt

# fine HC lines to be used. We only want A, B and C, *not* AB as it is
# a linear combination of AB and does not provide an independent measure
files = np.sort(glob.glob('*/*_wave_hclines*.fits'))

for i in range(len(files)):
    if 'AB' in files[i]:
        files[i] = ''
files = files[files != '']

# get a vector of all HC lines ever seen
all_wave_ref = []
for i in range(len(files)):
    print(files[i])
    tbl = Table(fits.getdata(files[i]))
    # append all WAVE_REF
    all_wave_ref = np.append(all_wave_ref, np.array(tbl['WAVE_REF']))

# get unique values
all_wave_ref = np.unique(all_wave_ref)

# map of all WAVE_MEAS for all files. Padded with NaNs so that
# images for which lines have not been seen are rejected
all_wave_meas = np.zeros([len(all_wave_ref), len(files)]) + np.nan
all_wave_amp = np.zeros([len(all_wave_ref), len(files)]) + np.nan

# pad the map
for i in range(len(files)):
    print(files[i])
    tbl = Table(fits.getdata(files[i]))
    for j in range(len(all_wave_ref)):
        g = np.where(tbl['WAVE_REF'] == all_wave_ref[j])[0]
        if len(g) == 0:
            continue
        all_wave_meas[j, i] = np.mean(tbl['WAVE_MEAS'][g])
        all_wave_amp[j, i] = np.mean(tbl['AMP_MEAS'][g])

# median value is the new reference grid
wave_meas = np.nanmedian(all_wave_meas, axis=1)
amp_meas = np.nanmedian(all_wave_amp, axis=1)

all_wave_meas_mad = np.array(all_wave_meas)
for i in range(len(wave_meas)):
    all_wave_meas_mad[i] -= wave_meas[i]

mad = np.nanmedian(np.abs(all_wave_meas_mad), axis=1)
ngood = np.nansum(np.isfinite(all_wave_meas), axis=1)

# good lines are seen more than 50% of the time
keep = ngood > len(files) // 2

wave_meas, amp_meas = wave_meas[keep], amp_meas[keep]
mad, ngood, all_wave_ref = mad[keep], ngood[keep], all_wave_ref[keep]
all_wave_meas = all_wave_meas[keep]
all_wave_amp = all_wave_amp[keep]
all_wave_meas_mad = all_wave_meas_mad[keep]

# maybe some cuts in Median Absolute Deviation ?
# we keep the info until now, but don't use it yet

tbl_out = Table()
tbl_out['wavelength'] = wave_meas
tbl_out['strength'] = amp_meas
tbl_out['ID'] = '@SPIROU'

tbl_out.write('new_master_table.csv', overwrite=True)

fig, ax = plt.subplots(nrows=2, ncols=1, sharex=True, sharey=True)

for i in range(len(files)):
    dv = (1 - all_wave_meas[:, i] / all_wave_ref) * 2.99e8
    rms1 = (np.nanpercentile(dv, 84) - np.nanpercentile(dv, 16)) / 2

dv = (1 - all_wave_meas[:, i] / wave_meas) * 2.99e8
rms2 = (np.nanpercentile(dv, 84) - np.nanpercentile(dv, 16)) / 2

print('before rms = {0:6.2f} m/s, after rms = {1:6.2f} m/s'.format(rms1, rms2))

ax[0].plot(all_wave_ref, (1 - all_wave_meas[:, i] / all_wave_ref) * 2.99e5, '.')
ax[1].plot(wave_meas, (1 - all_wave_meas[:, i] / wave_meas) * 2.99e5, '.')

ax[0].set(xlabel='Wavelength (nm)', ylabel='dv [km/s]', title='initial HC list')

ax[1].set(xlabel='Wavelength (nm)', ylabel='dv [km/s]', title='updated HC list')
