import json
import os

LEADERBOARD_DB = "utils/leaderboard.json"

# =====================
# LOAD / SAVE
# =====================
def load_lb():
    if not os.path.exists(LEADERBOARD_DB):
        return {}
    with open(LEADERBOARD_DB, "r") as f:
        return json.load(f)

def save_lb(db):
    with open(LEADERBOARD_DB, "w") as f:
        json.dump(db, f, indent=2)

# =====================
# ENSURE STRUCTURE
# =====================
def ensure_game(db, game):
    db.setdefault(game, {"players": {}})

def ensure_player(db, game, pid, name):
    ensure_game(db, game)
    db[game]["players"].setdefault(pid, {
        "name": name,
        "wins": 0,
        "losses": 0,
        "battles": 0
    })

# =====================
# RECORD MATCH
# =====================
def record_match(game, winner_id, winner_name, loser_id, loser_name):
    db = load_lb()

    ensure_player(db, game, winner_id, winner_name)
    ensure_player(db, game, loser_id, loser_name)

    db[game]["players"][winner_id]["wins"] += 1
    db[game]["players"][loser_id]["losses"] += 1

    db[game]["players"][winner_id]["battles"] += 1
    db[game]["players"][loser_id]["battles"] += 1

    save_lb(db)

# =====================
# GET MVP
# =====================
def get_mvp(game):
    db = load_lb()

    if game not in db or not db[game]["players"]:
        return None

    players = list(db[game]["players"].values())

    players.sort(
        key=lambda p: (
            p["wins"],
            -p["losses"],
            p["battles"]
        ),
        reverse=True
    )

    return players[0]
