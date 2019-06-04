"""Stuff to run on app startup."""

import logging
import pickle
import pandas as pd

logging.basicConfig(format="%(asctime)s - %(levelname)s: %(message)s")
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def find_closest(bacteroides, firmicutes, n=1):
    """Find the id of the members closest to the input.

    Parameters
    ==========
    bacteroides : float in [0, 1]
        The fraction of bacteroides.
    firmicutes : float in [0, 1]
        The fraction of firmicutes.

    Returns
    =======
    list of str
        The id of the n closest individuals.

    """
    pass


genera = pd.read_csv("../data/american_gut_genus.csv", dtype={"id": str})
libsize = genera.groupby("id")["count"].sum()
meta = pd.read_csv("../data/metadata.tsv", dtype={"id": str}, sep="\t")

phyla = genera.groupby(["id", "Phylum"])["count"].sum().reset_index()
phyla["relative"] = phyla["count"].values / libsize[phyla.id].values
phyla = pd.pivot_table(phyla, index="id", columns="Phylum", values="relative",
                       fill_value=0)[["Bacteroidetes", "Firmicutes"]]
with open("pcoa.pickle", "rb") as pfile:
    red = pickle.load(pfile)

samples = red.samples.sample(1000)
samples = pd.merge(samples, phyla, left_index=True, right_index=True)
