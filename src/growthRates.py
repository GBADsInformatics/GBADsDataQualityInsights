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
from plotly.subplots import make_subplots




def str2frame(estr, source, sep = ',', lineterm = '\n'):
    dat = [x.split(sep) for x in estr.split(lineterm)][1:-1]
    if source == "fao":
        df = pd.DataFrame(dat, columns=['iso3', "country", 'year', 'species', 'population'] )
    elif source == "oie":
        df = pd.DataFrame(dat, columns=["country", 'year', 'species', 'population', "source"] )
    return df


 # Step one: Get FAO data
countries = ["Ethiopia", "Canada", "USA", "Ireland", "India", "Brazil", "Botswana", "Egypt", "South Africa", "Indonesia", "China", "Australia", "NewZealand", "Japan", "Mexico", "Argentina", "Chile"]
species = ["Cattle","Sheep","Goats","Pigs","Chickens"]
specie = "Cattle"
country = "USA"

if specie == None:
    specie = species[0]

if country == "USA":
    fao_data = fao.get_data("United%20States%20of%20America", specie)

elif country == None:
    fao_data = fao.get_data(countries[0], specie)

else:
    fao_data = fao.get_data(country, specie)

fao_data = str2frame(fao_data, "fao")
fao_data['source'] = "fao"
fao_data = fao_data.drop(columns=['iso3', "country"])
fao_data = fao_data.replace('"','', regex=True)
fao_data.sort_values(by=['year'], inplace=True)

# Step two: Get OIE data
if country == "USA":
    oie_data = oie.get_data("United%20States%20of%20America", specie)
else:
    oie_data = oie.get_data(country, specie)
oie_data = str2frame(oie_data, "oie")
oie_data['source'] = "oie"
oie_data = oie_data.drop(columns=['country'])
oie_data = oie_data.replace('"','', regex=True)
oie_data.sort_values(by=['year'], inplace=True)

# Step 3: Get Census data
try:
    csv_data = pd.read_csv(f"censusData/{country}.csv")
    species = species + csv_data["species"].tolist() # Add the species from the csv file to the list of species
    species = list(dict.fromkeys(species))  # Remove duplicates from the list of species
    csv_index_list = csv_data[(csv_data['species'] == specie)].index.tolist()

except:
    print("Error, count not find the correct csv file")
    csv_data = pd.DataFrame()
    csv_index_list = []

# Step 4: Get National data
try:
    nationalData = pd.read_csv(f"nationalData/{country}.csv")
    #Add the species from the national data
    species = species + nationalData["species"].tolist() # Add the species from the csv file to the list of species
    species = list(dict.fromkeys(species))  # Remove duplicates from the list of species
    nationalData_index_list = nationalData[(nationalData['species'] == specie)].index.tolist()

except:
    print("Error, count not find the correct csv file")
    nationalData = pd.DataFrame()
    nationalData_index_list = []

#print(fao_data.head())

FaoGrowthRate = helperFunctions.growthRate(fao_data, "population")

print(FaoGrowthRate.head())

FaoGrowthRate.sort_values(by=['growthRate'], inplace=True)

x = np.random.normal( 0, 1, len(FaoGrowthRate['growthRate'].tolist()))

#print(FaoGrowthRate['growthRate'].tolist())
data = FaoGrowthRate['growthRate'].tolist()
# fig = make_subplots(rows=2, cols=2,
#                     specs=[[{"secondary_y": True}, {"secondary_y": True}],
#                            [{"secondary_y": True}, {"secondary_y": True}]])
fig = make_subplots(rows = 1, cols = 1, shared_xaxes=False, shared_yaxes=False, specs=[[{"type": "histogram", "type" : "indicator"}]])


sub = ff.create_distplot([x], ["FAO"], bin_size=0.1)
#fig = px.histogram(FaoGrowthRate, x="year", y="growthRate", marginal="box", hover_data=FaoGrowthRate.columns)

#Add the mean and standard deviation to the graph
mean = np.mean(x)
stdev_pluss = np.std(x)
stdev_minus = np.std(x)*-1
mean = np.mean(x)
stdev_pluss2 = np.std(x) * 2
stdev_minus2 = np.std(x)*-1 * 2
stdev_pluss3 = np.std(x) * 3
stdev_minus3 = np.std(x)*-1 * 3


# sub.add_shape(type="line",x0=mean, x1=mean, y0 =0, y1=0.4 , xref='x', yref='y',
#                line = dict(color = 'blue', dash = 'dash'))
# sub.add_shape(type="line",x0=stdev_pluss, x1=stdev_pluss, y0 =0, y1=0.4 , xref='x', yref='y',
#                line = dict(color = 'red', dash = 'dash'))
# sub.add_shape(type="line",x0=stdev_minus, x1=stdev_minus, y0 =0, y1=0.4 , xref='x', yref='y',
#                line = dict(color = 'red', dash = 'dash'))
# sub.add_shape(type="line",x0=stdev_pluss2, x1=stdev_pluss2, y0 =0, y1=0.4 , xref='x', yref='y',
#                line = dict(color = 'Green', dash = 'dash'))
# sub.add_shape(type="line",x0=stdev_minus2, x1=stdev_minus2, y0 =0, y1=0.4 , xref='x', yref='y',
#                line = dict(color = 'Green', dash = 'dash'))

# Get the values outside of the second standard deviation
outliers = pd.DataFrame(columns=['year', "growthRate"])

#print(FaoGrowthRate.iloc[0])
for i in range(len(x)):
    if FaoGrowthRate.iloc[i]['growthRate'] > stdev_pluss * 3 or FaoGrowthRate.iloc[i]['growthRate'] < stdev_minus * 3:
        data = [FaoGrowthRate.iloc[i]['year'], FaoGrowthRate.iloc[i]['growthRate']]
        row = pd.DataFrame([data], columns=['year', "growthRate"])
        outliers = pd.concat([outliers, row], axis=0)

print(outliers)


# Adding a table to show the outliers

fig.add_trace(
    go.Table(header=dict(values=['Year', 'Growth Rate']),
        cells=dict(values=[outliers['year'], outliers['growthRate']])),
    row=1, col=1, secondary_y=False
)

fig.add_trace(
    sub.data[0],
    row=1, col=1, secondary_y=False
)



fig.show()


