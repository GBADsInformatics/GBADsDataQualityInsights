# Census Data Qaulity Research
# Written By Ian McKechnie
# Last Updated: Tuesday Dec 20, 2022
import API_helpers.fao as fao
import API_helpers.oie as oie
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

def str2frame(estr, source, sep = ',', lineterm = '\n'):
    dat = [x.split(sep) for x in estr.split(lineterm)][1:-1]
    if source == "fao":
        df = pd.DataFrame(dat, columns=['iso3', "country", 'year', 'species', 'population'] )
    elif source == "oie":
        df = pd.DataFrame(dat, columns=["country", 'year', 'species', 'population', "source"] )
    return df

countries = ["Ethiopia", "Canada", "USA", "Ireland", "India", "Brazil", "Botswana", "Egypt", "South Africa", "Indonesia", "China", "Australia", "NewZealand", "Japan", "Mexico", "Argentina", "Chile"]
species = ["Cattle","Sheep","Goats","Pigs","Chickens"]

country = countries[1]
specie = species[0]


#Build a Plotly graph around the data
app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Data Quality Comparison for FAO, OIE, Census Data, and National Sources'),

    dcc.Graph(id='graph'),
    #dcc.Checklist(
    #    id="checklist",
    #    options=species,
    #    value=[specie],
    #),
    dcc.Checklist(
        species,
        value=[species[0]],
        id="checklist",)

])

@app.callback(
    Output("graph", "figure"), 
    Input("checklist", "value"))
def update_line_chart(specie):
    # Step one: Get FAO data
    countries = ["Ethiopia", "Canada", "USA", "Ireland", "India", "Brazil", "Botswana", "Egypt", "South Africa", "Indonesia", "China", "Australia", "NewZealand", "Japan", "Mexico", "Argentina", "Chile"]
    species = ["Cattle","Sheep","Goats","Pigs","Chickens", "Horses", "Ostrichs", "Asses and Mules", "Bees", "Elk", "Rabbits", "Mink", "Deer", "Turkeys"]

    country = countries[1]

    if specie == None:
        specie = species[0]
    else:
        specie = specie[0]

    print(specie)

    if country == "USA":
        fao_data = fao.get_data("United%20States%20of%20America", specie)
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
        csv_data = pd.read_csv(f"censusData/{country}.csv")\

    except:
        try:
            csv_data = pd.read_csv("censusData/Ethiopia.csv")
        except:
            print("Error, count not find the correct csv file")

    #species.append(csv_data["species"].tolist()) 
    species = species + csv_data["species"].tolist() # Add the species from the csv file to the list of species
    species = list(dict.fromkeys(species))  # Remove duplicates from the list of species

    #csv_data['source'] = "census"

    # Step 4: Get National data
    try:
        nationalData = pd.read_csv(f"nationalData/{country}.csv")\

    except:
        try:
            nationalData = pd.read_csv("censusData/Ethiopia.csv")
        except:
            print("Error, count not find the correct csv file")


    # Build a master dataframe
    csv_index_list = csv_data[(csv_data['species'] == specie)].index.tolist()
    nationalData_index_list = nationalData[(nationalData['species'] == specie)].index.tolist()

    master_df = pd.concat([fao_data, oie_data, csv_data.iloc[csv_index_list], nationalData.iloc[nationalData_index_list]])

    fig = px.line(oie_data,
                x=master_df["year"],
                y=master_df["population"],
                color=master_df["source"],
                markers=True)
    fig.update_yaxes(type='linear')

    fig.update_layout(
        title=f"Population of {specie} in {country}",
        xaxis_title="Year",
        yaxis_title="Population",
        legend_title="Sources",
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)