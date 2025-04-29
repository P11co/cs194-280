# ./src/mindmates/utils/models.py

from pydantic import BaseModel, Field
from typing import Optional

class TherapyOutput(BaseModel):
    final_response: str = Field(description="The final text response for the user.")
    suggested_reaction: Optional[str] = Field(description="The suggested single emoji character or 'None'.")

class CalendarEvent(BaseModel):
    time: str = Field(description="Time of the event")
    schedule: str = Field(description="A brief description of the event")
    feedback: str = Field(description="A brief description of the when to remind the user, or [Empty]")