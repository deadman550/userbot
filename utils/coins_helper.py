import json
import os

DB = "utils/coins.json"

def load():
    if not os.path.exists(DB):
        return {"users": {}}
    with open(DB, "r") as f:
        return json.load(f)

def save(db):
    with open(DB, "w") as f:
        json.dump(db, f, indent=2)

def add_coin(uid, name, amt):
    db = load()
    u = db["users"].setdefault(str(uid), {"name": name, "coins": 0})
    u["coins"] += amt
    save(db)

def get_coins(uid):
    db = load()
    return db["users"].get(str(uid), {}).get("coins", 0)

def spend(uid, amt):
    db = load()
    u = db["users"].get(str(uid))
    if not u or u["coins"] < amt:
        return False
    u["coins"] -= amt
    save(db)
    return True
