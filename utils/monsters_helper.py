import random

MONSTERS = {
    "Dragon": {"atk": 20, "def": 15, "rarity": "legendary"},
    "Wolf": {"atk": 10, "def": 8, "rarity": "common"},
    "Golem": {"atk": 15, "def": 20, "rarity": "rare"},
}

def summon():
    roll = random.random()
    if roll < 0.6:
        pool = [m for m in MONSTERS if MONSTERS[m]["rarity"] == "common"]
    elif roll < 0.9:
        pool = [m for m in MONSTERS if MONSTERS[m]["rarity"] == "rare"]
    else:
        pool = [m for m in MONSTERS if MONSTERS[m]["rarity"] == "legendary"]

    name = random.choice(pool)
    return name, MONSTERS[name]
