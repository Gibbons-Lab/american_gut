# The American Gut App

This little app will allow you to find similar individuals in the American
Gut dataset based on your proportion of Bacteroidetes and Firmicutes.

<img src="demo.gif" style="max-width: 320px; margin: 1em">

## Installation

The App uses [dash](https://plot.ly/products/dash/). You can install all
dependencies with conda.

```bash
conda install dash dash-daq pandas
```

If you want to run the beta diversity calculation (already provided pre-computed)
you also need `scikit-bio`.

```bash
conda install -c conda-forge scikit-bio
```

## Run the app

To run the app use any terminal and enter the directory of the app. Now run

```bash
python app.py
```

On Windows you can do that with the conda terminal.



