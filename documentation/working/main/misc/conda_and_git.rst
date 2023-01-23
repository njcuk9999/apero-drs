.. _conda_git:

*********************************
Useful guide on conda and git
*********************************


conda
===================

Conda is a package manager. We use conda specifically to install a python
environment where all python pacakges are managed and contained to ensure
maximum compatibility. For python conda comes in two main flavours "anaconda"
and "miniconda". Anaconda has many built in packages that are shipped with it,
miniconda only contains standard python packages. We only use and recommend
miniconda throughout APERO.

miniconda installation
========================

Miniconda can be installed as follows:

1. download miniconda from here: https://docs.conda.io/en/latest/miniconda.html
   for your OS. I.e. for linux 64 bit

.. code-block:: bash

    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh


2. Install, following all instructions. The last step asks you to add the
   conda initialization to your profile (e.g. `source ~/.bashrc).
   You should make sure you do this
   (or run `conda init` before any other steps)

.. code-block:: bash

   bash Miniconda3-latest-Linux-x86_64.sh

3. Make sure to source your profile (e.g. `source ~/.bashrc) before using conda


useful conda commands
========================

The main commands you may want to use with conda are:

.. code-block:: bash

    conda deactivate

which stops/unloads (deactivating) the current conda environment, but not all
environments. Run this may times over to get out of all environments before
starting/loading (activating) a new environment. You cannot break anything from
running the deactivation command many times, so use as many times as you like!

.. code-block:: bash

    conda activate {env name}

which starts/loads/activates the environment "env name". You must be in
this environment to use and install python modules.

.. code-block:: bash

    conda create --name {env name} python=3.9.7

which creates a new environment (called "env name") for python version 3.9.7
in this case. Replace the 3.9.7 with your chosen python version (use 3.9 for the
most recent version of 3.9 etc) leaving this out will use the most recent
version of python for your conda (conda update conda may be required to get the
most recent version of python).

.. code-block:: bash

    conda env remove --name {env name}

which deletes the environment called "env name". You cannot do this if you are
inside this environment (so must use the deactivate comment first).

.. code-block:: bash

    conda env list

which shows you which environment you are in and which conda environments exist

.. code-block:: bash

    conda update conda

which updates conda to the most recent version.

git
========================

Git is a version management system.
Github is an online platform using git.
Git is set up in a "tree" system where you have the `main` or `master` branch
which is the default version, and then there are branches coming off the main
branch which contain (in general) newer code and newer versions, that can be
merged into the main branch at some point in the future. Note branches can
also have branches coming off them.

some git commands
=========================

.. code-block:: bash

    git clone {url}
    git clone {url} {directory name}
    git clone {ur} -branch {branch name}

where url is taken from a github repository, directory name is the directory
name on disk to call the top level directory taken from github and
branch name is the name of the branch you wish to start at (by default this is
`master` or `main`.

.. code-block:: bash

    git branch

shows which branches are currently available locally and which branch you are
currently on

.. code-block:: bash

    git checkout {branch name}

moves from your current branch to a new branch (called "branch name"). You can
only do this if there are no uncommited changes.

.. code-block:: bash

    git add {filename}

add a new file to be tracked by git

.. code-block:: bash

    git commit -m "message"

commit changes to the current branch

.. code-block:: bash

    git push

Send changes to github (from the local git repository)

.. code-block:: bash

    git pull

Get changes from github and update the local git repository

.. code-block:: bash

    git stash

Remove all local uncommited changes and reset to the last commited local version
this can be useful to allow pulling from github.
