import glob
import os


inputpath = '/spirou/data/raw/**'
outputpath = '/spirou/data/raw/tells/'

codes = ['2278951o', '2278952o', '2279005o', '2279006o', '2279007o', '2279008o',
         '2279009o', '2279010o', '2279017o', '2279018o', '2279019o', '2279020o',
         '2279104o', '2279197o', '2279271o', '2279272o', '2279273o', '2279346o',
         '2279399o', '2279400o', '2279401o', '2279402o', '2279404o', '2279405o',
         '2279416o', '2279427o', '2279438o', '2279457o', '2279458o', '2279459o',
         '2279460o', '2279461o', '2279462o', '2279463o', '2279536o', '2279540o',
         '2279541o', '2279542o', '2279697o']

# get folders
all_files = glob.glob(inputpath, recursive=True)
# storage for required paths
required_paths = []

for code in codes:
    # print progress
    print('Locating code = {0}'.format(code))
    found = False
    # search folders
    for all_file in all_files:
        # check is file
        if not os.path.isfile(all_file):
            continue
        if code in all_file:
            required_paths.append(all_file)
            found = True
    # log if found
    if found:
        print('\tFound code.')
    else:
        print('\tCode not found.')

# copy all to new path
for oldpath in required_paths:
    basefilename = os.path.basename(oldpath)
    newpath = os.path.join(outputpath, basefilename)
    print('Copying {0}'.format(oldpath))
    print('\tTo {0}'.format(newpath))
    os.system('ln -s {0} {1}'.format(oldpath, newpath))
