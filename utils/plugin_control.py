import json
import os

FILE = "data/plugins_state.json"

def _load():
    if not os.path.exists(FILE):
        return {}
    with open(FILE, "r") as f:
        return json.load(f)

def is_enabled(name: str) -> bool:
    return _load().get(name, True)

def is_disabled(name: str) -> bool:
    return not is_enabled(name)

def enable(name: str):
    d = _load()
    d[name] = True
    with open(FILE, "w") as f:
        json.dump(d, f, indent=2)

def disable(name: str):
    d = _load()
    d[name] = False
    with open(FILE, "w") as f:
        json.dump(d, f, indent=2)
