import requests


def get_data(country, species):
    url = f"http://gbadske.org:9000/GBADsLivestockPopulation/oie?year=*&country={country}&species={species}&format=file"
    print(url)
    response = requests.get(url)
    return response.text 