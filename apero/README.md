# The APERO module

## Use:

```python
import apero
```

## import rules

apero.base				- no apero modules
apero.lang 				- only from apero.lang, apero.base
apero.core.constants   	- only from core.constants, apero.lang, apero.base
apero.core.math 		- only from core.math, core.constants, apero.lang, apero.base
apero.core.core   		- only from core.core, core.math, core.constants, apero.lang, apero.base
apero.core.utils  		- only from apero.core.utils, core.core, core.math, core.constants, apero.lang, apero.base

apero.io - only from core.core

apero.plotting - from all
apero.recipes - from all
apero.science - from all
apero.tools - from all


## Contains:

- core

    Core scripts for controlling APERO

- data

    Data products used directly by APERO but not to be changed/modified 
    by the user

- io

    Input/Ouput scripts (reading, writing, path, text, locking etc)

- locale

    Language database scripts (controlling all text, errors, warnings etc)
    
- plotting

    Scripts dealing with plotting
    
- recipes

    User front end scripts the 'recipes' (sorted by instrument)
    
- science

    Scripts dealing with the science of running the recipes
    
- tools

    Useful user and developer tools