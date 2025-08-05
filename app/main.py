
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.models.persona_model import Persona
from app.models.persona_scraper import scrape_persona_from_url

app = FastAPI()

class PersonaRequest(BaseModel):
    url: str
    description:str

@app.post("/persona", response_model=Persona)
def create_persona(request: PersonaRequest):
    try:
        persona = scrape_persona_from_url(request.url , request.description)
        return persona
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
