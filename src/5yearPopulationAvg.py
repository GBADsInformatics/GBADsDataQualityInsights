# Census Data Quality Research
# Written By Ian McKechnie

# This program gets the population number for a specific animal from a specific country from
# all data sources. It then groups them into 5 year intervals and finds the average population.
# The averages are then plotted on a histogram.

import API_helpers.fao as fao
import API_helpers.oie as oie
import pandas as pd
import plotly.express as px
import API_helpers.helperFunctions as helperFunctions
import numpy as np


def groupBy5Years(data, startYear, endYear):
    # Group the data into 5 year intervals
    grouped_data = []
    for year in range(startYear, endYear):
        # Get the average population for the 5 year interval
        population = 0
        for index, row in data.iterrows():
            if row['year'] == year:
                population += row['population']
                grouped_data.append(population)
                break



# Step one: Get FAO Data
countries = ["Ethiopia", "Canada", "USA", "Ireland", "India", "Brazil", "Botswana", "Egypt", "South Africa", "Indonesia", "China", "Australia", "NewZealand", "Japan", "Mexico", "Argentina", "Chile"]
species = ["Cattle","Sheep","Goats","Pigs","Chickens"]
specie = "Goats"
country = "South Africa"

# Step one: Get FAO Data and OIE Data
if country == "USA":
    fao_data = fao.get_data("United%20States%20of%20America", specie)
    oie_data = oie.get_data("United%20States%20of%20America", specie)
else:
    fao_data = fao.get_data(country, specie)
    oie_data = oie.get_data(country, specie)

fao_data = fao.formatFAOData(fao_data)
oie_data = oie.formatOIEData(oie_data)

# Step 3: Get Census Data
csv_data, csv_index_list, species = helperFunctions.getFormattedCensusData(country, specie, species)

#Only get the rows that have the correct specie
new_csv_data = []
for index, row in csv_data.iterrows():
    if row['species'] == specie:
        new_csv_data.append( [row['year'], row['population']] )

csv_data = pd.DataFrame(new_csv_data, columns = ["year", "population"])

# Step 4: Get National Data
nationalData, nationalData_index_list, species = helperFunctions.getFormattedNationalData(country, specie, species)

new_national_data = []
for index, row in nationalData.iterrows():
    if row['species'] == specie:
        new_national_data.append( [row['year'], row['population']] )

nationalData = pd.DataFrame (new_national_data, columns = ["year", "population"])


