import requests
from API_helpers.helperFunctions import str2frame

def get_data(country, species):
    url = f"http://gbadske.org:9000/GBADsLivestockPopulation/oie?year=*&country={country}&species={species}&format=file"
    response = requests.get(url)
    return response.text

def formatOIEData(oie_data):
    oie_data = str2frame(oie_data, "oie")
    oie_data['source'] = "oie"
    oie_data = oie_data.drop(columns=['country'])
    oie_data = oie_data.replace('"','', regex=True)
    oie_data.sort_values(by=['year'], inplace=True)

    return oie_data