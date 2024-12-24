import json
import datetime
import requests
from typing import Dict, List, Optional
from libs.config import Config
import os

class PandascoreAPI:
    def __init__(self):
        self.base_url = Config.PANDASCORE_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {Config.PANDASCORE_TOKEN}",
            "Accept": "application/json"
        }

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Wykonuje zapytanie do API Pandascore"""
        url = f"{self.base_url}/{endpoint}"
        print(f"Wysyłanie zapytania do: {url}")
        print(f"Z parametrami: {params}")

        response = requests.get(url, headers=self.headers, params=params)
        print(f"Kod odpowiedzi: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Otrzymano dane: {len(data)} elementów")
            return data
        else:
            print(f"Treść błędu: {response.text}")
            raise Exception(f"Błąd API: {response.status_code} - {response.text}")

    def get_active_matches(self) -> Dict:
        """Pobiera aktywne mecze CS2"""
        print("Pobieranie aktywnych meczy...")
        params = {
            "filter[videogame]": "cs2",
            "filter[status]": "not_started",
            "sort": "begin_at",
            "per_page": 10
        }

        try:
            matches = self._make_request("matches", params)
            print(f"Pobrano {len(matches)} meczy")

            active_match_dict = {}
            for match in matches:
                match_id = match["id"]
                print(f"Przetwarzanie meczu {match_id}")

                teams = []
                if match.get("opponents"):
                    print(f"Znaleziono {len(match['opponents'])} drużyn")
                    for opponent in match["opponents"]:
                        if opponent.get("opponent"):
                            team_data = opponent["opponent"]
                            teams.append({
                                "name": team_data.get("name", "TBD"),
                                "id": team_data.get("id")
                            })

                active_match_dict[match_id] = {
                    "name": match["name"],
                    "status": match["status"],
                    "begin_at": datetime.datetime.strptime(
                        match["begin_at"], "%Y-%m-%dT%H:%M:%SZ"
                    ) if match["begin_at"] else None,
                    "teams": teams
                }

            print(f"Przetworzono {len(active_match_dict)} meczy")
            return active_match_dict

        except Exception as e:
            print(f"Wystąpił błąd w get_active_matches: {str(e)}")
            return {}

    def get_tournament_details(self, tournament_id: str) -> Dict:
        """Pobiera szczegóły turnieju"""
        try:
            tournament = self._make_request(f"tournaments/{tournament_id}")
            return {
                "success": True,
                "data": tournament
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def add_player_to_tournament(self, tournament_id: str, player_data: Dict) -> Dict:
        """Dodaje zawodnika do turnieju"""
        # Endpoint do dodawania zawodnika (przykład)
        endpoint = f"tournaments/{tournament_id}/players"

        try:
            # W rzeczywistym API mogłoby to być POST zamiast GET
            response = requests.post(
                f"{self.base_url}/{endpoint}",
                headers=self.headers,
                json=player_data
            )

            if response.status_code == 201:  # Created
                return {
                    "success": True,
                    "player_id": response.json()["id"],
                    "tournament_name": response.json()["tournament_name"]
                }
            else:
                return {
                    "success": False,
                    "error": f"Błąd API: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_tournament_roster(self, tournament_id: str) -> Dict:
        """Pobiera skład drużyn w turnieju, łącznie z lokalnie dodanymi zawodnikami"""
        try:
            # Najpierw sprawdzamy, czy podane ID to ID meczu
            url = f"{Config.PANDASCORE_BASE_URL}/matches/{tournament_id}"
            params = {
                "token": Config.PANDASCORE_TOKEN
            }

            print(f"Pobieranie informacji o meczu z: {url}")
            match_response = requests.get(url, params=params)
            print(f"Status odpowiedzi meczu: {match_response.status_code}")

            tournament_id_to_use = tournament_id
            if match_response.status_code == 200:
                match_data = match_response.json()
                if match_data.get("tournament"):
                    tournament_id_to_use = match_data["tournament"]["id"]
                    print(f"Znaleziono ID turnieju: {tournament_id_to_use}")

            roster_data = []

            # Popraw sposób wczytywania lokalnych danych
            if os.path.exists(LOCAL_DATA_FILE):
                with open(LOCAL_DATA_FILE, 'r', encoding='utf-8') as f:
                    local_data = json.load(f)
                    
                if str(tournament_id_to_use) in local_data:  # Dodaj konwersję na string
                    tournament_data = local_data[str(tournament_id_to_use)]
                    for team_name, team_players in tournament_data["teams"].items():
                        # Sprawdź czy drużyna już istnieje w roster_data
                        existing_team = next(
                            (t for t in roster_data if t["team_name"] == team_name),
                            None
                        )
                        
                        if existing_team:
                            # Dodaj lokalnych graczy do istniejącej drużyny
                            existing_team["players"].extend([
                                {
                                    "name": player["name"],
                                    "role": "N/A",
                                    "nationality": "N/A",
                                    "source": "Local",
                                    "added_at": player["added_at"]
                                }
                                for player in team_players
                            ])
                        else:
                            # Utwórz nową drużynę z lokalnymi graczami
                            roster_data.append({
                                "team_name": team_name,
                                "team_id": "LOCAL",
                                "status": "active",
                                "players": [
                                    {
                                        "name": player["name"],
                                        "role": "N/A",
                                        "nationality": "N/A",
                                        "source": "Local",
                                        "added_at": player["added_at"]
                                    }
                                    for player in team_players
                                ]
                            })

            # Następnie pobierz dane z API
            teams_url = f"{Config.PANDASCORE_BASE_URL}/tournaments/{tournament_id_to_use}/teams"
            print(f"Pobieranie drużyn z API: {teams_url}")

            teams_response = requests.get(teams_url, params=params)
            print(f"Status odpowiedzi drużyn: {teams_response.status_code}")

            if teams_response.status_code == 200:
                teams = teams_response.json()

                for team in teams:
                    team_name = team["name"]
                    print(f"Pobieranie zawodników dla drużyny {team_name} z API")

                    # Sprawdź, czy drużyna już istnieje w roster_data
                    existing_team = next(
                        (t for t in roster_data if t["team_name"] == team_name),
                        None
                    )

                    # Pobierz zawodników z API
                    players_url = f"{Config.PANDASCORE_BASE_URL}/teams/{team['id']}/players"
                    players_response = requests.get(players_url, params=params)
                    api_players = []

                    if players_response.status_code == 200:
                        api_players = [
                            {
                                "name": player["name"],
                                "role": player.get("role", "N/A"),
                                "nationality": player.get("nationality", "N/A"),
                                "source": "API"
                            }
                            for player in players_response.json()
                        ]

                    if existing_team:
                        # Dodaj graczy z API do istniejącej drużyny
                        existing_team["players"].extend(api_players)
                    else:
                        # Utwórz nową drużynę z graczami z API
                        roster_data.append({
                            "team_name": team_name,
                            "team_id": team["id"],
                            "status": team.get("status", "active"),
                            "players": api_players
                        })

            # Jeśli nie znaleźliśmy żadnych drużyn, spróbuj pobrać informacje z meczu
            if not roster_data and match_response.status_code == 200:
                for opponent in match_data.get("opponents", []):
                    if opponent.get("opponent"):
                        team = opponent["opponent"]
                        roster_data.append({
                            "team_name": team.get("name", "TBD"),
                            "team_id": team.get("id", "N/A"),
                            "status": "upcoming",
                            "players": []
                        })

            print(f"Końcowa liczba drużyn: {len(roster_data)}")
            for team in roster_data:
                print(f"Drużyna {team['team_name']}: {len(team['players'])} graczy")

            return {
                "success": True,
                "data": roster_data
            }

        except Exception as e:
            print(f"Wystąpił wyjątek: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return {
                "success": False,
                "error": str(e)
            }

# Inicjalizacja klasy API
api = PandascoreAPI()

# Ścieżka do pliku z lokalnymi danymi
LOCAL_DATA_FILE = "local_tournament_data.json"

def get_active_match_dict():
    """Pobiera aktywne mecze CS2 używając bezpośredniego linku API"""
    try:
        # Bezpośrednie użycie działającego URL
        url = f"{Config.PANDASCORE_BASE_URL}/csgo/matches"
        params = {
            "token": Config.PANDASCORE_TOKEN,
            "filter[status]": "not_started",
            "per_page": 10
        }

        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"Błąd API: {response.status_code}")
            return {}

        matches = response.json()
        active_match_dict = {}

        for match in matches:
            match_id = match["id"]
            match_name = match["name"]

            # Konwersja czasu rozpoczęcia
            match_begin_at = None
            if match["begin_at"]:
                match_begin_at = datetime.datetime.strptime(
                    match["begin_at"],
                    "%Y-%m-%dT%H:%M:%SZ"
                )

            # Pobieranie informacji o drużynach
            teams = []
            if match.get("opponents"):
                for opponent in match["opponents"]:
                    if opponent.get("opponent"):
                        team_data = opponent["opponent"]
                        teams.append({
                            "name": team_data.get("name", "TBD"),
                            "acronym": team_data.get("acronym", ""),
                            "image_url": team_data.get("image_url")
                        })

            # Dodawanie informacji o turnieju
            tournament_info = None
            if match.get("tournament"):
                tournament_info = {
                    "name": match["tournament"].get("name"),
                    "prizepool": match["tournament"].get("prizepool")
                }

            # Zapisywanie w słowniku
            active_match_dict[match_id] = [
                match_name,
                match["status"],
                match_begin_at,
                teams,
                tournament_info
            ]

        return active_match_dict

    except Exception as e:
        print(f"Błąd podczas pobierania danych: {str(e)}")
        return {}


def get_tournament_details(tournament_id: str):
    """Pobiera szczegóły turnieju na podstawie ID meczu lub ID turnieju"""
    try:
        # Najpierw spróbujmy pobrać informacje o meczu, aby znaleźć ID turnieju
        url = f"{Config.PANDASCORE_BASE_URL}/matches/{tournament_id}"
        params = {
            "token": Config.PANDASCORE_TOKEN
        }

        print(f"Pobieranie informacji o meczu z: {url}")  # Debug log
        match_response = requests.get(url, params=params)
        print(f"Status odpowiedzi meczu: {match_response.status_code}")  # Debug log

        tournament_id_to_use = tournament_id
        if match_response.status_code == 200:
            match_data = match_response.json()
            if match_data.get("tournament"):
                tournament_id_to_use = match_data["tournament"]["id"]
                print(f"Znaleziono ID turnieju: {tournament_id_to_use}")  # Debug log

        # Teraz pobieramy szczegóły turnieju
        tournament_url = f"{Config.PANDASCORE_BASE_URL}/tournaments/{tournament_id_to_use}"
        print(f"Pobieranie szczegółów turnieju z: {tournament_url}")  # Debug log

        tournament_response = requests.get(tournament_url, params=params)
        print(f"Status odpowiedzi turnieju: {tournament_response.status_code}")  # Debug log

        if tournament_response.status_code == 200:
            return {
                "success": True,
                "data": tournament_response.json()
            }
        else:
            print(f"Treść błędu: {tournament_response.text}")  # Debug log
            return {
                "success": False,
                "error": f"Błąd API: {tournament_response.status_code} - {tournament_response.text}"
            }

    except Exception as e:
        print(f"Wystąpił wyjątek: {str(e)}")  # Debug log
        return {
            "success": False,
            "error": str(e)
        }


def add_player_to_tournament(tournament_id: str, player_name: str, team_name: str):
    """Dodaje zawodnika do lokalnej bazy danych turnieju"""
    try:
        # Najpierw sprawdzamy, czy podane ID to ID meczu
        match_url = f"{Config.PANDASCORE_BASE_URL}/matches/{tournament_id}"
        params = {
            "token": Config.PANDASCORE_TOKEN
        }

        print(f"Sprawdzanie ID meczu: {match_url}")
        match_response = requests.get(match_url, params=params)

        tournament_id_to_use = tournament_id
        tournament_name = None

        # Jeśli to ID meczu, pobierz ID turnieju
        if match_response.status_code == 200:
            match_data = match_response.json()
            if match_data.get("tournament"):
                tournament_id_to_use = match_data["tournament"]["id"]
                tournament_name = match_data["tournament"].get("name")
                print(f"Znaleziono ID turnieju: {tournament_id_to_use}")

        # Jeśli nie mamy jeszcze nazwy turnieju, spróbuj pobrać dane turnieju
        if not tournament_name:
            tournament_url = f"{Config.PANDASCORE_BASE_URL}/tournaments/{tournament_id_to_use}"
            print(f"Pobieranie danych turnieju: {tournament_url}")
            tournament_response = requests.get(tournament_url, params=params)

            if tournament_response.status_code != 200:
                return {
                    "success": False,
                    "error": "Nie znaleziono turnieju o podanym ID"
                }

            tournament_data = tournament_response.json()
            tournament_name = tournament_data.get("name", "Unknown Tournament")

        # Wczytaj lub utwórz lokalną bazę danych
        local_data = {}
        if os.path.exists(LOCAL_DATA_FILE):
            with open(LOCAL_DATA_FILE, 'r', encoding='utf-8') as f:
                local_data = json.load(f)

        # Inicjalizuj strukturę danych dla turnieju jeśli nie istnieje
        if tournament_id_to_use not in local_data:
            local_data[tournament_id_to_use] = {
                "name": tournament_name,
                "teams": {}
            }

        # Dodaj drużynę jeśli nie istnieje
        if team_name not in local_data[tournament_id_to_use]["teams"]:
            local_data[tournament_id_to_use]["teams"][team_name] = []

        # Sprawdź czy zawodnik już istnieje w drużynie
        for player in local_data[tournament_id_to_use]["teams"][team_name]:
            if player["name"] == player_name:
                return {
                    "success": False,
                    "error": "Zawodnik już istnieje w tej drużynie"
                }

        # Dodaj zawodnika
        player_id = f"LOCAL_{len(local_data[tournament_id_to_use]['teams'][team_name]) + 1}"
        player_data = {
            "id": player_id,
            "name": player_name,
            "team": team_name,
            "added_at": datetime.datetime.now().isoformat()
        }

        local_data[tournament_id_to_use]["teams"][team_name].append(player_data)

        # Zapisz zmiany
        with open(LOCAL_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(local_data, f, indent=2, ensure_ascii=False)

        return {
            "success": True,
            "player_id": player_id,
            "tournament_name": tournament_name,
            "message": f"Dodano zawodnika {player_name} do drużyny {team_name} w turnieju {tournament_name}"
        }

    except Exception as e:
        print(f"Błąd podczas dodawania zawodnika: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def get_tournament_roster(tournament_id: str):
    return api.get_tournament_roster(tournament_id)

