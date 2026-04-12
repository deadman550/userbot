EXPLAIN_REGISTRY = {}

def register_explain(name: str, text: str):
    EXPLAIN_REGISTRY[name.lower()] = text

def get_explain(name: str):
    return EXPLAIN_REGISTRY.get(name.lower())

def get_all_explains():
    return EXPLAIN_REGISTRY
