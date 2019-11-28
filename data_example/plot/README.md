# Log folder

Plot will be put in here in folders named as follows:

```{NIGHT_NAME}/pid-{PID}_{recipe_name}_{iteration}```

where:
 - `NIGHT_NAME` is the directory name
- `PID` is the drs process ID number
- `recipe_name` is the script that generated the plot 
- `iteration` is the iteration number (if multiple files were given and not combined)

Each folder contains the following:

- pdf plots: `plot_{PLOT_NAME}_pid-{PID}{suffix}.pdf`
- png plots: `plot_{PLOT_NAME}_pid-{PID}{suffix}.png`
- summary pdf: `summary-pid-{PID}_{recipe_name}.pdf`
- summary latex: `summary-pid-{PID}_{recipe_name}.tex`
- summary html: `summary-pid-{PID}_{recipe_name}.html`

where:

- `PLOT_NAME` is the plot name
- `suffix` is the suffix if given to distinguish different version of a specific plot (else this is left blank)
- `PID` is the drs process ID number
- `recipe_name` is the script that generated the plot 

This path can be changed in  ```{DRS_UCONFIG}/{INSTRUMENT}/user_config.ini```