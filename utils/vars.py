# utils/vars.py

from utils.mongo import db

# Mongo collection
_vars = db["vars"]

# =====================
# SET VAR
# =====================
def set_var(key: str, value: str):
    _vars.update_one(
        {"_id": key},
        {"$set": {"value": value}},
        upsert=True
    )

# =====================
# GET VAR
# =====================
def get_var(key: str, default=None):
    data = _vars.find_one({"_id": key})
    if not data:
        return default
    return data.get("value")

# =====================
# DELETE VAR
# =====================
def del_var(key: str):
    _vars.delete_one({"_id": key})

# =====================
# LIST ALL VARS
# =====================
def all_vars():
    data = {}
    for x in _vars.find():
        data[x["_id"]] = x.get("value")
    return data