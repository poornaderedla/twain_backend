from app.models.persona_model import Persona
from app.models.sequence_model import IdeasOutput
import google.generativeai as genai
from app.utils import prompts
import json 



def generate_ideas(persona_data: Persona, num_ideas: int = 3) -> IdeasOutput:
    """
    Generates creative outreach ideas based on the provided persona data.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Craft a detailed prompt using the persona's key insights
    prompt = prompts.create_idea_generation_prompt(num_ideas= num_ideas , persona_data=persona_data)
    
    try:
        # Generate content without the problematic response_mime_type parameter
        ai_response = model.generate_content(prompt)
        
        response_text = ai_response.text.strip()
        
        # Extract JSON from response if it's wrapped in markdown code blocks
        if response_text.startswith('```json'):
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif response_text.startswith('```'):
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        ideas_json = json.loads(response_text)
        return IdeasOutput(**ideas_json)
    
    except Exception as e:
        print(f"Error calling Gemini API for ideas or parsing JSON: {e}")
        return IdeasOutput(ideas=[])
    
    