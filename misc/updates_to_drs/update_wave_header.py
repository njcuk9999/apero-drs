from astropy.io import fits


def change_num_key(header, key, prefix, newkey):
	try:
		numberkey = int(key.split(prefix)[-1])
		newkey = newkey.format(numberkey)
		header[newkey] = (header[key], header.comments[key])
	except:
		pass
	return header



filename = 'MASTER_WAVE.fits'
# filename = '/scratch/Projects/spirou/data_dev/calibDB/TEST1_20180805_2295515f_pp_loco_AB.fits'
# filename = '/scratch/Projects/spirou/data_dev/calibDB/TEST1_20180805_2295510f_pp_loco_C.fits'

data, header = fits.getdata(filename, header=True)


for key in header:
	if 'TH_LC' in key:
		header = change_num_key(header, key, 'TH_LC', 'WAVE{0:04d}')

	if 'LOCTR' in key:
		header = change_num_key(header, key, 'LOCTR', 'LOCE{0:04d}')

	if 'LOFW' in key:
		header = change_num_key(header, key, 'LOFW', 'LOFW{0:04d}')

	if key == 'TH_ORD_N':
		header['WAVEORDN'] = (header[key], header.comments[key])

	if key == 'TH_LL_D':
		header['WAVEDEGN'] = (header[key], header.comments[key])



fits.writeto(filename, data, header=header, overwrite=True)