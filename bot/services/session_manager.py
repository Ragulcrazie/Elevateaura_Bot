import json
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

SESSION_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/quiz_sessions.json"))
os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)

class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.load_from_disk()

    def load_from_disk(self):
        """Loads sessions from the JSON file."""
        print(f"DEBUG: Loading sessions from {SESSION_FILE}")
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, "r", encoding="utf-8") as f:
                    self.sessions = json.load(f)
                print(f"DEBUG: Loaded {len(self.sessions)} sessions from disk.")
            except Exception as e:
                print(f"DEBUG: Failed to load sessions: {e}")
                self.sessions = {}
        else:
            print("DEBUG: Session file does not exist (yet).")
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
        """Retrieves a user session. Reloads from disk if missing in memory."""
        print(f"DEBUG: Getting session for {user_id} (Type: {type(user_id)})")
        
        # Try Memory
        if str(user_id) in self.sessions:
            print("DEBUG: Found in memory cache")
            return self.sessions.get(str(user_id))
        
        # Try Disk Reload (In case another process updated it or cold start)
        print("DEBUG: Cache miss. Reloading from disk...")
        self.load_from_disk()
        
        if str(user_id) in self.sessions:
            print("DEBUG: Found after reload.")
            return self.sessions.get(str(user_id))
            
        print(f"DEBUG: Session definitely not found. Keys: {list(self.sessions.keys())}")
        return None

    def delete_session(self, user_id: int):
        """Deletes a user session."""
        if str(user_id) in self.sessions:
            del self.sessions[str(user_id)]
            self.save_to_disk()

# Singleton Instance
session_manager = SessionManager()
