import requests

class Library:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_games(self, steam_id):
        url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
        params = {
            "key": self.api_key,
            "steamid": steam_id,
            "include_appinfo": True,
            "include_played_free_games": True
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if "response" in data and "games" in data["response"]:
                # Map the API response to include 'id' and 'name'
                games = [
                    {
                        "id": game["appid"],
                        "name": game.get("name", "Unknown"),
                        "img_logo_url": game.get("img_logo_url", "")
                    }
                    for game in data["response"]["games"]
                ]
                return games
        return []

    def get_game_details(self, game_id):
        # This method should retrieve details for a specific game using the Steam API
        # For demonstration purposes, we'll return a mock game detail
        return {
            "id": game_id,
            "name": "Mock Game",
            "img_logo_url": "mock_logo_url"
        }