from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    user_id: int
    username: Optional[str]
    full_name: str
    subscription_status: str = "free"
    subscription_expiry: Optional[datetime] = None
    current_streak: int = 0
    language_pref: Optional[str] = "en"
    exam_category: Optional[str] = None

class GhostProfile(BaseModel):
    id: str
    name: str
    base_skill_level: int
    consistency_factor: float

class QuizResult(BaseModel):
    quiz_id: str
    user_id: int
    score: int
    time_taken_seconds: int
    submitted_at: datetime = datetime.now()
