# conda environments


Note in general these are for an exact copy of the tested environment,
therefore the following steps will only work for a linux-64 bit machine.
For other operating systems please refer to the requirements.txt


# Use

Install miniconda (recommended) or anaconda

## Method 1

Use the `yaml` file to create an environment

```
conda env create --file apero-env-{DATE}.yml
```

## Method 2

Use the `txt` files:

1. the apero-env text file:
```
conda create --name apero-env --file apero-env-{DATE}.txt
```

2. the apero-pip file:
```
bash apero-pip-{DATE}.txt
```

# Create

## Method 1

Create the `yaml` file

```
conda env export > apero-env-{DATE}.yml
```

## Method 2

Create the conda install package list

```
conda list --explicit > apero-env-{DATE}.txt
```

Have to manually add the pip installs (to `apero-pip-{DATE}.txt`)

i.e.
```
pip install PACKAGE==VERSION
```