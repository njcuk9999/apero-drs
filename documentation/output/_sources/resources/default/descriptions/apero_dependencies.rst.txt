The apero_dependencies recipe takes no arguments.

It scans through all valid python scripts within the apero module and prints
stats on:

- the number of lines
- the number of empty lines (no text)
- the number of comments
- the number of code lines (not comments)

We aim to have at least as many comments as lines of code, the text will
display in yellow for any script that this is not true for.

At the end the total number of these stats is printed.

i.e. for 2022-01-24

.. code-block::

    00:48:19.152-  |DEPEND| 	total lines: 156638
    00:48:19.171-  |DEPEND| 	total empty lines: 11270
    00:48:19.192-  |DEPEND| 	total lines of comments: 67476
    00:48:19.220-  |DEPEND| 	total lines of code: 77892

Below this the modules that are used (and the current system versions) is
printed - standard modules have no version but this can be used as a
quick check of which modules should be in the requirements files.

i.e. for 2022-01-24

.. code-block::

    traceback       (No version info)
    IPython         (8.0.1)
    ipdb            (No version info)
    pdb             (No version info)
    ctypes          (1.1.0)
    mpl_toolkits    (No version info)
    tqdm            (4.62.3)
    barycorrpy      (0.4.4)
    matplotlib      (3.5.1)
    struct          (No version info)
    astropy         (5.0)
    sqlalchemy      (1.4.28)
    yagmail         (0.14.260)
    multiprocessing (No version info)
    numba           (0.54.1)
    tkinter         (No version info)
    Tkinter         (NOT INSTALLED)
    bottleneck      (1.3.2)
    mysql           (No version info)
    string          (No version info)
    tkFileDialog    (NOT INSTALLED)
    tkFileFialog    (NOT INSTALLED)
    tkFont          (NOT INSTALLED)
    ttk             (NOT INSTALLED)
    PIL             (9.0.0)
    astroquery      (0.4.4)
    collections     (No version info)
    contextlib      (No version info)
    copy            (No version info)
    datetime        (No version info)
    hashlib         (No version info)
    pandasql        (No version info)
    pandastable     (0.12.2)
    pathlib         (No version info)
    scipy           (1.7.3)
    setuptools      (58.0.4)
    signal          (No version info)
    skimage         (0.19.1)
    time            (No version info)
    ttkthemes       (No version info)
    typing          (No version info)
    argparse        (1.1)
    getpass         (No version info)
    glob            (No version info)
    gspread_pandas  (3.0.4)
    importlib       (No version info)
    itertools       (No version info)
    numpy           (1.20.3)
    os              (No version info)
    pandas          (1.3.5)
    pkg_resources   (No version info)
    random          (No version info)
    re              (2.2.1)
    requests        (2.27.1)
    shutil          (No version info)
    socket          (No version info)
    sqlite3         (No version info)
    sys             (No version info)
    textwrap        (No version info)
    threading       (No version info)
    warnings        (No version info)
    yaml            (6.0)
