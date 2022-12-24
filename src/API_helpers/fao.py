import requests
import json


def get_fao_data(country, species):
    url = f"http://gbadske.org:9000/GBADsLivestockPopulation/faostat?year=*&country={country}&species={species}&format=file"
    print(url)
    response = requests.get(url)
    return response.text