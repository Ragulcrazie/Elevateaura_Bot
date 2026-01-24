import json
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

SESSION_FILE = "quiz_sessions.json"

class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.load_from_disk()

    def load_from_disk(self):
        """Loads sessions from the JSON file."""
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, "r", encoding="utf-8") as f:
                    self.sessions = json.load(f)
                logger.info(f"Loaded {len(self.sessions)} sessions from disk.")
            except Exception as e:
                logger.error(f"Failed to load sessions: {e}")
                self.sessions = {}
        else:
            self.sessions = {}

    def save_to_disk(self):
        """Saves current sessions to the JSON file."""
        try:
            with open(SESSION_FILE, "w", encoding="utf-8") as f:
                json.dump(self.sessions, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save sessions: {e}")

    def save_session(self, user_id: int, data: Dict[str, Any]):
        """Updates and saves a user session."""
        self.sessions[str(user_id)] = data
        self.save_to_disk()

    def get_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a user session."""
        return self.sessions.get(str(user_id))

    def delete_session(self, user_id: int):
        """Deletes a user session."""
        if str(user_id) in self.sessions:
            del self.sessions[str(user_id)]
            self.save_to_disk()

# Singleton Instance
session_manager = SessionManager()
