# Documentation


## 1. Compiling

Run the following command to compile and upload (see --help for details) 
```bash
apero_documentation.py --instruments=ALL --filedef --recipedef --recipeseq --compile --upload --mode=html
```


## 2. Structure

- `output/`: this is the compile output html and latex directory - do not edit directly
- `unused/`: this is files that are not currently being used
- `working/`: this is the working directory - edit this files only

### 2.1 working directory

- `_build/`: temporary files used in compiling - do not edit directly
- `_static/`: images, graphics and static files (not normally text editable)
- `_templates/`: the layout for html pages
- `auto/`: files autmoatically created by `apero_documentation` are here - do not edit manually they will be overwritten
- `main/`: the main files to write the documentation (some are edited by `apero_documentation`)
- `resources/`: other files used in either `apero_documentation` or by sphinx to compile the rst files
- `conf.py` - do not touch sphinx settings
- `index.rst` - the first page one sees - everything links from here
- `make.bat` - do not touch used with sphinx
- `Makefile` - do not touch used with sphinx

### 2.2 the working/main directory

This is the main files to write the documentation

- `default/`: pages associated with no instrument
- `developer/`: pages associated with developer mode
- `general/`: the general pages
- `misc/`: other pages
- `{instrument}/`: pages associated with a specific instrument
- `science/`: science algorithm pages