import requests
import pandas as pd

from API_helpers.helperFunctions import str2frame

def get_data(country, species):
    url = f"https://gbadske.org/api/GBADsLivestockPopulation/faostat?year=*&country={country}&species={species}&format=file"
    response = requests.get(url)
    return response.text

def formatFAOData(fao_data):
    fao_data = str2frame(fao_data, "fao")
    fao_data['source'] = "faostat"
    fao_data = fao_data.drop(columns=['iso3', "country"])
    fao_data = fao_data.replace('"','', regex=True)
    fao_data.sort_values(by=['year'], inplace=True)

    years = fao_data['year']
    fao_data['year'] = pd.to_numeric(years)

    return fao_data