from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class SocialProof(BaseModel):
    statement: str
    source: Optional[str] = None

class Persona(BaseModel):
    id: str = Field(default="scraped_lead", example="lead_123")
    name: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    pain_points: List[str] = []
    social_proof: List[SocialProof] = []
    cost_of_inaction: List[str] = []
    solutions : List[str] = []
    objections : List[str] = [] 
    competitive_advantages : List[str] = []
