import numpy as np
import glob
from astropy.io import fits
from tqdm import tqdm

# provide a vector of all darks
all_darks = np.array(glob.glob('2*d_pp.fits'))

# julian date to know which file we need to
# process together
dark_time = np.zeros(len(all_darks))

# looping through the file headers
for i in tqdm(np.arange(len(all_darks)), leave=False):
    hdr = fits.getheader(all_darks[i])
    dark_time[i] = float(hdr['MJDATE'])

# ID of matched multiplets of files
matched_id = np.zeros_like(dark_time, dtype=int)

# loop until all files are matched with all other files taken within
# 2 hours
ii = 1
while np.min(matched_id) == False:
    gg = (np.where(matched_id == 0))[0]
    g = gg[np.argmin(gg)]
    gm = np.abs(dark_time[g] - dark_time) < 2.0 / 24.0

    matched_id[gm] = ii
    ii += 1

# find all matched batches
u_ids = set(matched_id)

# how many bins of median darks. The 'long' option has 1 bin per
# epoch of +-2 hours
nbins = len(u_ids)
i = 0

# looping through epochs
for u_id in tqdm(u_ids, leave=False):

    # find all files at that epoch
    darks_id = all_darks[np.where(matched_id == u_id)]
    cube = []
    for fic in darks_id:
        cube.append(fits.getdata(fic))

    # median dark for that epoch
    dark = np.nanmedian(cube, axis=0)

    sz = np.shape(dark)

    # put all the medians in a bigger cube
    if i == 0:
        dark_cube = np.zeros([nbins, sz[0], sz[1]])
        w = np.zeros(nbins)

    # average within each bin
    dark_cube[i % nbins, :, :] += dark
    w[i % nbins] += 1
    i += 1

# normalize if we have more bins than 1
for i in tqdm(range(nbins)):
    dark_cube[i, :, :] /= w[i]

# we perform a median filtering over a -4 to +4 pixel box.
for i in tqdm(range(nbins)):
    dark = dark_cube[i, :, :]

    # performing a median filter of the image
    # with [-4,4] box in x and 1 pixel wide in y. Skips the pixel considered,
    # so this is equivalent of a 8 pixel boxcar.
    tmp = []
    for j in range(-4, 5):
        if j != 0:
            tmp.append(np.roll(dark, [0, j]))

    # low frequency image
    dark_lf = np.nanmedian(tmp, axis=0)
    # high frequency image
    dark_cube[i, :, :] = dark - dark_lf

fits.writeto('test.fits', np.nanmedian(dark_cube, axis=0), overwrite=True)
