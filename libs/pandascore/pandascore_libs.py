import requests
from libs.config import Config
import json
import datetime

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
    print(f"Zaktualizowane dane zapisano w: {pandascore_data_path}")


def get_all_match_dict():
    match_dict = dict()
    get_tournment_data()

    with open(pandascore_data_path, 'r') as json_file:
        data = json.load(json_file)
    for ttr in data:
        for match in ttr['matches']:
            match_id, match_name = match['id'], match["name"]
            match_status = match["status"]
            if match["begin_at"] is not None:
                match_begin_at = datetime.datetime.strptime(
                    match["begin_at"], "%Y-%m-%dT%H:%M:%SZ"
                )
            match_dict.update({
                match_id: [
                    match_name,
                    match_status,
                    match_begin_at
                ]
            })

    return match_dict


def get_active_match_dict():
    active_match_dict = dict()
    get_tournment_data()

    with open(pandascore_data_path, 'r') as json_file:
        data = json.load(json_file)
    for ttr in data:
        for match in ttr['matches']:
            if match["status"] == "not_started":
                match_status = match["status"]
                match_id, match_name = match['id'], match["name"]

                if match["begin_at"] is not None:
                    match_begin_at = datetime.datetime.strptime(
                        match["begin_at"], "%Y-%m-%dT%H:%M:%SZ"
                    )

                active_match_dict.update({
                    match_id: [
                        match_name,
                        match_status,
                        match_begin_at
                    ]
                })

    return active_match_dict
