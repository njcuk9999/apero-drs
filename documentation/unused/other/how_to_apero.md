

# How to terrapipe




## Adding a constant:




## Adding a keyword argument:




## Adding a new recipe:




## Adding a new filetype:




## Adding a plot:


##### 1. in plot_functions.py define a plotting function:

```text
def my_plot_function(plotter, graph, kwargs):
    # ------------------------------------------------------------------
    # start the plotting process
    if not plotter.plotstart(graph):
        return
    # get plt
    plt = plotter.plt
    # ------------------------------------------------------------------
    # get the arguments from kwargs
    x = kwargs['x']
    y = kwargs['y']
    color = kwargs['color']
    # ------------------------------------------------------------------
    # set up plot
    fig, frame = graph.set_figure(plotter)
    frame.plot(x, y, color=color)
    # ------------------------------------------------------------------
    # wrap up using plotter
    plotter.plotend(graph)
```

##### 2. In plot_functions.py define a Graph instance:
```text
my_plot = Graph(name, kind, func)
```
```text
my_debug_plot = Graph('MY_DEBUG_PLOT', kind='debug', func=my_plot_function)
my_summary_plot = Graph('MY_SUM_PLOT', kind='summary', func=my_plot_function)
```

where my_plot_function links to the function defined in (1)
where name is the NAME that will be used to link to other places in the code
where kind is either 'debug' (for the in line plots) or 'summary' (for adding to the summary document)

##### 3. In plot_functions.py add Graph instance to definitions list
```text
definitions += [my_plot, my_debug_plot, my_summary_plot]
```

##### 4. In recipe_definitions.py add NAME to set_debug_plots or set_summary_plots
```text
my_recipe.set_debug_plots(NAME)
```
```text
my_recipe.set_debug_plots('MY_DEBUG_PLOT')
my_recipe.set_summary_plots('MY_SUMMARY_PLOT')
```
##### 5. If kind='debug' then we need to allow user to turn it on/off. 

This is done in `terrapipe/core/instruments/{instrument}/default_constants.py` (and `terrapipe/core/instruments/default/default_constants.py`) by adding a constant `PLOT_{NAME}`

In `terrapipe/core/instruments/{instrument}/default_constants.py` (where `instrument` is the instrument name)
```text
PLOT_{NAME} = PLOT_{NAME}.copy(__NAME__)
PLOT_{NAME}.value = True
```
In `terrapipe/core/instruments/default/default_constants.py`
```text
PLOT_NAME = Const('PLOT_{NAME}', value=False, dtype=bool, source=__NAME__)
```
where NAME is the NAME from (2)

i.e. in `terrapipe/core/instruments/{instrument}/default_constants.py`   
```text
PLOT_MY_DEBUG_PLOT = PLOT_MY_DEBUG_PLOT.copy(__NAME__)
PLOT_MY_DEBUG_PLOT.value = True
```
in `terrapipe/core/instruments/default/default_constants.py`
```text 
        PLOT_MY_DEBUG_PLOT = Const('PLOT_MY_DEBUG_PLOT', value=False, dtype=bool, source=__NAME__)
```
Remembering to add to `__ALL__` at the top

Note: currently the .value is set to True this should be set to False to all the user to turn it on or off

See how to add a constant for more details on this step.

##### 6. In code where you want to plot use plotter.graph:     
```text
recipe.plotter.graph(name, kwargs)
```
where name = "my_plot_functions" and the kwargs match what is needed in the function
```text
recipe.plotter.graph('my_plot_function', x=[1,2,3,4], y=[5,6,7,8], color='red')
```



##### Summary plot

Add graph as in section (6). Note that debug and summary plots must be plotted seperately and definied separately even if using the same function. This means they have a different `NAME`. 

Add stats (if required) as follows:
```text
        recipe.plotter.add_stat(key, value)
```
where key can be a string or a parameter in `params` (i.e. a keyword from `defaults_keywords.py`)
i.e.:
```text
        recipe.plotter.add_stat('KW_VERSION', value=params['DRS_VERSION'])
```

The summary plot is then built as follows (usually at the end of a `__main__` code). It can take the `qc_params` (from quality control) as an argument or take no argument (for example if there are no quality control criteria). i.e.:
```text
        recipe.plotter.summary_document()
```
or 
```text
        recipe.plotter.summary_document(qc_params)
```
