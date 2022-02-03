.. _python-installation:

************************************************************************************
Python installation
************************************************************************************

You can install the modules required to run APERO in three ways (eventually
there will be a `setup.py` but not yet!

Currently supported options are:

- :ref:`install miniconda <python_install_miniconda>` (recommended)
- :ref:`install anaconda <python_install_anaconda>`
- :ref:`install via pip only (i.e. in a venv) <python_install_pip>`


Once python and the required modules are correctly installed you can
install APERO - see :ref:`here <installation>`.

.. warning:: We do not recommend ever using the base environment or the
             system python for installing modules or running the APERO codes.


.. _python_install_miniconda:

====================================================================================
Installing miniconda (with supplied environment)
====================================================================================

This is recommended for maximum compatibility

If you already use miniconda (with python 3) skip to step 3

.. note:: Make sure the miniconda you download/have is miniconda3

1. Download miniconda3, i.e. in bash and wget (or go to the
   anaconda website https:/repo.anaconda.com/miniconda/)

   i.e. the current latest version of Miniconda3 for Linux is this:

    .. code-block:: bash

        wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh


2. Install miniconda, i.e. with bash

    .. code-block:: bash

        bash Miniconda3-latest-Linux-x86_64.sh


3. Create a conda environment

    .. code-block:: bash

        conda env create --name {YOUR ENV NAME} python=3.9

    where `{YOUR ENV NAME}` should be a suitable name for the apero conda environemnt
    (e.g. `setup_07XXX_mini1` or `full_07111`)

You should now have an environment called `{YOUR ENV NAME}`.

Before running or installing APERO you must be in this conda environment, i.e. type:

    .. code-block:: bash

        conda activate {YOUR ENV NAME}


You can now install APERO (see :ref:`here <installation>`)

.. only:: html

  :ref:`Back to top <python-installation>`


.. _python_install_anaconda:

====================================================================================
Using anaconda (with supplied environment)
====================================================================================

If you already use anaconda (with python 3) skip to step 3

.. note:: Make sure the anaconda you download/have is anaconda3

1. Download anaconda3, i.e. in bash and wget (or go to the
   anaconda website https:/repo.anaconda.com/archive/)

   i.e. the current latest version of Anaconda3 for Linux is this:

    .. code-block:: bash

        wget https://repo.anaconda.com/archive/Anaconda3-2020.07-Linux-x86_64.sh


2. Install anaconda, i.e. with bash

    .. code-block:: bash

        bash Anaconda3-2020.07-Linux-x86_64.sh


3. Create a conda environment

    .. code-block:: bash

        conda env create --name {YOUR ENV NAME} python=3.9

    where `{YOUR ENV NAME}` should be a suitable name for the apero conda environemnt
    (e.g. `setup_07XXX_mini1` or `full_07111`)

You should now have an environment called `{YOUR ENV NAME}`.

Before running or installing APERO you must be in this conda environment, i.e. type:

    .. code-block:: bash

        conda activate {YOUR ENV NAME}


You can now install APERO (see :ref:`here <installation>`)

.. only:: html

  :ref:`Back to top <python-installation>`



.. _python_install_pip:


====================================================================================
Manually using pip
====================================================================================

Setup your python and install the pip module and create a environement as required,
we do not give instructions how to do this here.

We recommend typing `which pip` to verify you are using the correct pip.

You can now install APERO (see :ref:`here <installation>`)

.. warning:: We do not recommend ever using the base environment or the
             system python for installing modules or running the APERO codes.

.. only:: html

  :ref:`Back to top <python-installation>`
