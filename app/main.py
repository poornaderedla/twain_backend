import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.models.persona_scraper import persona_scraper
from app.models.persona_model import Persona
app = FastAPI()

class PersonaRequest(BaseModel):
    url: str
    description:str

    
@app.post("/persona", response_model=Persona)
def create_persona(request: PersonaRequest):
    try:
        persona = persona_scraper(request.url , request.description  )
        return persona
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
      
  