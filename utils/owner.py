import os

OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

def is_owner(e):
    if not OWNER_ID:
        return False
    return e.sender_id == OWNER_ID
