# utils/shop_helper.py

ITEMS = {

    # =====================
    # COMMON ITEMS (BATTLE)
    # =====================
    "wood_sword": {
        "name": "🪵 Wood Sword",
        "price": 50,
        "rarity": "common",
        "attack": 5,
        "defense": 0,
        "hp": 0,
        "consumable": False,
        "category": "battle"
    },

    "iron_sword": {
        "name": "⚔️ Iron Sword",
        "price": 120,
        "rarity": "common",
        "attack": 10,
        "defense": 0,
        "hp": 0,
        "consumable": False,
        "category": "battle"
    },

    "iron_shield": {
        "name": "🛡 Iron Shield",
        "price": 80,
        "rarity": "common",
        "attack": 0,
        "defense": 8,
        "hp": 0,
        "consumable": False,
        "category": "battle"
    },

    # =====================
    # RARE ITEMS (BATTLE)
    # =====================
    "steel_sword": {
        "name": "🗡 Steel Sword",
        "price": 200,
        "rarity": "rare",
        "attack": 15,
        "defense": 2,
        "hp": 0,
        "consumable": False,
        "category": "battle"
    },

    "golden_armor": {
        "name": "🥋 Golden Armor",
        "price": 220,
        "rarity": "rare",
        "attack": 0,
        "defense": 15,
        "hp": 10,
        "consumable": False,
        "category": "battle"
    },

    # =====================
    # LEGENDARY ITEMS (BATTLE)
    # =====================
    "diamond_sword": {
        "name": "💎 Diamond Sword",
        "price": 400,
        "rarity": "legendary",
        "attack": 25,
        "defense": 5,
        "hp": 0,
        "consumable": False,
        "category": "battle"
    },

    "dragon_blade": {
        "name": "🐉 Dragon Blade",
        "price": 600,
        "rarity": "legendary",
        "attack": 35,
        "defense": 10,
        "hp": 0,
        "consumable": False,
        "category": "battle"
    },

    # =====================
    # CONSUMABLES (BATTLE)
    # =====================
    "health_potion": {
        "name": "🧪 Health Potion",
        "price": 30,
        "rarity": "common",
        "attack": 0,
        "defense": 0,
        "hp": 30,
        "consumable": True,
        "category": "battle"
    },

    "mega_potion": {
        "name": "💊 Mega Potion",
        "price": 80,
        "rarity": "rare",
        "attack": 0,
        "defense": 0,
        "hp": 70,
        "consumable": True,
        "category": "battle"
    },

    # =====================
    # MINIGAMES ITEMS
    # =====================
    "double_coin": {
        "name": "💰 Double Coin Boost",
        "price": 100,
        "rarity": "rare",
        "attack": 0,
        "defense": 0,
        "hp": 0,
        "consumable": True,
        "category": "minigame"
    },

    "luck_boost": {
        "name": "🍀 Luck Boost",
        "price": 80,
        "rarity": "rare",
        "attack": 0,
        "defense": 0,
        "hp": 0,
        "consumable": True,
        "category": "minigame"
    },

    # =====================
    # ABILITY ITEMS
    # =====================
    "shield": {
        "name": "🛡 Shield",
        "price": 60,
        "rarity": "common",
        "attack": 0,
        "defense": 0,
        "hp": 0,
        "consumable": True,
        "category": "minigame",
        "ability": {
            "ignore_mistake": 1
        },
        "desc": "Ignore 1 wrong answer or bomb blast"
    },

    "lucky_charm": {
        "name": "🍀 Lucky Charm",
        "price": 90,
        "rarity": "rare",
        "attack": 0,
        "defense": 0,
        "hp": 0,
        "consumable": True,
        "category": "minigame",
        "ability": {
            "hint": True,
            "range_reduce": 0.25
        },
        "desc": "Small hint in Guess / Roulette"
    },

    "speed_boost": {
        "name": "⚡ Speed Boost",
        "price": 120,
        "rarity": "rare",
        "attack": 0,
        "defense": 0,
        "hp": 0,
        "consumable": True,
        "category": "minigame",
        "ability": {
            "reaction_bonus": 0.5
        },
        "desc": "Faster reaction in TypeFast / React"
    },

    "bomb_defuser": {
        "name": "🧯 Bomb Defuser",
        "price": 70,
        "rarity": "common",
        "attack": 0,
        "defense": 0,
        "hp": 0,
        "consumable": True,
        "category": "minigame",
        "ability": {
            "defuse_bomb": 1
        },
        "desc": "Survive one bomb explosion"
    },

    "vip": {
        "name": "👑 VIP Pass",
        "price": 250,
        "rarity": "legendary",
        "attack": 0,
        "defense": 0,
        "hp": 0,
        "consumable": False,
        "category": "minigame",
        "ability": {
            "coin_bonus": 5,
            "highlight": True
        },
        "desc": "Extra coins + VIP highlight"
    }
}
