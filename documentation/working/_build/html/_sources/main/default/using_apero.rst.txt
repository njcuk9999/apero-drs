.. _using_apero_default:

************************************************************************************
Using APERO
************************************************************************************

The user scripts to reduce data are referred to as 'recipes'.

From a coding point of view this due to the fact that they literally list
the steps (where each step is a function or set of functions).

By design recipes are kept to a bare minimum of code and all heavy functionality
is done in the functions that are called in the recipes.

Currently supported instruments are:

    - SPIRou (See the section on recipes :ref:`here <recipes_spirou>`)


There are two ways to use APERO:

    1. Using recipes individually
    2. Using the processing script to automatically generate batches of recipe
       runs (based on provided run files)

    both of these require installation (see :ref:`here <installation>`)
    and activating a profile (see the next section :ref:`here <activating_apero_profile>`)


.. _activating_apero_profile:

====================================================================================
Activating the APERO profile
====================================================================================

To activate an apero profile you need to source the `{DRS_UCONGIG}/{PROFILE}.{SYSTEM}`.setup script.

Details of this should be in green at the end of the installation process

i.e. for bash:

    .. code-block:: bash

        source {DRS_UCONFIG}/{PROFILE}.bash.setup

i.e. for tcsh/csh/sh

    .. code-block:: csh

        source {DRS_UCONFIG}/{PROFILE}.sh.setup


e.g. with bash and our example profile above:

    .. code-block::

        source {DRS_UCONFIG}/{PROFILE}.sh.setup


We strongly recommend setting up a alias for this

i.e. for bash (i.e. in :file:`~/.bashrc` :file:`~/.profile` or :file:`~/.bash_aliases`):

    .. code-block:: bash

        alias {PROFILE}="source {DRS_UCONFIG}/{PROFILE}.bash.setup"

i.e. for tcsh/csh/sh  (i.e. in :file:`~/.tcshrc`, :file:`~/.cshrc` etc)

    .. code-block:: csh

        alias {PROFILE} "source {DRS_UCONFIG}/{PROFILE}.sh.setup"


.. note:: This must be done every time one wishes to use APERO (and must be
          done after one activates the conda environment

          `conda activate apero-env`

          One could add these both to automatically happen in a :file:`~/.bashrc` but
          we recommend activating each time.


Following on from typing this command you should see a splash screen validating the
installation and letting you know everything is good to run APERO recipes and tools.

.. image:: ../../_static/images/apero_splash.png

.. only:: html

  :ref:`Back to top <using_apero_default>`

.. _running_recipes_indvidiually:

===========================================
Running recipes indvidiually
===========================================

One can simply run a recipe by using python or the command line.
For details on individual recipes please check the recipe definitions for
a specific instrument (e.g. for SPIROU click :ref:`here <recipes_spirou>`).

.. only:: html

  :ref:`Back to top <using_apero_default>`

.. _using_apero_processing:

===========================================
Using the processing script
===========================================

The processing script is the recommended way to run the reduction.

Details of how to use the processing script can be found :ref:`here <user_tools_default_proc>`.


.. only:: html

  :ref:`Back to top <using_apero_default>`
   