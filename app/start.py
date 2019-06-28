"""Stuff to run on app startup."""

import pandas as pd
from os import path


def find_closest(bacteroidetes, firmicutes, samples, n=5):
    """Find the id of the members closest to the input.

    Parameters
    ==========
    bacteroidetes : float in [0, 1]
        The fraction of bacteroides.
    firmicutes : float in [0, 1]
        The fraction of firmicutes.
    samples : pandas.DataFrame
        The sample data frame. Must contain column `Bacteroidetes` and
        `Firmicutes` that contain the percentage of those phyla.

    Returns
    =======
    list of str
        The id of the n closest individuals.

    """
    return None


def describe(samples, metadata):
    """Give representative information for set of samples.

    Parameters
    ==========
    samples : pandas.Series
        The samples to describe.
    metadata : pandas.DataFrame
        The DataFrame containing additional information for all samples.

    Returns
    =======
    dict
        A dictionary containing different characteristics of the samples.
        For instance:
        - "dogs": How many of the individuals have a dog?
        - "ibd": How many of the individuals have IBD?

    """
    return None


# We start by reading our genus level data
genera = pd.read_csv(
    path.join("..", "data", "american_gut_genus.csv"), dtype={"id": str}
)

# Here we calculate the "library size", the total sum of counts/reads for
# each sample
libsize = genera.groupby("id")["count"].sum()

# This is just the metadata
meta = pd.read_csv(
    path.join("..", "data", "metadata.tsv"),
    dtype={"id": str},
    sep="\t",
    index_col=0,
)

# Now we want to summarize the data on the phylum level and convert counts
# to percentages. We start by summarizing on the phylum level
phyla = genera.groupby(["id", "Phylum"])["count"].sum().reset_index()

# Now we convert the counts to fractions by dividing by the library size
phyla["relative"] = phyla["count"].values / libsize[phyla.id].values

# We will only keep the fractions for the two phyla we're interested in
phyla = pd.pivot_table(
    phyla, index="id", columns="Phylum", values="relative", fill_value=0
)[["Bacteroidetes", "Firmicutes"]]

# As a last step we will load the PCoA coordinates generated in
# `beta_diversity.py`, select 1000 random individuals and merge the
# coordinates with the phyla abundances
red = pd.read_csv("pcoa.csv", index_col=0)

samples = red.sample(1000)
samples = pd.merge(samples, phyla, left_index=True, right_index=True)

# The App will now use the samples DataFrame
