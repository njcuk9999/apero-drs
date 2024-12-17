# Constants

Please add any constant as follows


```python
# Plotting mode (0-3)
CDict.add('PLOTTING', value=0, dtype=int,
          source=__NAME__, user=True,
          active=True, group=cgroup, options=[0, 1, 2, 3],
          description='Plotting mode: '
                      '\n\t0: No plots'
                      '\n\t1: Only show plots '
                      '\n\t2: Only save plots to file '
                      '\n\t3: Show and save plots to file')
```


Arguments you can add are as follows:

```yaml
name: str, name of the constant
value: object, value of the constant, set to None for no value
dtype: type, data type of the constant
dtypei: type, data type of list/dictionary elements
options: list of objects, the allowed values for the constant
maximum: the maximum value allowed for the constant
minimum: the minimum value allowed for the constant
source: str, the source file of the constant
unit: astropy unit, the units of the constant
default: default value of the constant
datatype: str, an additional datatype i.e. used to pass to
                 another function e.g. a time having data type "MJD"
dataformat: str, an additional data format i.e. used to pass to
                   another function e.g. a time having data format float
group: str, the group this constant belongs to
user: bool, whether the constant is a user constant
active: bool, whether the constant is active in constant files
               (for user config file generation)
description: str, the description for this constant
author: str, the author of this constant (i.e. who to contact)
parent: str, the parent of this constant (if a constant is
               related to or comes from another constant)
output: bool if False does not put in parameter output table
not_none: bool, if True the constant is required and prompts
                 may ask for this value if set to None
```

## Adding a new constant groups

You'll see in the yaml file that constants are separated into groups.

To do this you can add a "section" as follows:

```python

cgroup = 'SCARVS.GLOBAL'
CDict.add_group(cgroup, description='global settings (generally '
                                    'don\'t touch these)')

```

Then in the constant make sure the group is set to "cgroup"


The following code is an example:


```python 
# =============================================================================
# path settings (generally don't touch these)
# =============================================================================
cgroup = 'SCARVS.PATHS'
CDict.add_group(cgroup, description='Definition of inputs related to the data')

# Define data path
CDict.add('DATA_PATH', value=None, dtype=str,
          source=__NAME__, user=True,
          active=True, group=cgroup, not_none=True,
          description='The data directory (required)')

# Define plot path
CDict.add('PLOT_PATH', value=None, dtype=str,
          source=__NAME__, user=True,
          active=True, group=cgroup, not_none=True,
          description='Plot path (required)')
```

that produces the following section in the yaml file

```yaml

# =============================================================================
# Definition of inputs related to the data
# =============================================================================
# The data directory (required)
DATA_PATH: /scratch2/other/prv/data
# Plot path (required)
PLOT_PATH: /scratch2/other/prv/plots
```