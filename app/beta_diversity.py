"""Calculate beta diversity and ordination."""

import logging
import pickle
from os import path
import pandas as pd
from skbio.diversity import beta_diversity
from skbio.stats.ordination import pcoa
from skbio.stats import subsample_counts

logging.basicConfig(format="%(asctime)s - %(levelname)s: %(message)s")
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def rarefy_counts(counts, depth=10000):
    """Normalize a count matrix by rarefaction (subsampling).

    Parameters
    ----------
    counts : pandas.DataFrame
        The count matrix to be normalized. Contains variables as columns and
        samples as rows.

    Returns
    -------
    pandas.DataFrame
        A new data frame with normalized samples such that each sample has
        a depth of `depth` (sum of variables equals depth).

    """
    log.info(
        "Subsampling %dx%d count matrix to a depth of %d."
        % (counts.shape[0], counts.shape[1], depth)
    )
    bad = counts.astype("int").sum(1) < depth
    log.info("Removing %d samples due to low depth." % bad.sum())
    rare = counts[~bad].apply(
        lambda x: pd.Series(
            subsample_counts(x.astype("int"), depth), index=counts.columns
        ),
        axis=1,
    )
    return rare


log.info("Reading genus-level data.")
genera = pd.read_csv(
    path.join("..", "data", "american_gut_genus.csv"), dtype={"id": str}
)
libsize = genera.groupby("id")["count"].sum()

mat = pd.pivot_table(
    genera,
    columns="Genus",
    index="id",
    values="count",
    fill_value=0,
    aggfunc="sum",
)
mat = rarefy_counts(mat, 1000)

log.info("Calculating beta diversity and PCoA.")
D = beta_diversity("braycurtis", mat.values, mat.index, validate=True)
red = pcoa(D, number_of_dimensions=2)

log.info("Saving results to `pcoa.csv`.")
red.samples.to_csv("pcoa.csv")
