"""Module containing helper functions for the analyses."""


def filled_bar(df, rank="Phylum", figsize=(16, 6), drop=0.01):
    """Plot a filled bar chart for the taxa composition of each individual.

    Parameters
    ----------
    df : pandas.DataFrame
        A pandas DataFrame containing the taxa abundances. Must have columns
        `id`, `count` and whatever is passed as `rank`.
    rank : str
        Name of the taxonomy rank used for summarization.
    figsize : tuple
        The figure size as (width, height).
    drop : float
        Drop taxa with less than this relative abundance. Defaults to 0.01
        meaning drop taxa less abundant than 1%.

    Returns
    -------
    plot : maplotlib.Axes
        The filled barplot ordered by the most abundant taxon.

    """
    summarized = df.groupby(["id", rank])["count"].sum().reset_index()
    summarized["percent"] = summarized.groupby("id")["count"].apply(
        lambda x: x / x.sum())
    summarized = summarized.pivot(index="id", columns=rank, values="percent")
    rank_means = summarized.mean()
    rank_order = (rank_means[rank_means > drop].
                  sort_values(ascending=False).index)
    id_order = summarized[rank_order[0]].sort_values(ascending=False).index
    summarized = summarized.reindex(id_order).reindex(rank_order, axis=1)
    summarized.index = range(summarized.shape[0])

    ax = summarized.plot(kind="area", stacked=True, legend=False,
                         figsize=figsize)
    ax.set_ylim(0, 1)
    ax.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
    return ax
