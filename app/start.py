"""Stuff to run on app startup."""

import pickle
import numpy as np
import pandas as pd
from os import path
import plotly.figure_factory as ff
import plotly.graph_objs as go

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
    distance = list()
    for index, row in samples.iterrows():
        distance.append(
            np.sqrt(
                (np.square(row["Bacteroidetes"] - bacteroidetes))
                + (np.square(row["Firmicutes"] - firmicutes))
            )
        )
    samples["Distance"] = distance
    samples = samples.sort_values(by="Distance")
    id = samples.index
    sorted_id = id.tolist()
    top_5 = sorted_id[0:5]

    return top_5


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
    import pandas as pd

    sample_metadata = pd.DataFrame()
    metadata.index = metadata["sample_name"]
    sample_metadata = metadata.loc[samples.index]
    samples_with_dog = sample_metadata[sample_metadata.dog == "true"].shape[0]
    samples_with_cat = sample_metadata[sample_metadata.cat == "true"].shape[0]
    samples_with_ibd = sample_metadata[
        sample_metadata.ibd
        == "Diagnosed by a medical professional (doctor, physician assistant)"
    ].shape[0]
    samples_with_diabetes = sample_metadata[
        sample_metadata.diabetes
        == "Diagnosed by a medical professional (doctor, physician assistant)"
    ].shape[0]
    samples_with_cardio = sample_metadata[
        sample_metadata.cardiovascular_disease
        == "Diagnosed by a medical professional (doctor, physician assistant)"
    ].shape[0]
    samples_with_cancer = sample_metadata[
        sample_metadata.cancer
        == "Diagnosed by a medical professional (doctor, physician assistant)"
    ].shape[0]
    samples_female = sample_metadata[
        sample_metadata.sex
        == "female"
    ].shape[0]
    samples_consume_alcohol = sample_metadata[
        sample_metadata.alcohol_consumption
        == "true"
    ].shape[0]
    samples_with_college = sample_metadata[
        sample_metadata.level_of_education == "Bachelor's degree"
    ].shape[0]
    samples_who_smoke = sample_metadata[
        (sample_metadata.smoking_frequency == "Rarely (a few times/month)")
        & (sample_metadata.smoking_frequency == "Daily")
        & (sample_metadata.smoking_frequency == "Occasionally (1-2 times/week)")
        & (sample_metadata.smoking_frequency == "Regularly (3-5 times/week)")
    ].shape[0]
    sample_metadata.fillna(0)
    sample_metadata.birth_year = sample_metadata.birth_year.replace(
        {"Not applicable": 0}
    )
    sample_metadata.birth_year = sample_metadata.birth_year.replace(
        {"Not provided": 0}
    )
    samples_older_70 = sample_metadata[
        (sample_metadata.birth_year.astype(float) < 1949)
        & (sample_metadata.birth_year.astype(float) > 1919)
    ].shape[0]
    sample_metadata.birth_year = sample_metadata.birth_year.replace(
        {0: np.NaN}
    )
    sample_metadata.birth_year = sample_metadata.birth_year.astype(float)
    age_average = 2019 - sample_metadata.birth_year.mean()
    sample_metadata.bmi = sample_metadata.bmi.replace(
        {"Not applicable": np.NaN}
    )
    sample_metadata.bmi = sample_metadata.bmi.replace({"Not provided": np.NaN})
    sample_metadata.bmi = sample_metadata.bmi.replace({0: np.NaN})
    sample_metadata.bmi = sample_metadata.bmi.astype(float)
    sample_metadata.bmi.loc[(sample_metadata["bmi"] > 40)] = np.NaN
    sample_metadata.bmi.loc[(sample_metadata["bmi"] < 13)] = np.NaN
    bmi_average = sample_metadata.bmi.mean()

    sample_metadata.height_cm = sample_metadata.height_cm.replace(
        {"Not applicable": np.NaN}
    )
    sample_metadata.height_cm = sample_metadata.height_cm.replace(
        {"Not provided": np.NaN}
    )
    sample_metadata.height_cm = sample_metadata.height_cm.replace({0: np.NaN})
    sample_metadata.height_cm = sample_metadata.height_cm.astype(float)
    sample_metadata.height_cm.loc[
        (sample_metadata["height_cm"] > 220)
    ] = np.NaN
    sample_metadata.height_cm.loc[
        (sample_metadata["height_cm"] < 130)
    ] = np.NaN
    height_average = sample_metadata.height_cm.mean()

    dict = [
        samples_with_dog,
        samples_with_ibd,
        samples_with_diabetes,
        samples_with_cancer,
        samples_with_college,
        samples_older_70,
        age_average,
    ]
    return_display = pd.DataFrame(columns=["names", "values", "icon"])
    return_display = return_display.append(
        {"names": "Dogs", "values": samples_with_dog, "icon": "dog"},
        ignore_index=True,
    )
    return_display = return_display.append(
        {"names": "Cats", "values": samples_with_cat, "icon": "cat"},
        ignore_index=True,
    )
    return_display = return_display.append(
        {"names": "Cancer", "values": samples_with_cancer, "icon": "ribbon"},
        ignore_index=True,
    )
    return_display = return_display.append(
        {
            "names": "Diabetes",
            "values": samples_with_diabetes,
            "icon": "circle",
        },
        ignore_index=True,
    )
    return_display = return_display.append(
        {"names": "IBD", "values": samples_with_ibd, "icon": "ambulance"},
        ignore_index=True,
    )
    return_display = return_display.append(
        {
            "names": "College degree",
            "values": samples_with_college,
            "icon": "graduation-cap",
        },
        ignore_index=True,
    )
    return_display = return_display.append(
        {"names": "Average age", "values": age_average, "icon": "child"},
        ignore_index=True,
    )
    return_display = return_display.append(
        {"names": "Average BMI", "values": bmi_average, "icon": "weight"},
        ignore_index=True,
    )
    return_display = return_display.append(
        {
            "names": "Average height (cm)",
            "values": height_average,
            "icon": "ruler-vertical",
        },
        ignore_index = True,
    )
    return_display = return_display.append(
        {
            "names": "Alcohol Consumption",
            "values": samples_consume_alcohol,
            "icon": "beer",
        },
    
        ignore_index=True,
    )
    return_display = return_display.append(
        {
            "names": "Cardiovascular disease",
            "values": samples_with_cardio,
            "icon": "heartbeat",
        },
    
        ignore_index=True,
    )
    return_display = return_display.append(
        {
            "names": "Females",
            "values": samples_female,
            "icon": "female",
        },
    
        ignore_index=True,
    )
    return_display = return_display.append(
        {
            "names": "Smokers",
            "values": samples_who_smoke,
            "icon": "smoking",
        },
    
        ignore_index=True,
    )
    return return_display

def firm_plot(samples, firmicutes, healthiest_sample):
    """
     Returns a graph of the distribution of the data in a graph
     ==========
     samples : pandas.DataFrame
         The sample data frame. Must contain column `Bacteroidetes` and
         `Firmicutes` that contain the percentage of those phyla.
     Returns
     =======
     plotly graph
   """
    hist_data = [samples["Firmicutes"]]
    group_labels = ['Firmicutes']
    firm = ff.create_distplot(hist_data, group_labels, show_hist=False)
    firm['layout'].update(title='Firmicutes Sample Distribution ')
    firm['layout'].update(
        showlegend=False,
        annotations= [
            dict(
                x=firmicutes,
                y=0,
                xref="x",
                yref="y",
                text="You are here!",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="#0e0f36",
                ax=70,
                ay=-30,
                bordercolor="#06a300",
                borderwidth=2,
                borderpad=4,
                bgcolor="#69f564",
                opacity=0.8
            ), dict(
                x=healthiest_sample['Firmicutes'],
                y=0,
                xref="x",
                yref="y",
                text="Healthiest sample",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="#0e0f36",
                ax=70,
                ay=30,
                bordercolor="#4c0acf",
                borderwidth=2,
                borderpad=4,
                bgcolor="#b977f2",
                opacity=0.8
            )
        ]
        
    )

    return firm

    
def bact_plot(samples, bacteroidetes, healthiest_sample):
    """
     Returns a graph of the distribution of the data in a graph
     ==========
     samples : pandas.DataFrame
         The sample data frame. Must contain column `Bacteroidetes` and
         `Firmicutes` that contain the percentage of those phyla.
     Returns
     =======
     plotly graph
   """
    import plotly.figure_factory as ff 
    hist_data = [samples["Bacteroidetes"]]
    group_labels = ['Bacteroidetes']
    bact = ff.create_distplot(hist_data, group_labels, show_hist=False)
    bact['layout'].update(title='Bacteroidetes Sample Distribution ')

    bact['layout'].update(
        showlegend=False,
        annotations= [
            dict(
                x=bacteroidetes,
                y=0,
                xref="x",
                yref="y",
                text="You are here!",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="#0e0f36",
                ax=70,
                ay=-30,
                bordercolor="#06a300",
                borderwidth=2,
                borderpad=4,
                bgcolor="#69f564",
                opacity=0.8
            ),
            dict(
                x=healthiest_sample['Bacteroidetes'],
                y=0,
                xref="x",
                yref="y",
                text="Healthiest Sample",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="#0e0f36",
                ax=70,
                ay=30,
                bordercolor="#4c0acf",
                borderwidth=2,
                borderpad=4,
                bgcolor="#b977f2",
                opacity=0.8
            )
        ]
        
    )
    return bact
     
def healthiest(samples, metadata):
    """
     Return the average firmicutes and bacteroidites levels for the healthiest individuals in the metadata and standard deviation
     Parameters
     ==========
     samples : pandas.DataFrame
         The sample data frame. Must contain column `Bacteroidetes` and
         `Firmicutes` that contain the percentage of those phyla.
     metadata : pandas.DataFrame
        The DataFrame containing additional information for all samples,
        Uses birth_year, alcohol frequency, alzheimer's, bmi,   cardiovascular_disease, cancer, depression_bipolar_schizophrenia, diabetes,
        ibd, ibs, kidney_disease, liver_disease, lung_disease, mental_illness, skin_condition
     Returns
     =======
     list of two numbers
         The bacteroidites and firmicutes ratios for the compiled healthiest individuals
   """
    sample_metadata = pd.DataFrame()
    metadata.index = metadata["sample_name"]
    sample_metadata = metadata.loc[samples.index]
    metadata_copy = sample_metadata.copy(deep=True)
    metadata_copy = metadata_copy[
        metadata_copy.cancer == "I do not have this condition"
    ]
    metadata_copy = metadata_copy[
        metadata_copy.alzheimers == "I do not have this condition"
    ]
    metadata_copy = metadata_copy[
        metadata_copy.cardiovascular_disease == "I do not have this condition"
    ]
    metadata_copy = metadata_copy[
        metadata_copy.diabetes == "I do not have this condition"
    ]
    metadata_copy = metadata_copy[
        metadata_copy.ibd == "I do not have this condition"
    ]
    metadata_copy = metadata_copy[
        metadata_copy.ibs == "I do not have this condition"
    ]
    metadata_copy = metadata_copy[
        metadata_copy.kidney_disease == "I do not have this condition"
    ]
    metadata_copy = metadata_copy[
        metadata_copy.liver_disease == "I do not have this condition"
    ]
    metadata_copy = metadata_copy[
        metadata_copy.lung_disease == "I do not have this condition"
    ]
    metadata_copy = metadata_copy[metadata_copy.mental_illness == "false"]
    metadata_copy = metadata_copy[
        metadata_copy.skin_condition == "I do not have this condition"
    ]
    metadata_copy.bmi = metadata_copy.bmi.replace({"Not applicable": 0})
    metadata_copy.bmi = metadata_copy.bmi.replace({"Not provided": 0})
    metadata_copy = metadata_copy[metadata_copy.bmi.astype(float) > 18.5]
    metadata_copy = metadata_copy[metadata_copy.bmi.astype(float) < 25.0]
    metadata_copy.birth_year = metadata_copy.birth_year.replace(
        {"Not applicable": 0}
    )
    metadata_copy.birth_year = metadata_copy.birth_year.replace(
        {"Not provided": 0}
    )
    metadata_copy = metadata_copy[
        metadata_copy.birth_year.astype(float) > 1959
    ]
    metadata_copy = metadata_copy[
        metadata_copy.birth_year.astype(float) < 1999
    ]
    id_list = metadata_copy["sample_name"].tolist()
    healthiest_samples = samples.loc[id_list]
    healthiest_sample = healthiest_samples.mean(axis=0)
    return healthiest_sample


# We start by reading our genus level data
genera = pd.read_csv(
    path.join("..", "data", "american_gut_genus.csv"), dtype={"id": str}
)

# Here we calculate the "library size", the total sum of counts/reads for
# each sample
libsize = genera.groupby("id")["count"].sum()

# This is just the metadata
meta = pd.read_csv(
    path.join("..", "data", "metadata.tsv"), dtype={"id": str}, sep="\t"
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
meta = meta[meta.sample_name.isin(samples.index)]
samples = pd.merge(samples, phyla, left_index=True, right_index=True)
healthiest_sample = healthiest(samples, meta)
firm_plot = firm_plot
bact_plot = bact_plot
# The App will now use the samples DataFrame
