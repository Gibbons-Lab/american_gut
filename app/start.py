"""Stuff to run on app startup."""

import pickle
import numpy as np
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
    distance = list()
    for index,row in samples.iterrows():
        distance.append(np.sqrt((np.square(row['Bacteroidetes']-bacteroidetes))+ (np.square(row['Firmicutes']-firmicutes))))
    samples['Distance'] = distance
    samples = samples.sort_values(by = 'Distance')
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
    sample_metadata = pd.DataFrame()
    metadata.index = metadata["sample_name"]  
    sample_metadata = metadata.loc[samples.index]                                                                                       
    samples_with_dog = "Percentage of sample with dogs: " + str(((sample_metadata[sample_metadata.dog == "true"].shape[0])/1000)*100)
    samples_with_ibd = "Percentage of sample with IBD: " + str((((sample_metadata[sample_metadata.ibd == "Diagnosed by a medical professional (doctor, physician assistant)"].shape[0]))/1000)*100)   
    samples_with_diabetes = "Percentage of sample with diabetes: " + str((((sample_metadata[sample_metadata.diabetes == "Diagnosed by a medical professional (doctor, physician assistant)"].shape[0]))/1000)*100) 
    samples_with_cancer = "Percentage of sample with cancer: " + str((((sample_metadata[sample_metadata.cancer == "Diagnosed by a medical professional (doctor, physician assistant)"].shape[0]))/1000)*100) 
    samples_with_college = "Percentage of sample with a college degree: " + str((((sample_metadata[sample_metadata.level_of_education == "Bachelor's degree"].shape[0]))/1000)*100) 
    sample_metadata.fillna(0)
    sample_metadata.birth_year = sample_metadata.birth_year.replace({'Not applicable': 0})
    sample_metadata.birth_year = sample_metadata.birth_year.replace({'Not provided': 0})
    samples_older_70 = "Percentage of sample over 70: " + str((((sample_metadata[(sample_metadata.birth_year.astype(float) < 1949) & (sample_metadata.birth_year.astype(float) > 1919)].shape[0]))/1000)*100)  
    sample_metadata.birth_year = sample_metadata.birth_year.replace({0: np.NaN})
    sample_metadata.birth_year = sample_metadata.birth_year.astype(float)
    age_average = (2019 - sample_metadata.birth_year.mean())
    age_average_return = "Average age of sample: " + str(age_average)
    
    dict = [samples_with_dog, samples_with_ibd, samples_with_diabetes, samples_with_cancer, samples_with_college, samples_older_70, age_average_return] 
    return dict 

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
    metadata_copy = metadata_copy[metadata_copy.cancer == "I do not have this condition"]
    metadata_copy = metadata_copy[metadata_copy.alzheimers == "I do not have this condition"]
    metadata_copy = metadata_copy[metadata_copy.cardiovascular_disease == "I do not have this condition"]
    metadata_copy = metadata_copy[metadata_copy.diabetes == "I do not have this condition"]
    metadata_copy = metadata_copy[metadata_copy.ibd == "I do not have this condition"]
    metadata_copy = metadata_copy[metadata_copy.ibs == "I do not have this condition"]
    metadata_copy = metadata_copy[metadata_copy.kidney_disease == "I do not have this condition"]
    metadata_copy = metadata_copy[metadata_copy.liver_disease == "I do not have this condition" ]
    metadata_copy = metadata_copy[metadata_copy.lung_disease == "I do not have this condition"]
    metadata_copy = metadata_copy[metadata_copy.mental_illness == "false"]
    metadata_copy = metadata_copy[metadata_copy.skin_condition == "I do not have this condition"]
    metadata_copy.bmi = metadata_copy.bmi.replace({'Not applicable': 0})
    metadata_copy.bmi = metadata_copy.bmi.replace({'Not provided': 0})
    metadata_copy = metadata_copy[metadata_copy.bmi.astype(float) > 18.5]
    metadata_copy = metadata_copy[metadata_copy.bmi.astype(float) < 25.0]
    metadata_copy.birth_year = metadata_copy.birth_year.replace({'Not applicable': 0})
    metadata_copy.birth_year = metadata_copy.birth_year.replace({'Not provided': 0})
    metadata_copy = metadata_copy[metadata_copy.birth_year.astype(float) > 1959]
    metadata_copy = metadata_copy[metadata_copy.birth_year.astype(float) < 1999]
    id_list = metadata_copy["sample_name"].tolist()


    return id_list 

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
