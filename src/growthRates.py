# Census Data Quality Research
# Written By Ian McKechnie
# Last Updated: Tuesday Feb 15, 2023

#Hypothsis
# If you take all the growth rates for a population of animals in a country every year,
# and you plot every yearly growth rate, it should produce a normal curve. From there we can
# spot outliers by defining a cut off of 3 standard deviations. Past this point we can label
# those points as outliers and conclude that there is a high chance that they are inaccuracies.

import sys
sys.path.append('../../src')
import API_helpers.fao as fao
import API_helpers.woah as woah
import API_helpers.helperFunctions
import pandas as pd
from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.express as px
import API_helpers.helperFunctions as helperFunctions
import plotly.figure_factory as ff
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def str2frame(estr, source, sep = ',', lineterm = '\n'):
    dat = [x.split(sep) for x in estr.split(lineterm)][1:-1]
    if source == "faostat":
        df = pd.DataFrame(dat, columns=['iso3', "country", 'year', 'species', 'population'] )
    elif source == "WOAH":
        df = pd.DataFrame(dat, columns=["country", 'year', 'species', 'population', "source"] )
    return df

# Get all the data
countries = ["Ethiopia", "Canada", "USA", "Ireland", "India", "Brazil", "Botswana", "Egypt", "South Africa", "Indonesia", "China", "Australia", "NewZealand", "Japan", "Mexico", "Argentina", "Chile"]
species = ["Cattle","Sheep","Goats","Pigs","Chickens"]
specie = "Sheep"
country = "Ethiopia"

if specie == None:
    specie = species[0]

if country == "USA":
    fao_data = fao.get_data("United%20States%20of%20America", specie)
    woah_data = woah.get_data("United%20States%20of%20America", specie)

elif country == None:
    fao_data = fao.get_data(countries[0], specie)
    woah_data = woah.get_data(countries[0], specie)

else:
    fao_data = fao.get_data(country, specie)
    woah_data = woah.get_data(country, specie)

woah_data = woah.formatWoahData(woah_data)

census_data, csv_index_list, species = API_helpers.helperFunctions.getFormattedCensusData(country, specie, species)

national_data, nationalData_index_list, species = API_helpers.helperFunctions.getFormattedNationalData(country, specie, species)


# Get the outliers from the FAO Data
fao_data = str2frame(fao_data, "faostat")
fao_data['source'] = "faostat"
fao_data = fao_data.drop(columns=['iso3', "country"])
fao_data = fao_data.replace('"','', regex=True)
fao_data.sort_values(by=['year'], inplace=True)

# Step two: Get woah data
if country == "USA":
    woah_data = woah.get_data("United%20States%20of%20America", specie)
else:
    woah_data = woah.get_data(country, specie)
woah_data = str2frame(woah_data, "WOAH")
woah_data['source'] = "WOAH"
woah_data = woah_data.drop(columns=['country'])
woah_data = woah_data.replace('"','', regex=True)
woah_data.sort_values(by=['year'], inplace=True)

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

FaoGrowthRate = helperFunctions.growthRate(fao_data, "population", specie)

FaoGrowthRate.sort_values(by=['growthRate'], inplace=True)

data = FaoGrowthRate['growthRate'].tolist()

fig = ff.create_distplot([data], ["FAOSTAT"], bin_size=0.3)
fig.update_xaxes(title_text='Growth Rate')
fig.update_yaxes(title_text='Density')

#Add the mean and standard deviation to the graph
mean = np.mean(data)
stdev_pluss = np.std(data)
stdev_minus = np.std(data)*-1
stdev_pluss2 = np.std(data) * 2
stdev_minus2 = np.std(data)*-1 * 2
stdev_pluss3 = np.std(data) * 3
stdev_minus3 = np.std(data)*-1 * 3


fig.add_shape(type="line",x0=mean, x1=mean, y0 =0, y1=0.4 , xref='x', yref='y',
            line = dict(color = 'blue', dash = 'dash'))
fig.add_shape(type="line",x0=stdev_pluss, x1=stdev_pluss, y0 =0, y1=0.4 , xref='x', yref='y',
            line = dict(color = 'red', dash = 'dash'))
fig.add_shape(type="line",x0=stdev_minus, x1=stdev_minus, y0 =0, y1=0.4 , xref='x', yref='y',
            line = dict(color = 'red', dash = 'dash'))
fig.add_shape(type="line",x0=stdev_pluss2, x1=stdev_pluss2, y0 =0, y1=0.4 , xref='x', yref='y',
            line = dict(color = 'Black', dash = 'dash'))
fig.add_shape(type="line",x0=stdev_minus2, x1=stdev_minus2, y0 =0, y1=0.4 , xref='x', yref='y',
            line = dict(color = 'Black', dash = 'dash'))
fig.add_shape(type="line",x0=stdev_pluss3, x1=stdev_pluss3, y0 =0, y1=0.4 , xref='x', yref='y',
            line = dict(color = 'orange', dash = 'dash'))
fig.add_shape(type="line",x0=stdev_minus3, x1=stdev_minus3, y0 =0, y1=0.4 , xref='x', yref='y',
            line = dict(color = 'orange', dash = 'dash'))

fig.update_layout(
    title="Distribution of Growth Rates for FAOSTAT Data for " + specie + " in " + country,
)

# Get the values outside of the second standard deviation
fao_outliers = pd.DataFrame(columns=['year', "growthRate"])

for i in range(len(data)):
    if FaoGrowthRate.iloc[i]['growthRate'] > stdev_pluss * 3 or FaoGrowthRate.iloc[i]['growthRate'] < stdev_minus * 3:
        data = [FaoGrowthRate.iloc[i]['year'], FaoGrowthRate.iloc[i]['growthRate']]
        row = round(pd.DataFrame([data], columns=['year', "growthRate"]), 2)
        fao_outliers = pd.concat([fao_outliers, row], axis=0)


#WOAH Data
woahGrowthRate = helperFunctions.growthRate(woah_data, "population", specie)

woahGrowthRate.sort_values(by=['growthRate'], inplace=True)

data = woahGrowthRate['growthRate'].tolist()

fig2 = ff.create_distplot([data], ["WOAH"], bin_size=0.3)
fig2.update_xaxes(title_text='Growth Rate')
fig2.update_yaxes(title_text='Density')

#Add the mean and standard deviation to the graph
mean = np.mean(data)
stdev_pluss = np.std(data)
stdev_minus = np.std(data)*-1
stdev_pluss2 = np.std(data) * 2
stdev_minus2 = np.std(data)*-1 * 2
stdev_pluss3 = np.std(data) * 3
stdev_minus3 = np.std(data)*-1 * 3


fig2.add_shape(type="line",x0=mean, x1=mean, y0 =0, y1=0.4 , xref='x', yref='y',
            line = dict(color = 'blue', dash = 'dash'))
fig2.add_shape(type="line",x0=stdev_pluss, x1=stdev_pluss, y0 =0, y1=0.4 , xref='x', yref='y',
            line = dict(color = 'red', dash = 'dash'))
fig2.add_shape(type="line",x0=stdev_minus, x1=stdev_minus, y0 =0, y1=0.4 , xref='x', yref='y',
            line = dict(color = 'red', dash = 'dash'))
fig2.add_shape(type="line",x0=stdev_pluss2, x1=stdev_pluss2, y0 =0, y1=0.4 , xref='x', yref='y',
            line = dict(color = 'Black', dash = 'dash'))
fig2.add_shape(type="line",x0=stdev_minus2, x1=stdev_minus2, y0 =0, y1=0.4 , xref='x', yref='y',
            line = dict(color = 'Black', dash = 'dash'))
fig2.add_shape(type="line",x0=stdev_pluss3, x1=stdev_pluss3, y0 =0, y1=0.4 , xref='x', yref='y',
            line = dict(color = 'orange', dash = 'dash'))
fig2.add_shape(type="line",x0=stdev_minus3, x1=stdev_minus3, y0 =0, y1=0.4 , xref='x', yref='y',
            line = dict(color = 'orange', dash = 'dash'))

fig2.update_layout(
    title="Distribution of Growth Rates for WOAH Data for " + specie + " in " + country,
)

# Get the values outside of the second standard deviation
woah_outliers = pd.DataFrame(columns=['year', "growthRate"])

for i in range(len(data)):
    if woahGrowthRate.iloc[i]['growthRate'] > stdev_pluss * 3 or woahGrowthRate.iloc[i]['growthRate'] < stdev_minus * 3:
        data = [woahGrowthRate.iloc[i]['year'], woahGrowthRate.iloc[i]['growthRate']]
        row = round(pd.DataFrame([data], columns=['year', "growthRate"]), 2)
        woah_outliers = pd.concat([woah_outliers, row], axis=0)

#Census Data
CensusGrowthRate = helperFunctions.growthRate(census_data, "population", specie)

CensusGrowthRate.sort_values(by=['growthRate'], inplace=True)

data = CensusGrowthRate['growthRate'].tolist()

fig3 = None
census_outliers = pd.DataFrame(columns=['year', "growthRate"])

try:
    fig3 = ff.create_distplot([data], ["Census"], bin_size=0.3)
    fig3.update_xaxes(title_text='Growth Rate')
    fig3.update_yaxes(title_text='Density')

    #Add the mean and standard deviation to the graph
    mean = np.mean(data)
    stdev_pluss = np.std(data)
    stdev_minus = np.std(data)*-1
    stdev_pluss2 = np.std(data) * 2
    stdev_minus2 = np.std(data)*-1 * 2
    stdev_pluss3 = np.std(data) * 3
    stdev_minus3 = np.std(data)*-1 * 3

    fig3.add_shape(type="line",x0=mean, x1=mean, y0 =0, y1=0.4 , xref='x', yref='y',
                line = dict(color = 'blue', dash = 'dash'))
    fig3.add_shape(type="line",x0=stdev_pluss, x1=stdev_pluss, y0 =0, y1=0.4 , xref='x', yref='y',
                line = dict(color = 'red', dash = 'dash'))
    fig3.add_shape(type="line",x0=stdev_minus, x1=stdev_minus, y0 =0, y1=0.4 , xref='x', yref='y',
                line = dict(color = 'red', dash = 'dash'))
    fig3.add_shape(type="line",x0=stdev_pluss2, x1=stdev_pluss2, y0 =0, y1=0.4 , xref='x', yref='y',
                line = dict(color = 'black', dash = 'dash'))
    fig3.add_shape(type="line",x0=stdev_minus2, x1=stdev_minus2, y0 =0, y1=0.4 , xref='x', yref='y',
                line = dict(color = 'black', dash = 'dash'))
    fig3.add_shape(type="line",x0=stdev_pluss3, x1=stdev_pluss3, y0 =0, y1=0.4 , xref='x', yref='y',
                line = dict(color = 'orange', dash = 'dash'))
    fig3.add_shape(type="line",x0=stdev_minus3, x1=stdev_minus3, y0 =0, y1=0.4 , xref='x', yref='y',
                line = dict(color = 'orange', dash = 'dash'))

    fig3.update_layout(
        title="Distribution of Growth Rates for Census Data for " + specie + " in " + country,
    )

    # Get the values outside of the second standard deviation
    for i in range(len(data)):
        if CensusGrowthRate.iloc[i]['growthRate'] > stdev_pluss * 3 or CensusGrowthRate.iloc[i]['growthRate'] < stdev_minus * 3:
            data = [CensusGrowthRate.iloc[i]['year'], CensusGrowthRate.iloc[i]['growthRate']]
            row = round(pd.DataFrame([data], columns=['year', "growthRate"]), 2)
            census_outliers = pd.concat([census_outliers, row], axis=0)
except Exception as e:
    print(e)


#National Data
NationalGrowthRate = helperFunctions.growthRate(national_data, "population", specie)

NationalGrowthRate.sort_values(by=['growthRate'], inplace=True)

data = NationalGrowthRate['growthRate'].tolist()

fig4 = None

try:
    fig4 = ff.create_distplot([data], ["National"], bin_size=0.3)
    fig4.update_xaxes(title_text='Growth Rate')
    fig4.update_yaxes(title_text='Density')

    #Add the mean and standard deviation to the graph
    mean = np.mean(data)
    stdev_pluss = np.std(data)
    stdev_minus = np.std(data)*-1
    stdev_pluss2 = np.std(data) * 2
    stdev_minus2 = np.std(data)*-1 * 2
    stdev_pluss3 = np.std(data) * 3
    stdev_minus3 = np.std(data)*-1 * 3

    print("mean = ", mean)

    fig4.add_shape(type="line",x0=mean, x1=mean, y0 =0, y1=0.4 , xref='x', yref='y',
                line = dict(color = 'blue', dash = 'dash'))
    fig4.add_shape(type="line",x0=stdev_pluss, x1=stdev_pluss, y0 =0, y1=0.4 , xref='x', yref='y',
                line = dict(color = 'red', dash = 'dash'))
    fig4.add_shape(type="line",x0=stdev_minus, x1=stdev_minus, y0 =0, y1=0.4 , xref='x', yref='y',
                line = dict(color = 'red', dash = 'dash'))
    fig4.add_shape(type="line",x0=stdev_pluss2, x1=stdev_pluss2, y0 =0, y1=0.4 , xref='x', yref='y',
                line = dict(color = 'black', dash = 'dash'))
    fig4.add_shape(type="line",x0=stdev_minus2, x1=stdev_minus2, y0 =0, y1=0.4 , xref='x', yref='y',
                line = dict(color = 'black', dash = 'dash'))
    fig4.add_shape(type="line",x0=stdev_pluss3, x1=stdev_pluss3, y0 =0, y1=0.4 , xref='x', yref='y',
                line = dict(color = 'orange', dash = 'dash'))
    fig4.add_shape(type="line",x0=stdev_minus3, x1=stdev_minus3, y0 =0, y1=0.4 , xref='x', yref='y',
                line = dict(color = 'orange', dash = 'dash'))

    fig4.update_layout(
        title="Distribution of Growth Rates for National Data for " + specie + " in " + country,
    )


except Exception as e:
    print(e)
    fig

# Get the values outside of the second standard deviation
national_outliers = pd.DataFrame(columns=['year', "growthRate"])

for i in range(len(data)):
    if NationalGrowthRate.iloc[i]['growthRate'] > stdev_pluss * 3 or NationalGrowthRate.iloc[i]['growthRate'] < stdev_minus * 3:
        data = [NationalGrowthRate.iloc[i]['year'], NationalGrowthRate.iloc[i]['growthRate']]
        row = round(pd.DataFrame([data], columns=['year', "growthRate"]), 2)
        national_outliers = pd.concat([national_outliers, row], axis=0)


#Build a Plotly graph around the data
app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Comparing Growth Rates for FAOSTAT, WOAH, Census Data, and National Sources, Showing Outliers'),


    html.H3(children='FAOSTAT Data for ' + specie + " in " + country),
    dcc.Graph(id='graph', figure=fig),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i}
            for i in fao_outliers.columns],
        data=fao_outliers.to_dict('records'),
    ),


    html.H3(children='WOAH Data for ' + specie + " in " + country),
    dcc.Graph(id='graph2', figure=fig2),
    dash_table.DataTable(
        id='table2',
        columns=[{"name": i, "id": i}
            for i in woah_outliers.columns],
        data=woah_outliers.to_dict('records'),
    ),


    html.H3(children='Census Data for ' + specie + " in " + country),
    dcc.Graph(id='graph3', figure=fig3),
    dash_table.DataTable(
        id='table3',
        columns=[{"name": i, "id": i}
            for i in census_outliers.columns],
        data=census_outliers.to_dict('records'),
    ),


    html.H3(children='National Data for ' + specie + " in " + country),
    dcc.Graph(id='graph4', figure=fig4),
    dash_table.DataTable(
        id='table4',
        columns=[{"name": i, "id": i}
            for i in national_outliers.columns],
        data=national_outliers.to_dict('records'),
    ),

    html.Br(),
    html.Br(),
    html.H2(),
    html.H2(children='.'),
    html.H2(children='.'),
])

if __name__ == '__main__':
    app.run_server(debug=True)