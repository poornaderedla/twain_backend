"""
Controller for scraping and generating persona data from web content.
This module handles web scraping, content processing, and AI-based persona generation.
"""

import json
from typing import List

import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

from app.config.config import settings
from app.models.persona_model import Persona, SocialProof
from app.utils import prompts

# Configure the Gemini API client with the key from settings
api_key = settings.gemini_api_key
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables or .env file")
genai.configure(api_key=api_key)




def persona_scraper(url: str, description: str) -> Persona:
    """
    Scrapes web content, combines it with a description, sends it to the Gemini API,
    and parses the JSON response into a Persona model.
    """
    # Configure the Gemini API client
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not configured")
    genai.configure(api_key=settings.gemini_api_key)


    # Scrape web content
    web_content = ''
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Processing description: {description}")
        # Extract meaningful content hierarchically
        content_tags = []
        
        # First priority: Main content containers
        main_content = soup.find_all(['main', 'article', 'section'])
        if main_content:
            for tag in main_content:
                content_tags.extend([
                    t.get_text(strip=True) for t in tag.find_all(['h1', 'h2', 'h3', 'p', 'li'])
                    if t.get_text(strip=True)
                ])
        
        # Second priority: Important text elements
        if not content_tags:
            # Headers for titles and main points
            content_tags.extend([t.get_text(strip=True) for t in soup.find_all(['h1', 'h2', 'h3'])])
            # Paragraphs for detailed content
            content_tags.extend([t.get_text(strip=True) for t in soup.find_all('p')])
            # Lists for features, benefits, etc.
            content_tags.extend([t.get_text(strip=True) for t in soup.find_all('li')])
            
        # Convert to string and clean up
        web_content = '\n'.join(filter(None, content_tags))
        print(f"[DEBUG] Scraped content length: {len(web_content)}")
    except Exception as e:
        print(f"[ERROR] Error scraping URL: {e}")
        web_content = ''

    # Always initialize the model outside the try block
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Prepare the prompt for Gemini
    prompt = prompts.create_persona_prompt(web_content = web_content , description=description)

    # It's recommended to use a model that supports JSON mode for more reliable JSON output.
    # For example, 'gemini-1.5-flash' or 'gemini-1.5-pro'.
    
    try:
        # Forcing a JSON response
        generation_config = genai.types.GenerationConfig(response_mime_type="application/json")
        
        ai_response = model.generate_content(prompt, generation_config=generation_config)
        
        
        # The response text should be a valid JSON string
        print(ai_response.text)
        persona_json = json.loads(ai_response.text)
    except Exception as e:
        print(f"Error calling Gemini API or parsing JSON: {e}")
        persona_json = {}
    def ensure_list(val):
        if val is None:
            return []
        if isinstance(val, list):
            return val
        if isinstance(val, str):
            # Split by comma and strip whitespace from each item
            return [v.strip() for v in val.split(',') if v.strip()]
        return list(val) if val else []

    # Patch persona_json to ensure all list fields are lists, not null
    for field in [
        'pain_points', 'social_proof', 'cost_of_inaction',
        'solutions', 'objections', 'competitive_advantages']:
        if persona_json.get(field) is None:
            persona_json[field] = []

    # Process social proof into proper objects
    def process_social_proof(proofs):
        if not proofs or not isinstance(proofs, list):
            return []
        result = []
        for proof in proofs:
            if isinstance(proof, dict):
                # If it's already in the correct format
                result.append(SocialProof(
                    statement=proof.get('statement', ''),
                    source=proof.get('source')
                ))
            elif isinstance(proof, str):
                # If it's a string, use it as statement with no source
                result.append(SocialProof(statement=proof))
        return result

    # Create and return the Persona object
    return Persona(
        name='',  # Explicitly empty
        title=(persona_json.get('title') or '').strip() or None,
        company=(persona_json.get('company') or '').strip() or None,
        email='',  # Explicitly empty
        pain_points=ensure_list(persona_json.get('pain_points')),
        social_proof=process_social_proof(persona_json.get('social_proof')),
        cost_of_inaction=ensure_list(persona_json.get('cost_of_inaction')),
        solutions=ensure_list(persona_json.get('solutions')),
        objections=ensure_list(persona_json.get('objections')),
        competitive_advantages=ensure_list(persona_json.get('competitive_advantages'))
    )
    
    