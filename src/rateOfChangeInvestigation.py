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


print("Rate of changes")
print("fao", fao_roc.tail())
print("oie", oie_roc.tail())
print("csv", csv_roc)
print("natonal", national_roc.tail())

# Step 5: Find the path distance between each point in each data set
mainDict = {}

# Get every year for all tables
years = []
for year in fao_roc['year']:
    years.append(year)

# Check the OIE data
if oie_roc['year'].to_list()[0] not in years or oie_roc['year'].to_list()[-1] not in years:
    for year in oie_roc['year']:
        if year not in years:
            years.append(year)

# Check the CSV data

if csv_roc != [] and csv_roc['year'].to_list()[0] not in years or csv_roc['year'].to_list()[-1] not in years:
    for year in csv_roc['year']:
        if year not in years:
            years.append(year)

# Check the National data
if national_roc != [] and national_roc['year'].to_list()[0] not in years or national_roc['year'].to_list()[-1] not in years:
    for year in national_roc['year']:
        if year not in years:
            years.append(year)



# Create the dictionary
for year in years:
    # This df is for each year in the table
    mainDf = pd.DataFrame(columns=["elen", "fao", "oie", "csv", "national"])

    # All the FAO distances
    fao_distances = ['fao']
    fao_distances.append(None)

    if fao_roc[year] != None:
        if oie_roc[year] != None:
            fao_distances.append(fao_roc[year]['rateOfChange'] - oie_roc[year]['rateOfChange'])

        if csv_roc != [] and csv_roc[year] != None:
            fao_distances.append(fao_roc[year]['rateOfChange'] - csv_roc[year]['rateOfChange'])

        if national_roc != [] and national_roc[year] != None:
            fao_distances.append(fao_roc[year]['rateOfChange'] - national_roc[year]['rateOfChange'])

        mainDf.loc[0] = fao_distances

    else:
        fao_distances.append(None)
        fao_distances.append(None)
        fao_distances.append(None)

        mainDf.loc[0] = fao_distances

    # All the OIE distances
    oie_distances = ['oie']

    if fao_roc[year] != None:
        if fao_roc[year] != None:
            oie_distances.append(oie_roc[year]['rateOfChange'] - fao_roc[year]['rateOfChange'])

        oie_distances.append(None)

        if csv_roc != [] and csv_roc[year] != None:
            oie_distances.append(oie_roc[year]['rateOfChange'] - csv_roc[year]['rateOfChange'])

        if national_roc != [] and national_roc[year] != None:
            oie_distances.append(oie_roc[year]['rateOfChange'] - national_roc[year]['rateOfChange'])

        mainDf.loc[1] = oie_distances

    else:
        oie_distances.append(None)
        oie_distances.append(None)
        oie_distances.append(None)
        oie_distances.append(None)

        mainDf.loc[1] = oie_distances

    # All the CSV distances
    csv_distances = ['csv']

    if csv_roc[year] != None:
        if fao_roc[year] != None:
            csv_distances.append(csv_roc[year]['rateOfChange'] - fao_roc[year]['rateOfChange'])

        if oie_roc[year] != None:
            csv_distances.append(csv_roc[year]['rateOfChange'] - oie_roc[year]['rateOfChange'])

        csv_distances.append(None)

        if national_roc != [] and national_roc[year] != None:
            csv_distances.append(csv_roc[year]['rateOfChange'] - national_roc[year]['rateOfChange'])

        mainDf.loc[2] = csv_distances

    else:
        csv_distances.append(None)
        csv_distances.append(None)
        csv_distances.append(None)
        csv_distances.append(None)

        mainDf.loc[2] = csv_distances

    # All the National distances
    national_distances = ['national']

    if national_roc[year] != None:
        if fao_roc[year] != None:
            national_distances = ['national', national_roc[year]['rateOfChange'] - fao_roc[year]['rateOfChange']]

        if oie_roc[year] != None:
            national_distances.append(national_roc[year]['rateOfChange'] - oie_roc[year]['rateOfChange'])

        if csv_roc != [] and csv_roc[year] != None:
            national_distances.append(national_roc[year]['rateOfChange'] - csv_roc[year]['rateOfChange'])

        national_distances.append(None)

        mainDf.loc[3] = national_distances

    else:
        national_distances.append(None)
        national_distances.append(None)
        national_distances.append(None)
        national_distances.append(None)

        mainDf.loc[3] = national_distances


    mainDict[year] = mainDf

print(mainDict)