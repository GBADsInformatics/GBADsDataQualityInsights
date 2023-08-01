# Census Data Quality Research
# Written By Ian McKechnie

import sys
sys.path.append('../../src')
import API_helpers.fao as fao
import API_helpers.woah as woah
import API_helpers.helperFunctions
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
from PIL import Image


countries = ["Greece", "Ethiopia", "Canada", "USA", "Ireland", "India", "Brazil", "Botswana", "Egypt", "South Africa", "Indonesia", "China", "Australia", "NewZealand", "Japan", "Mexico", "Argentina", "Chile"]
species = ["Cattle","Sheep","Goats","Pigs","Chickens"]
img = pil_image = Image.open("../lib/logo.png")


#Build a Plotly graph around the data
app = Dash(__name__)

app.layout = html.Div(children=[
    html.Img(src=pil_image, style={'width': '25%', 'display': 'inline-block', "align-items": "left" }),
    html.H1(children='Title'),

    dcc.Tabs(id="tabs", value='GDV', children=[
        dcc.Tab(label='General Data Viewer', value='GDV'),
        dcc.Tab(label='Table of data', value='table-tab'),
    ]),
    html.Br(),
    html.Div(id='contents'),
])


@app.callback(
        Output('contents', 'children'),
        Input('tabs', 'value'))
def render_content(tab):
    if tab == 'graph-tab':
        return html.Div([
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
        ])

    else:
        return html.Div([

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
    Output("graph", "figure"),
    Input("species_checklist", "value"),
    Input("country_checklist", "value"))
def update_line_chart(specie, country):
    # Step one: Get FAO data
    countries = ["Greece", "Ethiopia", "Canada", "USA", "Ireland", "India", "Brazil", "Botswana", "Egypt", "South Africa", "Indonesia", "China", "Australia", "NewZealand", "Japan", "Mexico", "Argentina", "Chile"]
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
    #master_df = pd.concat([fao_data, woah_data, csv_data.iloc, nationalData.iloc])
    master_df = pd.concat([fao_data, woah_data, csv_data.iloc[csv_index_list], nationalData.iloc[nationalData_index_list]])

    # Build the plotly graph
    fig = px.line(
            master_df,
            x=master_df["year"],
            y=master_df["population"],
            color=master_df["source"],
            markers=True)

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

    fig.update_layout(
        title=f"Population of {specie} in {country}",
        xaxis_title="Year",
        yaxis_title="Population",
        legend_title="Sources",
        font = dict(
            size=18,
        ),
        plot_bgcolor='white',
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)