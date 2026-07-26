from motor.motor_asyncio import AsyncIOMotorClient
from .settings import settings

# Initialize Motor (async driver for MongoDB) with settings values
client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.DB_NAME]

# Collections reference handles
users_collection = db["users"]
documents_collection = db["documents"]
chat_history_collection = db["chat_history"]
quiz_history_collection = db["quiz_history"]
notes_history_collection = db["notes_history"]

async def check_db_connection() -> bool:
    """
    Verifies database connectivity by pinging the admin database.
    Used during startup hooks.
    """
    try:
        await client.admin.command("ping")
        return True
    except Exception as e:
        print(f"[DB Error] Failed to ping MongoDB: {e}")
        return False
