import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "paperpal_db"

# Initialize motor async client
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Collections
users_collection = db["users"]
documents_collection = db["documents"]
chats_collection = db["chats"]

async def check_db_connection():
    """Verify that we can connect to the database."""
    try:
        # Trigger a simple command to check server status
        await client.admin.command('ping')
        return True
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return False
