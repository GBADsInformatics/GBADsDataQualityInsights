# Census Data Qaulity Research
# Written By Ian McKechnie
# Last Updated: Tuesday Dec 20, 2022
import API_helpers.fao as fao
import API_helpers.oie as oie
import pandas as pd
from dash import Dash, html, dcc
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

country = countries[2]
specie = species[0]

# Step one: Get FAO data
if country == "USA":
    fao_data = fao.get_data("United%20States%20of%20America", specie)
else:
    fao_data = fao.get_data(country, specie)

fao_data = str2frame(fao_data, "fao")
fao_data['source'] = "fao"
fao_data = fao_data.drop(columns=['iso3', "country"])
fao_data = fao_data.replace('"','', regex=True)
fao_data.sort_values(by=['year'], inplace=True)

#print("fao data")
#print(fao_data.head())


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

#print("oie data")
#print(oie_data.head())

# Step 3: Get Census data
print("country is: '"+ country+ "'")
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


# Build a master dataframe
index_list = csv_data[(csv_data['species'] == "Cattle")].index.tolist()

master_df = pd.concat([fao_data, oie_data, csv_data.iloc[index_list]])

#Build a Plotly graph around the data
app = Dash(__name__)


#fig = px.line(fao_data, x="year", y="population", color="source")
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
app.layout = html.Div(children=[
    html.H1(children='Data Quality Comparison for FAO, OIE, Census Data, and National Sources'),

    dcc.Graph(
        id='example-graph',
        figure=fig
    ),
    dcc.Checklist(
        id="checklist",
        options=species,
        value=[specie],
        inline=True
    ),
])

if __name__ == '__main__':
    app.run_server(debug=True)