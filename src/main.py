import os
import random
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
import webbrowser
from steam_api.library import Library
from steam_api.stats import Stats
from dotenv import load_dotenv

def get_user_input():
    # Load credentials from the .env file in the "auth" folder
    load_dotenv(os.path.join("auth", ".env"))
    api_key = os.getenv("STEAM_API_KEY")
    user_id = os.getenv("STEAM_USER_ID")

    if api_key and user_id:
        return api_key, user_id

    # If not found, prompt the user for input
    input_window = tk.Tk()
    input_window.title("Steam API Credentials")
    input_window.geometry("400x300")
    input_window.configure(bg="#1e1e1e")
    input_window.resizable(False, False)

    ttk.Label(input_window, text="Enter your Steam API Key:", background="#1e1e1e", foreground="white").pack(pady=10)
    api_key_entry = ttk.Entry(input_window, width=40)
    api_key_entry.pack(pady=5)

    # Add button for Steam API Key link directly under the input field
    def open_apikey_link():
        webbrowser.open("https://steamcommunity.com/dev/apikey")

    api_key_button = ttk.Button(input_window, text="Get your Steam API Key", command=open_apikey_link)
    api_key_button.pack(pady=5)

    ttk.Label(input_window, text="Enter your Steam User ID:", background="#1e1e1e", foreground="white").pack(pady=10)
    user_id_entry = ttk.Entry(input_window, width=40)
    user_id_entry.pack(pady=5)

    # Add button for Steam ID link directly under the input field
    def open_steamid_link():
        webbrowser.open("https://steamid.io/lookup")

    steam_id_button = ttk.Button(input_window, text="Find your Steam ID", command=open_steamid_link)
    steam_id_button.pack(pady=5)

    def submit():
        nonlocal api_key, user_id
        api_key = api_key_entry.get().strip()
        user_id = user_id_entry.get().strip()

        # Validate input fields
        if not api_key or not user_id:
            messagebox.showerror("Error", "Both Steam API Key and Steam User ID are required.")
            return

        # Validate that the Steam User ID contains only numbers
        if not user_id.isdigit():
            messagebox.showerror("Error", "Steam User ID must contain only numbers.")
            return

        # Test the API Key and User ID by making a request to the Steam API
        test_url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
        params = {
            "key": api_key,
            "steamid": user_id,
            "include_appinfo": False,
            "include_played_free_games": False
        }

        try:
            response = requests.get(test_url, params=params, timeout=5)
            if response.status_code != 200:
                raise Exception("Invalid API Key or Steam User ID.")
            data = response.json()
            if "response" not in data or "games" not in data["response"]:
                raise Exception("Invalid API Key or Steam User ID.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to validate API Key or Steam User ID: {e}")
            return

        # Save the credentials to the .env file
        os.makedirs("auth", exist_ok=True)
        with open(os.path.join("auth", ".env"), "w") as env_file:
            env_file.write(f"STEAM_API_KEY={api_key}\n")
            env_file.write(f"STEAM_USER_ID={user_id}\n")

        input_window.destroy()

    submit_button = ttk.Button(input_window, text="Submit", command=submit)
    submit_button.pack(pady=20)

    api_key, user_id = None, None
    input_window.mainloop()
    return api_key, user_id

def roll_game(library, stats, root, game_label, playtime_label, achievements_label, thumbnail_label, link_label, user_id):
    print("Rolling a game...")
    games = library.get_games(user_id)
    if not games:
        game_label.config(text="No games found in the library.")
        playtime_label.config(text="")
        achievements_label.config(text="")
        thumbnail_label.config(image="")
        link_label.config(text="", command=None)
        return

    selected_game = random.choice(games)
    if 'id' not in selected_game:
        game_label.config(text="Selected game does not have an 'id'.")
        playtime_label.config(text="")
        achievements_label.config(text="")
        thumbnail_label.config(image="")
        link_label.config(text="", command=None)
        return

    playtime = stats.get_playtime(selected_game['id'], user_id)
    completed_achievements, total_achievements = stats.get_achievements(selected_game['id'], user_id)

    game_label.config(text=f"Selected Game: {selected_game.get('name', 'Unknown')}")
    playtime_label.config(text=f"Playtime: {playtime} hours")
    achievements_label.config(text=f"Achievements: {completed_achievements}/{total_achievements}")

    img_logo_url = selected_game.get('img_logo_url', '')
    if img_logo_url:
        thumbnail_url = f"http://media.steampowered.com/steamcommunity/public/images/apps/{selected_game['id']}/{img_logo_url}.jpg"
        try:
            image = Image.open(requests.get(thumbnail_url, stream=True).raw)
            image = image.resize((150, 150))
            thumbnail = ImageTk.PhotoImage(image)
            thumbnail_label.config(image=thumbnail)
            thumbnail_label.image = thumbnail
        except Exception as e:
            print(f"Failed to load thumbnail: {e}")
            thumbnail_label.config(image="")
    else:
        thumbnail_label.config(image="")

    def open_game():
        webbrowser.open(f"steam://run/{selected_game['id']}")

    link_label.config(text="Open in Steam", command=open_game)

def main():
    api_key, user_id = get_user_input()
    library = Library(api_key)
    stats = Stats(api_key)

    games = library.get_games(user_id)
    if not games:
        print("No games found in your library. Please check your API key and Steam ID.")
        return

    root = tk.Tk()
    root.title("Steam Library Checker")
    root.geometry("500x600")
    root.configure(bg="#1e1e1e")
    root.resizable(False, False)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel", font=("Arial", 10), background="#1e1e1e", foreground="white")
    style.configure("TButton", font=("Arial", 10), background="#3a3a3a", foreground="white", padding=5)
    style.map("TButton", background=[("active", "#555555")])

    logo_label = ttk.Label(root, text="Soulless Projects", font=("Arial", 16, "bold"), anchor="center")
    logo_label.pack(pady=10)

    game_label = ttk.Label(root, text="Selected Game: ", anchor="center", font=("Arial", 12))
    game_label.pack(pady=10)

    playtime_label = ttk.Label(root, text="Playtime: ", anchor="center")
    playtime_label.pack(pady=5)

    achievements_label = ttk.Label(root, text="Achievements: ", anchor="center")
    achievements_label.pack(pady=5)

    thumbnail_label = ttk.Label(root)
    thumbnail_label.pack(pady=10)

    link_label = ttk.Button(root, text="", command=None)
    link_label.pack(pady=5)

    roll_button = ttk.Button(
        root,
        text="Roll Again",
        command=lambda: roll_game(library, stats, root, game_label, playtime_label, achievements_label, thumbnail_label, link_label, user_id)
    )
    roll_button.pack(pady=10)

    close_button = ttk.Button(root, text="Close", command=root.destroy)
    close_button.pack(pady=10)

    tooltip_label = ttk.Label(
        root,
        text="If the game is installed it'll launch the .exe, if not it'll prompt an install",
        font=("Arial", 8),
        background="#1e1e1e",
        foreground="white",
        anchor="center",
        wraplength=400
    )
    tooltip_label.pack(pady=5)

        # Add a "Join Discord for Support" button
    def open_discord_link():
        webbrowser.open("https://discord.gg/UvABbh4D8b")

    discord_button = ttk.Button(root, text="Join Discord for Support", command=open_discord_link)
    discord_button.pack(pady=10)

    footer_label = ttk.Label(root, text="Soulless Projects 2025", font=("Arial", 8), anchor="e")
    footer_label.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor="se")

    roll_game(library, stats, root, game_label, playtime_label, achievements_label, thumbnail_label, link_label, user_id)

    root.mainloop()

if __name__ == "__main__":
    main()