import requests
import json

class MakeApiCall:
    def __init__(self, url, params):
        self.url = url
        self.params = params

    def get(self):
        response = requests.get(self.url, params=self.params)
        return response.json()