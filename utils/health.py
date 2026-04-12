import time
from utils.mongo import mongo, db, check_mongo_health

START_TIME = time.time()

# =====================
# UPTIME
# =====================
def get_uptime():
    seconds = int(time.time() - START_TIME)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h}h {m}m {s}s"

# =====================
# MONGO STATUS
# =====================
def mongo_status():
    info = check_mongo_health()
    if not info["ok"]:
        return "❌ Disconnected"

    try:
        stats = db.command("dbstats")
        size_mb = round(stats.get("dataSize", 0) / (1024 * 1024), 2)
        collections = stats.get("collections", 0)

        return (
            "✅ Connected\n"
            f"• DB Size: {size_mb} MB\n"
            f"• Collections: {collections}"
        )
    except Exception:
        return "✅ Connected (stats unavailable)"
