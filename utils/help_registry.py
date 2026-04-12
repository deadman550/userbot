_HELP = {}

def register_help(section, usage=None, description=None):
    """
    Supports:
    register_help(section, text)
    register_help(section, usage, description)
    """

    if description is None:
        # OLD STYLE: register_help(section, full_text)
        _HELP[section.lower()] = usage.strip()
    else:
        # NEW STYLE
        _HELP[section.lower()] = (
            f"{usage.strip()}\n\n{description.strip()}"
        )

def get_all_help():
    return _HELP
