import cal_extract_RAW_spirou
import glob
import os

PATH = '/spirou/data/raw/tells/*pp.fits'
NIGHT_NAME = 'tells'

files = glob.glob(PATH)

for filename in files:
    basename = os.path.basename(filename)
    ll = cal_extract_RAW_spirou.main(NIGHT_NAME, files=basename)
