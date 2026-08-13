"""
data.py — Gets real F1 race results from a free public API.

This is the ONLY file that talks to the internet for race data.
Everything else just calls the function below and gets back a
simple Python list.
"""

import requests

SEASON = 2025  # we only support the 2025 season, kept simple on purpose


def get_race_results(round_number: int) -> list:
    """
    Fetches real results for one race (identified by its round number
    in the 2025 season, e.g. round 4 = Bahrain).

    Returns a list of dictionaries, one per driver, like:
        {"driver": "Oscar Piastri", "position": 1}
    """
    url = f"https://api.jolpi.ca/ergast/f1/{SEASON}/{round_number}/results.json"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    races = data["MRData"]["RaceTable"]["Races"]
    if not races:
        return []

    results = races[0]["Results"]
    return [
        {
            "driver": f"{r['Driver']['givenName']} {r['Driver']['familyName']}",
            "position": int(r["position"]),
        }
        for r in results
    ]


def get_season_schedule() -> list:
    """
    Fetches the real list of every 2025 race, so we can match a race
    NAME (like "Bahrain Grand Prix") to its round number.
    """
    url = f"https://api.jolpi.ca/ergast/f1/{SEASON}.json"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    races = data["MRData"]["RaceTable"]["Races"]
    return [
        {"round": int(r["round"]), "name": r["raceName"]}
        for r in races
    ]
