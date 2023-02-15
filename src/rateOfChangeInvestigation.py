# Census Data Quality Research
# Written By Ian McKechnie
# Last Updated: Tuesday Feb 15, 2023

# We could take the average rate of change for the
# increase in a species population for each year for a
# given country for each data source. We could compare
# the rate of change between each data source and if
# one is substantially bigger than the other two it could
# be concluded that there is a higher chance that it is wrong.

import API_helpers.fao as fao
import API_helpers.oie as oie
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import API_helpers.helperFunctions as helperFunctions
import plotly.figure_factory as ff
import numpy as np
import plotly.graph_objects as go


# Step one: Get FAO Data
countries = ["Ethiopia", "Canada", "USA", "Ireland", "India", "Brazil", "Botswana", "Egypt", "South Africa", "Indonesia", "China", "Australia", "NewZealand", "Japan", "Mexico", "Argentina", "Chile"]
species = ["Cattle","Sheep","Goats","Pigs","Chickens"]
specie = "Cattle"
country = "USA"

if country == "USA":
    fao_data = fao.get_data("United%20States%20of%20America", specie)
else:
    fao_data = fao.get_data(country, specie)

fao_data = fao.formatFAOData(fao_data)

# Step two: Get OIE Data
if country == "USA":
    oie_data = oie.get_data("United%20States%20of%20America", specie)
else:
    oie_data = oie.get_data(country, specie)

oie_data = oie.formatOIEData(oie_data)

# Step 3: Get Census Data
csv_data, csv_index_list, species = helperFunctions.getFormattedCensusData(country, specie, species)

print("Csv data")
print(csv_data)


# Step 4: Get National Data
nationalData, nationalData_index_list, species = helperFunctions.getFormattedNationalData(country, specie, species)

# Get the rate of change of each point in each data set and put it into arrays
fao_roc = helperFunctions.getROC(fao_data, "population")
oie_roc = helperFunctions.getROC(oie_data, "population")
csv_roc = helperFunctions.getROC(csv_data, "population")
national_roc = helperFunctions.getROC(nationalData, "population")


# print("Rate of changes")
# print(fao_roc.head())
# print(oie_roc.head())
# print(csv_roc.head())
print(national_roc)

# Step 5: Find the largest distance between all the points for each given year
allData = pd.merge(fao_roc, oie_roc, on="year")
allData = pd.merge(allData, csv_roc, on="year")
allData = pd.merge(allData, national_roc, on="year")

print("all Data")
print(allData)

