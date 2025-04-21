# Example location: src/mindmates/utils/models.py

from pydantic import BaseModel, Field
from typing import Optional

class TherapyOutput(BaseModel):
    final_response: str = Field(description="The final text response for the user.")
    suggested_reaction: Optional[str] = Field(description="The suggested single emoji character or 'None'.")
