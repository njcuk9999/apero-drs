# Config file directory


This file contains the following REQUIRED files:
- ```config.py``` 
- ```constants_SPIROU_H2RG.py```
- ```constants_SPIROU_H4RG.py```

It also contains two directories showing example custom config directories
(change ```DRS_UCONFIG``` to a path and copy these to it). The contain either
 ```config.py``` or ```constants_SPIROU_{X}.py``` and any variables in them
 (while DRS_UCONFIG is set and ```USER_CONFIG = 1```) will overwrite the values
 in this folder (i.e. ```.../config/config.py``` and 
 ```.../config/constants_SPIROU_{X}.py```)
 
 
 
 All other DRS data files should be located in: ```.../SpirouDRS/data/``` 