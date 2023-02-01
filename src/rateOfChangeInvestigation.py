# Census Data Quality Research
# Written By Ian McKechnie
# Last Updated: Tuesday Jan 28, 2023
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
csv_data = helperFunctions.getFormattedCensusData(country, specie, species)
# print("CSV DATA")
# print(csv_data)

# Step 4: Get National Data
national_data = helperFunctions.getFormattedNationalData(country, specie, species)

# Get the rate of change of each point in each data set and put it into arrays
fao_roc = helperFunctions.getROC(fao_data, "population")
oie_roc = helperFunctions.getROC(oie_data, "population")
# print("HERE")
# print(type(csv_data))
csv_roc = helperFunctions.getROC(csv_data, "population")
# print(csv_roc)

national_roc = helperFunctions.getROC(national_data, "population")

# Step 5: Find the largest distance between all the points for each given year
dfs = {"FAO Data" : fao_roc, "OIE Data": oie_roc, "Census Data" : csv_roc, "National Data" : national_roc}

# plot the data
fig = go.Figure()

for i in dfs:
    fig = fig.add_trace(go.Scatter(x = dfs[i]["year"],
                                   y = dfs[i]["rateOfChange"],
                                   name = i))

fig.update_layout(
    title=f"Rate of Change of {specie} in {country} Between Four Data Sources",
    legend_title="Sources",
)
fig.show()

