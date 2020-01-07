.. _python_installation:


************************************************************************************
Recommended python installation
************************************************************************************

If you already use anaconda/conda skip to step 3

1. Download anaconda, i.e. in bash and wget (or go to the
   `anaconda website <https://www.anaconda.com/distribution/#download-section>`)

    ```bash
    wget https://repo.anaconda.com/archive/Anaconda3-2019.10-Linux-x86_64.sh
    ```

2. Install anaconda, i.e. with bash

    ```bash
    bash Anaconda3-2019.10-Linux-x86_64.sh
    ```

3. Add `conda-forge` to list of anaconda repositories:
    ```bash
    conda config --add channels conda-forge
    conda config --set channel_priority strict
    ```

4. Create a new conda environment with python3.7
    ```bash
    conda create -n aperoenv python=3.7
    ```

5. Activate conda environment (you will have to do this each time to use apero)
   so putting it in the generated setup script (for convinence) or in
   `~/.bashrc` `~/.tcshrc` to always use, is recommended.
   i. e. to activate in bash:
   ```bash
   conda activate aperoenv
   ```

6. Install python packages not in anaconda:
    ```
    conda install astroquery
    conda install numba
    conda install yagmail
    ```