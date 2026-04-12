# utils/mongo.py

import os
import time
from pymongo import MongoClient

# =====================
# CONFIG
# =====================
MONGO_URL = os.environ.get("MONGO_URL")

# ❗ crash mat karo, plugins khud handle karenge
mongo = None
db = None
settings = None
notes = None

if MONGO_URL:
    try:
        mongo = MongoClient(
            MONGO_URL,
            serverSelectionTimeoutMS=5000
        )

        db = mongo["userbot"]

        # common collections
        settings = db["settings"]
        notes = db["notes"]

    except Exception as e:
        mongo = None
        db = None
        settings = None
        notes = None
        print("❌ Mongo init failed:", e)
else:
    print("⚠️ MONGO_URL not set — Mongo features disabled")

# =====================
# HEALTH CHECK
# =====================
def check_mongo_health():
    if not mongo:
        return {
            "ok": False,
            "error": "Mongo not connected"
        }

    try:
        start = time.time()
        mongo.admin.command("ping")
        return {
            "ok": True,
            "db": db.name,
            "collection": "settings / notes / others",
            "time": f"{round(time.time() - start, 2)}s"
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }
