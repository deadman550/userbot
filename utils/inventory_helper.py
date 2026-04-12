# utils/inventory_helper.py

def get_equipped(player):
    weapon = player.get("weapon")
    defense = player.get("defense")

    return {
        "weapon": weapon,
        "weapon_hp": player.get("weapon_hp", 0),
        "defense": defense,
        "defense_hp": player.get("defense_hp", 0)
    }

def damage_items(player, weapon_dmg=5, defense_dmg=5):
    if player.get("weapon"):
        player["weapon_hp"] = max(0, player.get("weapon_hp", 0) - weapon_dmg)

    if player.get("defense"):
        player["defense_hp"] = max(0, player.get("defense_hp", 0) - defense_dmg)

def repair_item(player, item, amount):
    if item == "weapon" and player.get("weapon"):
        player["weapon_hp"] = min(100, player.get("weapon_hp", 0) + amount)

    if item == "defense" and player.get("defense"):
        player["defense_hp"] = min(100, player.get("defense_hp", 0) + amount)
