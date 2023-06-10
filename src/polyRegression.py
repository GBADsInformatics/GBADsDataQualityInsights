# Using Polynomial Regression to Predict Animal Populations

import sys
sys.path.append('../../src')
from sklearn.linear_model import LinearRegression
import API_helpers.fao as fao
import API_helpers.woah as woah
import API_helpers.helperFunctions
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
import plotly.graph_objects as go


countries = ["Ethiopia", "Canada", "USA", "Ireland", "India", "Brazil", "Botswana", "Egypt", "South Africa", "Indonesia", "China", "Australia", "NewZealand", "Japan", "Mexico", "Argentina", "Chile"]
species = ["Cattle","Sheep","Goats","Pigs","Chickens"]
sources = ['No Options Available']

#Build a Plotly graph around the data
app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Data Quality Comparison for FAOSTAT, WOAH, Census Data, and National Sources'),

    dcc.Graph(id='graph'),

    html.H3(children='Countries'),
    dcc.Dropdown(
        countries,
        value=countries[0],
        id="country_checklist",
    ),

    html.H3(children='Species'),
    dcc.Dropdown(
        species,
        value=species[0],
        id="species_checklist",
    ),

    html.H3(children='Source for Prediction'),
    dcc.Dropdown(
        sources,
        value=sources[0],
        id="sources_checklist",
    ),

    html.Div([
        html.Div([
            html.H3(children='Degree of Polynomial Regression (>1)'),
            dcc.Input(id='polyDegree', value='2', type='number'),
        ],style={'width': '49%', 'display': 'inline-block'}),

        html.Div([
            html.H3(children='Year to be predicted to'),
        dcc.Input(id='maxYear', value='2050', type='number'),
        ],style={'width': '49%', 'display': 'inline-block'}),
    ])
])

@app.callback(
    Output("species_checklist", "options"),
    Input("country_checklist", "value"))
def update_species_checklist(country):
    # Step one: Get FAO data
    species = ["Cattle","Sheep","Goats","Pigs","Chickens"]

    # Step 3: Get Census data
    try:
        csv_data = pd.read_csv(f"censusData/{country}.csv")
        species = species + csv_data["species"].tolist() # Add the species from the csv file to the list of species
        species = list(dict.fromkeys(species))  # Remove duplicates from the list of species

    except:
        print("Error, count not find the correct csv file")

    # Step 4: Get National data
    try:
        nationalData = pd.read_csv(f"nationalData/{country}.csv")
        species = species + nationalData["species"].tolist() # Add the species from the csv file to the list of species
        species = list(dict.fromkeys(species))  # Remove duplicates from the list of species

    except:
        print("Error, count not find the correct csv file")

    return species


@app.callback(
    Output("sources_checklist", "options"),
    Input("species_checklist", "value"),
    Input("country_checklist", "value")
)
def populate_dropDown(specie, country):
    species = ["Cattle","Sheep","Goats","Pigs","Chickens"]

    if specie == None:
        specie = species[0]

    if country == "USA":
        fao_data = fao.get_data("United%20States%20of%20America", specie)

    elif country == None:
        fao_data = fao.get_data("Ethiopia", specie)

    else:
        fao_data = fao.get_data(country, specie)

    fao_data = fao.formatFAOData(fao_data)

    # Step two: Get woah data
    if country == "USA":
        woah_data = woah.get_data("United%20States%20of%20America", specie)
    else:
        woah_data = woah.get_data(country, specie)

    woah_data = woah.formatWoahData(woah_data)

    # Step 3: Get Census data
    csv_data, csv_index_list, species  = API_helpers.helperFunctions.getFormattedCensusData(country, specie, species)

    # Step 4: Get National data
    nationalData, nationalData_index_list, species = API_helpers.helperFunctions.getFormattedNationalData(country, specie, species)

    #Fill the dropdown with the available sources
    sources = []
    # if fao_data.empty == False:
    sources.append("FAOSTAT")

    # if woah_data.empty == False:
    sources.append("WOAH")

    # if csv_data.empty == False:
    sources.append("UN Census Data")

    # if nationalData.empty == False:
    sources.append("National Census Data")

    if sources == []:
        sources = ["No Options Available"]

    return sources


@app.callback(
    Output("graph", "figure"),
    Input("species_checklist", "value"),
    Input("country_checklist", "value"),
    Input("sources_checklist", "value"),
    Input("polyDegree", "value"),
    Input("maxYear", "value"),
)
def polynomialRegression(specie, country, source, polyDegree, maxYear):
    maxYear = int(maxYear)

    # Step one: Get FAO data
    countries = ["Ethiopia", "Canada", "USA", "Ireland", "India", "Brazil", "Botswana", "Egypt", "South Africa", "Indonesia", "China", "Australia", "NewZealand", "Japan", "Mexico", "Argentina", "Chile"]
    species = ["Cattle","Sheep","Goats","Pigs","Chickens"]

    if specie == None:
        specie = species[0]

    if country == "USA":
        fao_data = fao.get_data("United%20States%20of%20America", specie)

    elif country == None:
        fao_data = fao.get_data(countries[0], specie)

    else:
        fao_data = fao.get_data(country, specie)

    fao_data = fao.formatFAOData(fao_data)

    # Step two: Get woah data
    if country == "USA":
        woah_data = woah.get_data("United%20States%20of%20America", specie)
    else:
        woah_data = woah.get_data(country, specie)

    woah_data = woah.formatWoahData(woah_data)

    # Step 3: Get Census data
    csv_data, csv_index_list, species = API_helpers.helperFunctions.getFormattedCensusData(country, specie, species)

    # Step 4: Get National data
    nationalData, nationalData_index_list, species = API_helpers.helperFunctions.getFormattedNationalData(country, specie, species)

    # Build a master dataframe
    master_df = pd.concat([fao_data, woah_data, csv_data.iloc[csv_index_list], nationalData.iloc[nationalData_index_list]])

    # Build the plotly graph
    fig = px.line(master_df,
                x=master_df["year"],
                y=master_df["population"],
                color=master_df["source"],
                markers=True)

    # Build out the polynomial regression lines
    polyDegree = int(polyDegree)
    x = []
    if source != "No Options Available":
        for i in range(1, polyDegree+1):
            #Turn the data into a numpy array
            if source == "FAOSTAT":
                x = fao_data["year"]
                y = fao_data["population"]

            elif source == "WOAH":
                x = woah_data["year"]
                y = woah_data["population"]

            elif source == "UN Census Data":
                x = csv_data.iloc[csv_index_list]["year"]
                y = csv_data.iloc[csv_index_list]["population"]

            else:
                x = nationalData.iloc[nationalData_index_list]["year"]
                y = nationalData.iloc[nationalData_index_list]["population"]

            #Convert to numpy arrays
            x = np.array(x)
            y = np.array(y)

            #Fit the model
            model = PolynomialFeatures(degree=i)
            x_new = model.fit_transform(x.reshape(-1, 1))
            new_model = LinearRegression()
            new_model.fit(x_new, y)

            #Add in any missing years
            for i in range(1960, x[-1]+1):
                if i not in x:
                    x = np.append(x, i)

            x.sort()

            #Add in the predicted value years
            print("x[-1]: ", x[-1])
            print(x)
            x = np.append(x, [i for i in range(x[-1] + 1, maxYear+1)])
            x_new = model.fit_transform(x.reshape(-1, 1))
            ypredict = new_model.predict(x_new)

            fig.add_traces(go.Scatter(x=x, y=ypredict, mode='lines', name='Polynomial Regression Degree ' + str(i)))

    fig.update_layout(
        title=f"Population of {specie} in {country}",
        xaxis_title="Year",
        yaxis_title="Population",
        legend_title="Sources",
        font= dict(
            size = 18,
            color = "black"
        ),
        plot_bgcolor='white',
        xaxis = dict(
        tickmode='array',
        tickvals = x,
        ticktext = x,
    ),
    )

    fig.update_yaxes(
        type='linear',
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )

    fig.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )

    fig.update_traces(line=dict(width=5))

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
