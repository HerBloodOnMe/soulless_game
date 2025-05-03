import requests

class Stats:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_playtime(self, game_id, steam_id):
        # Use the GetOwnedGames API to fetch playtime
        url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
        params = {
            "key": self.api_key,
            "steamid": steam_id,
            "include_appinfo": False,
            "include_played_free_games": True
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if "response" in data and "games" in data["response"]:
                for game in data["response"]["games"]:
                    if game["appid"] == game_id:
                        # Playtime is returned in minutes; convert to hours
                        return round(game.get("playtime_forever", 0) / 60, 2)
        return 0

    def get_achievements(self, game_id, steam_id):
        # Use the GetPlayerAchievements API to fetch achievements
        url = f"https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/"
        params = {
            "key": self.api_key,
            "steamid": steam_id,
            "appid": game_id
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if "playerstats" in data and "achievements" in data["playerstats"]:
                achievements = data["playerstats"]["achievements"]
                completed = sum(1 for a in achievements if a.get("achieved", 0) == 1)
                total = len(achievements)
                return completed, total
        return 0, 0