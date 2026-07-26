# Global settings and database connection handles package initialiser

from .settings import settings
from .database import (
    db,
    users_collection,
    documents_collection,
    chat_history_collection,
    quiz_history_collection,
    notes_history_collection,
    check_db_connection
)
