import requests
from libs.config import Config
import json

pandascore_data_path = "libs/pandascore/pandascore_data.json"


def get_tournment_data():
    url = (
        f"https://api.pandascore.co/csgo/tournaments"
        f"?token={Config.PANDASCORE_ACCESS_TOKEN}"
    )
    response = requests.get(url)
    tournaments = str()

    if response.status_code == 200:
        tournaments = response.text

    with open(pandascore_data_path, 'w') as output_file:
        output_file.write(tournaments)


def structurize_data():
    with open(pandascore_data_path, 'r') as json_file:
        data = json.load(json_file)

    for ttr in data:
        print(ttr['name'])
        for match in ttr['matches']:
            print(match["name"], "#### Starts at", match["begin_at"])
