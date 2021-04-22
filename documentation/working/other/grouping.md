# File groups

For APERO processing files must be grouped to be able to run
individual "runs" of recipes.
This is set at the recipe level (`recipe_definitions.py`)
 ```
recipe.group_func = grouping.function
recipe.group_column = 'SOME REFERENCE TO A COLUMN'
```
Note the group_column must either be a column in the `index` database
or a reference to a variable in `params` (`ParamDict`) that is itself
a string name of a column in the `index` database.

---

## 1. No group


- recipe must have no file arguments
- 1 run is returns with other argument values filled

i.e.

	group1 = arg1

---

## 2. Group individually

- recipe must have 1 file argument only
- no `group_column` is required

i.e.

	arg1 = ['TYPE1', 'TYPE2', 'TYPE3']

- each argument is then added to a separate group

i.e.

	group1 = arg1[0]
	group2 = arg1[1]
	group3 = arg1[2]

---

# 3. Group by dirname


- each file argument has a set of drs file types associated with it
- `group_column` is required (this is usually a directory reference i.e. 
  `REPROCESS_OBSDIR_COL`)

i.e.  
	arg1 = ['TYPE1', 'TYPE2']
	arg2 = ['TYPE3']

- we get all combinations of argument drs file types

i.e.:

	combination 1:   [arg1='TYPE1', arg2='TYPE3']
	combination 2:   [arg1='TYPE2', arg2='TYPE3']

where the length is always the number of file arguments

We then loop around each directory and get all drs files that match a combination

i.e. 

	group1 = directory1 + combination1
	group2 = directory1 + combination2
	group3 = directory2 + combination1
	group4 = directory2 + combination2
	group5 = directory3 + combination1
	group6 = directory3 + combination2

---

## 4. Group by polar sequence


- recipe must have only one file argument

- drs file types must have header keys CMPLTEXP and NEXP

- we then loop through all files

- if directory changes: start NEW GROUP
- if CMPLTEXP in group - add to group + remove other CMPLTEXP from this group
- if CMPLTEXP < NEXP: add to group
- if CMPLTEXT = NEXP: add to group + start NEW GROUP if NGROUP=NEXP
- else start NEW GROUP

i.e.
	c=CMPLTEXP  and n = NEXP

	group1 = directory1 + set[0][c=1/n=4, c=2/n=4, c=3/n=4, c=4/n=4]
	group2 = directory1 + set[1][c=1/n=4, c=2/n=4, c=3/n=4, c=4/n=4]
	group3 = directory1 + set[2][c=1/n=4, c=2/n=4, c=3/n=4, c=4/n=4]
	group4 = directory2 + set[0][c=1/n=4, c=2/n=4, c=3/n=4, c=4/n=4]
	group5 = directory3 + set[1][c=1/n=4, c=2/n=4, c=3/n=4, c=4/n=4]
	group6 = directory4 + set[2][c=1/n=4, c=2/n=4, c=3/n=4, c=4/n=4]