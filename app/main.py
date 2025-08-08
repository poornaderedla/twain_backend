from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Models
from app.models.persona_model import Persona
from app.models.sequence_model import (
    CampaignRequest,
    CampaignResponse,
    IdeasOutput,
    OutreachChannel
)

# Controllers
from app.controllers.persona_controller import persona_scraper
from app.controllers.content_controllers import (
    generate_email_content,
    generate_linkedin_content
)
from app.controllers.idea_controller import generate_ideas

app = FastAPI()

class PersonaRequest(BaseModel):
    url: str
    description:str

    
@app.post("/persona", response_model=Persona)
def create_persona(request: PersonaRequest):
    try:
        # Log the incoming request data
        print(f"Received request - URL: {request.url}, Description length: {len(request.description)}")
        
        # Validate URL format
        if not request.url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
            
        # Validate description
        if not request.description.strip():
            raise ValueError("Description cannot be empty")
            
        persona = persona_scraper(request.url, request.description)
        return persona
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
      
@app.post("/ideas", response_model=IdeasOutput)
def get_ideas(persona_data: Persona):
    """
    Generates and returns a list of outreach ideas based on the provided persona data.
    """
    try:
        ideas = generate_ideas(persona_data)
        return ideas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate ideas: {e}")
  
  
  
  
  
@app.post("/create_campaign", response_model=CampaignResponse)
def create_campaign(request: CampaignRequest):
    """
    Creates a new outreach campaign, generating content based on the chosen channel.
    """
    channel = request.outreach_channel
    persona = request.persona
    
    campaign_details = {
        "outreach_channel": channel,
        "persona_title": persona.title,
    }
    
    generated_content = None
    
    if channel == OutreachChannel.EMAIL:
        email_output = generate_email_content(persona)
        generated_content = email_output.messages
        campaign_details["message"] = "Email campaign created."
    elif channel == OutreachChannel.LINKEDIN:
        linkedin_output = generate_linkedin_content(persona)
        generated_content = linkedin_output.messages
        campaign_details["message"] = "LinkedIn campaign created."
    elif channel == OutreachChannel.USE_BOTH:
        email_output = generate_email_content(persona)
        linkedin_output = generate_linkedin_content(persona)
        generated_content = {
            "email": email_output.messages,
            "linkedin": linkedin_output.messages
        }
        campaign_details["message"] = "Multi-channel campaign created."
    else:
        raise HTTPException(status_code=400, detail="Invalid outreach channel selected.")

    if not generated_content:
        raise HTTPException(status_code=500, detail="Failed to generate any campaign content.")

    return CampaignResponse(
        message=f"Campaign successfully created for '{channel}' channel.",
        campaign_details=campaign_details,
        generated_content=generated_content
    )
