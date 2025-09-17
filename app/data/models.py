from pydantic import BaseModel
from typing import List, Optional

class Event(BaseModel):
    id: str
    name: str
    description: str = ""
    rewards: Optional[List[str]] = None
    rewards_text: Optional[str] = None
    bonus: Optional[str] = None
    tips: Optional[List[str]] = None
    tips_text: Optional[str] = None
    duration: Optional[str] = None
    extra_time_text: Optional[str] = None
    has_rules: bool = False
    rules_text: Optional[str] = None
    season: Optional[str] = None
