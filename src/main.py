# Census Data Qaulity Research
# Written By Ian McKechnie
# Last Updated: Tuesday Dec 20, 2022
import API_helpers.fao as fao
import API_helpers.oie as oie
import pandas as pd
from io import StringIO

def str2frame(estr, sep = ',', lineterm = '\n', set_header = True):
    dat = [x.split(sep) for x in estr.split(lineterm)][1:-1]
    df = pd.DataFrame(dat)
    if set_header:
        df = df.T.set_index(0, drop = True).T # flip, set ix, flip back
    return df

countries = ["Ethiopia", "Canada", "USA", "Ireland", "India", "Brazil", "Botswana", "Egypt", "South Africa", "Idndonisia", "China", "Australia", "New Zealand", "Japan", "Mexico", "Argentina", "Chile"]
species = ["Cattle","Sheep","Goats","Pigs","Chickens"]

country = countries[0]
specie = species[0]

# Step one: Get FAO data
fao_data = fao.get_data(country, specie)
fao_data = str2frame(fao_data)

# Step two: Get OIE data
oie_data = oie.get_data(country, specie)
oie_data = str2frame(oie_data)

# Step 3: Get Census data
csv_data = pd.read_csv(f"censusData/{country}.csv")
print(csv_data)

# Step 4: Get National data

#Build a Plotly graph around the data
