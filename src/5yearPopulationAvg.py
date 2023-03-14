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
import plotly.graph_objects as go


def groupBy5Years(data, startYear, endYear, type):
    # Group the data into 5 year intervals
    sum = 0
    counter = 0
    for year in range(int(startYear), int(endYear)):
        try:
            if type == "String":
                row = data[data['year'] == str(year)]
            else:
                row = data[data['year'] == int(year)]
            sum += int(row['population'])
            counter += 1

        except:
            continue

    if counter == 0:
        return 0
    return sum/counter


# Step one: Get FAO Data
countries = ["Ethiopia", "Canada", "USA", "Ireland", "India", "Brazil", "Botswana", "Egypt", "South Africa", "Indonesia", "China", "Australia", "NewZealand", "Japan", "Mexico", "Argentina", "Chile"]
species = ["Cattle","Sheep","Goats","Pigs","Chickens"]
specie = "Cattle"
country = "India"

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

print("csv Data: ")
print(csv_data)

#Get a list of all the years from each data source
fao_years = fao_data['year'].tolist()
oie_years = oie_data['year'].tolist()
csv_years = csv_data['year'].tolist()
national_years = nationalData['year'].tolist()

years = fao_years + oie_years + csv_years + national_years

years = list(dict.fromkeys(years))
years = [int(s) for s in years]
years.sort()

#Get each ones five year averages
fao_averages = []
oie_averages = []
csv_averages = []
national_averages = []
yearsArr = []

counter = 0

if len(years) == 0:
    print("No data found")
    exit()

for i in range(years[0], years[-1]):
    if counter % 5 == 0 and counter != 0:
        fao_averages.append(groupBy5Years(fao_data, i - 5, i, "String"))
        oie_averages.append(groupBy5Years(oie_data, i - 5, i, "String"))
        csv_averages.append(groupBy5Years(csv_data, i - 5, i, "Int"))
        national_averages.append(groupBy5Years(nationalData, i - 5, i, "Int"))
        yearsArr.append(i)

    counter += 1


#Graph them
masterDf = pd.DataFrame(columns = ["year", "fao", "oie", "census", "national",])
masterDf['year'] = yearsArr
masterDf['fao'] = fao_averages
masterDf['oie'] = oie_averages
masterDf['census'] = csv_averages
masterDf['national'] = national_averages

#Census and national are all zeros
if masterDf['census'].isnull().values.any() and masterDf['national'].isnull().values.any():
    fig = go.Figure([
        go.Bar(name='FAO', x=masterDf['year'], y=masterDf['fao']),
        go.Bar(name='OIE', x=masterDf['year'], y=masterDf['oie'])
    ])

#National is all zeros
elif masterDf['national'].isnull().values.any():
    fig = go.Figure([
        go.Bar(name='FAO', x=masterDf['year'], y=masterDf['fao']),
        go.Bar(name='National', x=masterDf['year'], y=masterDf['national']),
        go.Bar(name='OIE', x=masterDf['year'], y=masterDf['oie']),
    ])

#Census is all zeros
elif masterDf['census'].isnull().values.any():
    fig = go.Figure([
        go.Bar(name='FAO', x=masterDf['year'], y=masterDf['fao']),
        go.Bar(name='OIE', x=masterDf['year'], y=masterDf['oie']),
        go.Bar(name='Census', x=masterDf['year'], y=masterDf['census']),
    ])

else:
    fig = go.Figure([
        go.Bar(name='FAO', x=masterDf['year'], y=masterDf['fao']),
        go.Bar(name='National', x=masterDf['year'], y=masterDf['national']),
        go.Bar(name='OIE', x=masterDf['year'], y=masterDf['oie']),
        go.Bar(name='Census', x=masterDf['year'], y=masterDf['census']),
    ])

fig.update_xaxes(title="Year")
fig.update_yaxes(title="Population")

print("len yearsArr: " + str(len(yearsArr)))

fig.update_xaxes(nticks=len(yearsArr))
fig.show()