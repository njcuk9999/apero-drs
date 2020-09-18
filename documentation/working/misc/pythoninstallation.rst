.. _python-installation:

************************************************************************************
Python installation
************************************************************************************

You can install the modules required to run APERO in three ways (eventually
there will be a `setup.py` but not yet!

Currently supported options are:

- :ref:`install miniconda with the supplied environment <python_install_miniconda_env>` (recommended)
- :ref:`install miniconda and manually installing packages <python_install_miniconda_manual>`
- :ref:`install anaconda with the supplied environment <python_install_anaconda_env>`
- :ref:`install anaconda and manually installing packages <python_install_anaconda_manual>`
- :ref:`install via pip only <python_install_pip>`


Once python and the required modules are correctly installed you can
install APERO - see :ref:`here <installation>`.


.. _python_install_miniconda_env:

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


3. Find the APERO conda environment for you (you can either use the yml or the
   txt file) - note these files are system depenedent - do not install on
   non-supported systems

    .. code-block:: bash

        cd apero-drs/setup/env/
        conda env create --file apero-env-{EXT}.yml

    or

    .. code-block:: bash

        cd apero-drs/setup/env/
        conda create --name apero-env --file apero-env-{EXT}.txt
        bash apero-pip-{EXT}.txt


    where {EXT} should be the latest version for your system / setup.

You should now have an environment called `apero-env`.

Before running or installing APERO you must be in this conda environment, i.e. type:

    .. code-block:: bash

        conda activate apero-env


.. only:: html

  :ref:`Back to top <python-installation>`

.. _python_install_miniconda_manual:

====================================================================================
Using miniconda (conda/pip install packages)
====================================================================================

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

3. Create a new conda environment

    .. code-block:: bash

        conda create --name apero-env python=3.7


4. Install the packages available via conda. You will need to check the
   currently supported packages in the `apero-drs/requirements_current.txt` file
   or for developers `apero-drs/requirements_developer.txt` file.

    .. code-block:: bash

        conda install astropy=4.0
        conda install numpy=1.18.1

    .. note:: Some packages must be installed via pip

    .. code-block::

        pip install astroquery=0.3.10
        pip install barycorrpy=0.3.1

.. note::
    If experiencing trouble with barycorrpy with the error:
    `Cannot remove entries from nonexistent` run the following:

    .. code-block:: bash

        pip install barycorrpy --ignore-installed

You should now have an environment called `apero-env`.

Before running or installing APERO you must be in this conda environment, i.e. type:

    .. code-block:: bash

        conda activate apero-env

.. only:: html

  :ref:`Back to top <python-installation>`

.. _python_install_anaconda_env:

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


3. Find the APERO conda environment for you (you can either use the yml or the
   txt file) - note these files are system depenedent - do not install on
   non-supported systems

    .. code-block:: bash

        cd apero-drs/setup/env/
        conda env create --file apero-env-{EXT}.yml

    or

    .. code-block:: bash

        cd apero-drs/setup/env/
        conda create --name apero-env --file apero-env-{EXT}.txt
        bash apero-pip-{EXT}.txt


    where {EXT} should be the latest version for your system / setup.

You should now have an environment called `apero-env`.

Before running or installing APERO you must be in this conda environment, i.e. type:

    .. code-block:: bash

        conda activate apero-env

.. only:: html

  :ref:`Back to top <python-installation>`

.. _python_install_anaconda_manual:

====================================================================================
Using anaconda (conda/pip install packages)
====================================================================================

If you already use anaconda (with python 3) skip to step 3

.. note:: Make sure the anaconda you download/have is anaconda3

1. Download anaconda, i.e. in bash and wget (or go to the
   anaconda website https:/repo.anaconda.com/archive/)

   i.e. the current latest version of Anaconda3 for Linux is this:

    .. code-block:: bash

        wget https://repo.anaconda.com/archive/Anaconda3-2020.07-Linux-x86_64.sh


2. Install anaconda, i.e. with bash

    .. code-block:: bash

        bash Anaconda3-2020.07-Linux-x86_64.sh


3. Create a new conda environment

    .. code-block:: bash

        conda create --name apero-env python=3.7


4. Install the packages available via conda. You will need to check the
   currently supported packages in the `apero-drs/requirements_current.txt` file
   or for developers `apero-drs/requirements_developer.txt` file.

    .. code-block:: bash

        conda install astropy=4.0
        conda install numpy=1.18.1

    .. note:: Some packages must be installed via pip

    .. code-block::

        pip install astroquery=0.3.10
        pip install barycorrpy=0.3.1


.. note::
    If experiencing trouble with barycorrpy with the error:
    `Cannot remove entries from nonexistent` run the following:

    .. code-block:: bash

        pip install barycorrpy --ignore-installed


You should now have an environment called `apero-env`.

Before running or installing APERO you must be in this conda environment, i.e. type:

    .. code-block:: bash

        conda activate apero-env

.. only:: html

  :ref:`Back to top <python-installation>`

.. _python_install_pip:

====================================================================================
Manually using pip
====================================================================================

1. install python 3.7 (install, via virtual environment etc)

2. pip install all modules. You will need to check the
   currently supported packages in the `apero-drs/requirements_current.txt` file
   or for developers `apero-drs/requirements_developer.txt` file.

    .. code-block::

        pip install astroquery=0.3.10
        pip install barycorrpy=0.3.1

.. note::
    If experiencing trouble with barycorrpy with the error:
    `Cannot remove entries from nonexistent` run the following:

    .. code-block:: bash

        pip install barycorrpy --ignore-installed

.. only:: html

  :ref:`Back to top <python-installation>`