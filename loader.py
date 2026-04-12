# loader.py
import os
import importlib
import traceback

from utils.plugin_control import is_enabled   # 👈 IMPORTANT

def load_plugins():
    for file in os.listdir("plugins"):
        if not file.endswith(".py"):
            continue
        if file.startswith("_"):
            continue
        if file == "__init__.py":
            continue

        plugin_name = file[:-3]   # e.g. api_search
        module = f"plugins.{plugin_name}"

        # 🔒 PLUGIN DISABLE CHECK
        if not is_enabled(plugin_name):
            print(f"⛔ Skipped disabled plugin: {plugin_name}")
            continue

        try:
            importlib.import_module(module)
            print(f"✔ {file} imported")
        except Exception:
            print(f"❌ Failed to load {file}")
            traceback.print_exc()
