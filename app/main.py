from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uuid

# Config
from app.config.config import settings

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

# Database
from app.database import connect_to_mongo, close_mongo_connection, get_database
from app.database.db_utils import insert_document, find_documents

app = FastAPI(title="TWAIN AI Backend", version="1.0.0")

# --- CORS Middleware (must be immediately after app creation) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/db-test")
async def test_database():
    """Test database connection and basic operations."""
    try:
        from app.database import get_database
        db = get_database()
        if db is None:
            return {"status": "error", "message": "Database not connected"}
        
        # Test a simple operation
        test_collection = db["test"]
        test_doc = {"test": "connection", "timestamp": datetime.utcnow()}
        result = await test_collection.insert_one(test_doc)
        
        # Clean up test document
        await test_collection.delete_one({"_id": result.inserted_id})
        
        return {
            "status": "success", 
            "message": "Database connection working",
            "database": settings.DATABASE_NAME,
            "collections": ["personas", "ideas", "campaigns"]
        }
    except Exception as e:
        return {"status": "error", "message": f"Database test failed: {str(e)}"}

@app.on_event("startup")
async def startup_db_client():
    """Initialize database connection on startup."""
    try:
        print(f"🔄 Connecting to MongoDB: {settings.DATABASE_NAME}")
        await connect_to_mongo()
        print(f"✅ Database connection established successfully!")
        
        # Test the connection with a simple operation
        from app.database import get_database
        db = get_database()
        if db is not None:
            print(f"✅ Database instance available: {db.name}")
        else:
            print("❌ WARNING: Database instance not available after connection")
            
    except Exception as e:
        print(f"❌ CRITICAL: Failed to connect to database: {e}")
        print(f"Database URL: {settings.MONGO_URL}")
        print(f"Database Name: {settings.DATABASE_NAME}")
        raise

@app.on_event("shutdown")
async def shutdown_db_client():
    """Close database connection on shutdown."""
    await close_mongo_connection()
    print("Database connection closed.")

class PersonaRequest(BaseModel):
    url: str
    description: str

@app.post("/persona", response_model=Persona)
async def create_persona(request: PersonaRequest):
    print(f"[POST /persona] Received: url={request.url}, description={request.description}")
    try:
        # Log the incoming request data
        print(f"Received persona request - URL: {request.url}, Description: {request.description}")
        
        # Validate URL format
        if not request.url.startswith(('http://', 'https://')):
            print(f"❌ Invalid URL format: {request.url}")
            raise ValueError("URL must start with http:// or https://")
            
        # Validate description
        if not request.description.strip():
            print(f"❌ Empty description provided")
            raise ValueError("Description cannot be empty")
        
        print(f"✅ URL and description validation passed")
            
        # Generate persona data
        print(f"🔄 Calling persona_scraper...")
        persona = persona_scraper(request.url, request.description)
        print(f"✅ Persona generated successfully: {persona}")
        
        # Prepare document for MongoDB (only use fields that exist in Persona model)
        # Convert SocialProof objects to dictionaries for MongoDB serialization
        social_proof_list = getattr(persona, 'social_proof', [])
        social_proof_dicts = []
        for proof in social_proof_list:
            if hasattr(proof, 'statement') and hasattr(proof, 'source'):
                social_proof_dicts.append({
                    "statement": proof.statement,
                    "source": proof.source
                })
            elif isinstance(proof, dict):
                social_proof_dicts.append(proof)
            else:
                # Fallback: convert to string
                social_proof_dicts.append({"statement": str(proof), "source": None})
        
        persona_doc = {
            "id": getattr(persona, 'id', str(uuid.uuid4())),  # Add the required id field
            "url": request.url,
            "description": request.description,
            "title": getattr(persona, 'title', None),
            "company": getattr(persona, 'company', None),
            "name": getattr(persona, 'name', None),
            "email": getattr(persona, 'email', None),
            "pain_points": getattr(persona, 'pain_points', []),
            "social_proof": social_proof_dicts,
            "cost_of_inaction": getattr(persona, 'cost_of_inaction', []),
            "solutions": getattr(persona, 'solutions', []),
            "objections": getattr(persona, 'objections', []),
            "competitive_advantages": getattr(persona, 'competitive_advantages', []),
            "created_at": datetime.utcnow(),
            "persona_id": str(uuid.uuid4())
        }
        
        print(f"Prepared persona document: {persona_doc}")
        
        # Save to MongoDB with better error handling
        try:
            from app.database import get_database
            db = get_database()
            if db is None:
                print("ERROR: Database not connected! Cannot save persona.")
                raise Exception("Database connection not available")
            
            persona_id = await insert_document("persona", persona_doc)
            print(f"✅ Persona successfully saved to MongoDB with ID: {persona_id}")
            persona_doc["_id"] = persona_id
            
        except Exception as db_error:
            print(f"❌ CRITICAL ERROR: Failed to save persona to database: {db_error}")
            print(f"Database error details: {type(db_error).__name__}: {str(db_error)}")
            # Don't continue silently - raise the error so we know about it
            raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
        
        print(f"✅ Returning persona to frontend: {persona}")
        return persona
    except Exception as e:
        print(f"❌ Error processing persona request: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        if "Database error" in str(e):
            raise e  # Re-raise database errors
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/ideas", response_model=IdeasOutput)
async def get_ideas(persona_data: Persona):
    """
    Generates and returns a list of outreach ideas based on the provided persona data.
    """
    try:
        print(f"Received ideas request for persona: {persona_data.company} - {persona_data.name}")
        ideas = generate_ideas(persona_data)
        print(f"Generated ideas: {ideas}")
        
        # Save ideas to MongoDB with better error handling
        ideas_doc = {
            "persona_title": persona_data.title,
            "persona_company": persona_data.company,
            "persona_name": persona_data.name,
            "ideas": ideas.ideas,
            "created_at": datetime.utcnow(),
            "ideas_id": str(uuid.uuid4())
        }
        
        print(f"Prepared ideas document: {ideas_doc}")
        
        try:
            from app.database import get_database
            db = get_database()
            if db is None:
                print("ERROR: Database not connected! Cannot save ideas.")
                raise Exception("Database connection not available")
            
            ideas_id = await insert_document("ideas", ideas_doc)
            print(f"✅ Ideas successfully saved to MongoDB with ID: {ideas_id}")
            
        except Exception as db_error:
            print(f"❌ CRITICAL ERROR: Failed to save ideas to database: {db_error}")
            print(f"Database error details: {type(db_error).__name__}: {str(db_error)}")
            # Don't continue silently - raise the error so we know about it
            raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
        
        return ideas
    except Exception as e:
        print(f"❌ Error processing ideas request: {str(e)}")
        if "Database error" in str(e):
            raise e  # Re-raise database errors
        raise HTTPException(status_code=500, detail=f"Failed to generate ideas: {e}")

@app.post("/create_campaign", response_model=CampaignResponse)
async def create_campaign(request: CampaignRequest):
    print(f"[POST /create_campaign] Received: outreach_channel={request.outreach_channel}, persona={request.persona}")
    """
    Creates a new outreach campaign, generating content based on the chosen channel.
    """
    channel = request.outreach_channel
    persona = request.persona
    campaign_details = {
        "outreach_channel": channel,
        "persona_title": persona.title,
        "persona_company": persona.company,
        "created_at": datetime.utcnow(),
        "campaign_id": str(uuid.uuid4())
    }
    generated_content = None
    if channel == OutreachChannel.EMAIL:
        email_output = generate_email_content(persona)
        generated_content = email_output.messages
        campaign_details["message"] = "Email campaign created."
        campaign_details["content_type"] = "email"
    elif channel == OutreachChannel.LINKEDIN:
        linkedin_output = generate_linkedin_content(persona)
        generated_content = linkedin_output.messages
        campaign_details["message"] = "LinkedIn campaign created."
        campaign_details["content_type"] = "linkedin"
    elif channel == OutreachChannel.USE_BOTH:
        email_output = generate_email_content(persona)
        linkedin_output = generate_linkedin_content(persona)
        generated_content = {
            "email": email_output.messages,
            "linkedin": linkedin_output.messages
        }
        campaign_details["message"] = "Multi-channel campaign created."
        campaign_details["content_type"] = "multi_channel"
    else:
        raise HTTPException(status_code=400, detail="Invalid outreach channel selected.")
    if not generated_content:
        raise HTTPException(status_code=500, detail="Failed to generate any campaign content.")
    
    # Convert MessageContent objects to dictionaries for MongoDB serialization
    def convert_message_content_to_dict(content):
        if isinstance(content, list):
            return [convert_message_content_to_dict(item) for item in content]
        elif hasattr(content, 'subject') and hasattr(content, 'body'):
            # It's a MessageContent object
            return {
                "subject": content.subject,
                "body": content.body
            }
        elif isinstance(content, dict):
            # It's already a dictionary, but check if it contains MessageContent objects
            result = {}
            for key, value in content.items():
                result[key] = convert_message_content_to_dict(value)
            return result
        else:
            return content
    
    # Convert the generated content to MongoDB-serializable format
    serializable_content = convert_message_content_to_dict(generated_content)
    
    # Save campaign to MongoDB
    campaign_doc = {
        **campaign_details,
        "generated_content": serializable_content,
        "status": "active",
        "persona_data": {
            "title": persona.title,
            "company": persona.company
            # Removed 'location': persona.location
        }
    }
    try:
        campaign_id = await insert_document("campaign", campaign_doc)
        print(f"Campaign saved to MongoDB with ID: {campaign_id}")
        campaign_doc["_id"] = campaign_id
    except Exception as db_error:
        print(f"Warning: Failed to save campaign to database: {db_error}")
    return CampaignResponse(
        message=f"Campaign successfully created for '{channel}' channel.",
        campaign_details=campaign_details,
        generated_content=generated_content
    )

@app.post("/create_campaign_create_campaign_post", response_model=CampaignResponse)
async def create_campaign_post(request: CampaignRequest):
    print(f"[POST /create_campaign_create_campaign_post] Received: outreach_channel={request.outreach_channel}, persona={request.persona}")
    """
    Creates a new outreach campaign, generating content based on the chosen channel.
    """
    channel = request.outreach_channel
    persona = request.persona
    campaign_details = {
        "outreach_channel": channel,
        "persona_title": persona.title,
        "persona_company": persona.company,
        "created_at": datetime.utcnow(),
        "campaign_id": str(uuid.uuid4())
    }
    generated_content = None
    if channel == OutreachChannel.EMAIL:
        email_output = generate_email_content(persona)
        generated_content = email_output.messages
        campaign_details["message"] = "Email campaign created."
        campaign_details["content_type"] = "email"
    elif channel == OutreachChannel.LINKEDIN:
        linkedin_output = generate_linkedin_content(persona)
        generated_content = linkedin_output.messages
        campaign_details["message"] = "LinkedIn campaign created."
        campaign_details["content_type"] = "linkedin"
    elif channel == OutreachChannel.USE_BOTH:
        email_output = generate_email_content(persona)
        linkedin_output = generate_linkedin_content(persona)
        generated_content = {
            "email": email_output.messages,
            "linkedin": linkedin_output.messages
        }
        campaign_details["message"] = "Multi-channel campaign created."
        campaign_details["content_type"] = "multi_channel"
    else:
        raise HTTPException(status_code=400, detail="Invalid outreach channel selected.")
    if not generated_content:
        raise HTTPException(status_code=500, detail="Failed to generate any campaign content.")
    
    # Convert MessageContent objects to dictionaries for MongoDB serialization
    def convert_message_content_to_dict(content):
        if isinstance(content, list):
            return [convert_message_content_to_dict(item) for item in content]
        elif hasattr(content, 'subject') and hasattr(content, 'body'):
            # It's a MessageContent object
            return {
                "subject": content.subject,
                "body": content.body
            }
        elif isinstance(content, dict):
            # It's already a dictionary, but check if it contains MessageContent objects
            result = {}
            for key, value in content.items():
                result[key] = convert_message_content_to_dict(value)
            return result
        else:
            return content
    
    # Convert the generated content to MongoDB-serializable format
    serializable_content = convert_message_content_to_dict(generated_content)
    
    # Save campaign to MongoDB
    campaign_doc = {
        **campaign_details,
        "generated_content": serializable_content,
        "status": "active",
        "persona_data": {
            "title": persona.title,
            "company": persona.company
        }
    }
    
    print(f"Prepared campaign document: {campaign_doc}")
    
    try:
        from app.database import get_database
        db = get_database()
        if db is None:
            print("ERROR: Database not connected! Cannot save campaign.")
            raise Exception("Database connection not available")
        
        campaign_id = await insert_document("campaign", campaign_doc)
        print(f"✅ Campaign successfully saved to MongoDB with ID: {campaign_id}")
        campaign_doc["_id"] = campaign_id
        
    except Exception as db_error:
        print(f"❌ CRITICAL ERROR: Failed to save campaign to database: {db_error}")
        print(f"Database error details: {type(db_error).__name__}: {str(db_error)}")
        # Don't continue silently - raise the error so we know about it
        raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
    
    return CampaignResponse(
        message=f"Campaign successfully created for '{channel}' channel.",
        campaign_details=campaign_details,
        generated_content=generated_content
    )


# New endpoint to retrieve stored data
@app.get("/personas")
async def get_personas(limit: int = 50):
    """Retrieve stored personas from MongoDB."""
    try:
        personas = await find_documents("persona", {}, limit)
        return {"personas": personas, "count": len(personas)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve personas: {e}")


@app.get("/campaigns")
async def get_campaigns(limit: int = 50):
    """Retrieve stored campaigns from MongoDB."""
    try:
        campaigns = await find_documents("campaign", {}, limit)
        return {"campaigns": campaigns, "count": len(campaigns)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve campaigns: {e}")


@app.get("/ideas")
async def get_stored_ideas(limit: int = 50):
    """Retrieve stored ideas from MongoDB."""
    try:
        ideas = await find_documents("ideas", {}, limit)
        return {"ideas": ideas, "count": len(ideas)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve ideas: {e}")
