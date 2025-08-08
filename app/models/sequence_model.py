from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from app.models.persona_model import Persona


class IdeasOutput(BaseModel):
    """Output model for generated outreach ideas."""
    ideas: List[str] = Field(..., description="A list of generated outreach ideas based on persona data.")



class MessageContent(BaseModel):
    subject: Optional[str] = Field(None, description="The subject line for an email message.")
    body: str = Field(..., description="The main content of the message.")

class MessageOutput(BaseModel):
    messages: List[MessageContent] = Field(..., description="A list of generated messages.")

class OutreachChannel(str, Enum):
    EMAIL = "email"
    LINKEDIN = "linkedin"
    USE_BOTH = "useboth"


class CampaignRequest(BaseModel):
    persona: Persona
    outreach_channel: OutreachChannel = Field(..., description="The chosen outreach channel.")

class CampaignResponse(BaseModel):
    message: str = Field(..., description="Confirmation message.")
    campaign_details: dict = Field(..., description="Details of the created campaign.")
    # This field will now hold the generated content
    generated_content: Union[List[MessageContent], Dict[str, List[MessageContent]],None] = None