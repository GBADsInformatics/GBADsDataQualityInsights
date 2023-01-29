# Census Data Qaulity Research
# Written By Ian McKechnie
# Last Updated: Tuesday Jan 28, 2023
import API_helpers.fao as fao
import API_helpers.oie as oie
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import helpers

def str2frame(estr, source, sep = ',', lineterm = '\n'):
    dat = [x.split(sep) for x in estr.split(lineterm)][1:-1]
    if source == "fao":
        df = pd.DataFrame(dat, columns=['iso3', "country", 'year', 'species', 'population'] )
    elif source == "oie":
        df = pd.DataFrame(dat, columns=["country", 'year', 'species', 'population', "source"] )
    return df

countries = ["Ethiopia", "Canada", "USA", "Ireland", "India", "Brazil", "Botswana", "Egypt", "South Africa", "Indonesia", "China", "Australia", "NewZealand", "Japan", "Mexico", "Argentina", "Chile"]
species = ["Cattle","Sheep","Goats","Pigs","Chickens"]

#Build a Plotly graph around the data
app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Data Quality Comparison for FAO, OIE, Census Data, and National Sources'),

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

    FaoGrowthRate = helpers.getGrowthRate(fao_data)
    print(FaoGrowthRate.head())

    FaoGrowthRate.sort_values(by=['growthRate'], inplace=True)

    # Build the plotly graph
    fig = px.histogram(
                FaoGrowthRate,
                x=FaoGrowthRate["year"],
                y=FaoGrowthRate["growthRate"],
                #color=master_df["source"],
                #markers=True)
    )
    #fig.update_yaxes(type='linear')

    # fig.update_layout(
    #     title=f"GrowthRate of the Population in for FAO",
    #     xaxis_title="Year",
    #     yaxis_title="Population",
    #     legend_title="Sources",
    # )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)