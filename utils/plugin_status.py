PLUGIN_STATUS = {}

def mark_plugin_loaded(name):
    PLUGIN_STATUS[name] = {
        "status": "ok",
        "error": None
    }

def mark_plugin_error(name, error):
    PLUGIN_STATUS[name] = {
        "status": "error",
        "error": str(error)
    }

def get_broken_plugins():
    return {
        k: v for k, v in PLUGIN_STATUS.items()
        if v["status"] == "error"
    }

def all_ok():
    return all(v["status"] == "ok" for v in PLUGIN_STATUS.values())