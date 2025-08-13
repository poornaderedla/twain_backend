"""
Controller for scraping and generating persona data from web content.
This module handles web scraping, content processing, and AI-based persona generation.
"""

import json
from typing import List
import uuid

import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

from app.config.config import settings
from app.models.persona_model import Persona, SocialProof
from app.utils import prompts

# Configure the Gemini API client with the key from settings
api_key = settings.GEMINI_API_KEY
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables or .env file")
genai.configure(api_key=api_key)




def persona_scraper(url: str, description: str) -> Persona:
    """
    Scrapes web content, combines it with a description, sends it to the Gemini API,
    and parses the JSON response into a Persona model.
    """
    print(f"[PERSONA_SCRAPER] Starting persona generation for URL: {url}")
    print(f"[PERSONA_SCRAPER] Description: {description}")
    
    # Configure the Gemini API client
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured")
    genai.configure(api_key=settings.GEMINI_API_KEY)
    print(f"[PERSONA_SCRAPER] Gemini API configured successfully")

    # Scrape web content
    web_content = ''
    try:
        print(f"[PERSONA_SCRAPER] Attempting to scrape URL: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"[PERSONA_SCRAPER] Successfully scraped URL, processing content...")
        
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
        print(f"[PERSONA_SCRAPER] Scraped content length: {len(web_content)} characters")
        
        if len(web_content) < 50:
            print(f"[PERSONA_SCRAPER] WARNING: Very little content scraped, this might cause issues")
            
    except Exception as e:
        print(f"[PERSONA_SCRAPER] ERROR: Failed to scrape URL {url}: {e}")
        web_content = ''

    # Always initialize the model outside the try block
    model = genai.GenerativeModel('gemini-1.5-flash')
    print(f"[PERSONA_SCRAPER] Gemini model initialized")

    # Prepare the prompt for Gemini
    prompt = prompts.create_persona_prompt(web_content=web_content, description=description)
    print(f"[PERSONA_SCRAPER] Prompt prepared, length: {len(prompt)} characters")
    
    try:
        print(f"[PERSONA_SCRAPER] Calling Gemini API...")
        # Generate content without the problematic response_mime_type parameter
        ai_response = model.generate_content(prompt)
        
        response_text = ai_response.text.strip()
        print(f"[PERSONA_SCRAPER] Gemini response received, length: {len(response_text)} characters")
        print(f"[PERSONA_SCRAPER] Response preview: {response_text[:200]}...")
        
        # Extract JSON from response if it's wrapped in markdown code blocks
        if response_text.startswith('```json'):
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif response_text.startswith('```'):
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        print(f"[PERSONA_SCRAPER] Attempting to parse JSON...")
        persona_json = json.loads(response_text)
        print(f"[PERSONA_SCRAPER] JSON parsed successfully: {persona_json}")
        
    except Exception as e:
        print(f"[PERSONA_SCRAPER] ERROR: Failed to call Gemini API or parse JSON: {e}")
        print(f"[PERSONA_SCRAPER] Response text was: {response_text if 'response_text' in locals() else 'No response'}")
        # Return a default persona instead of empty dict
        persona_json = {
            'title': 'Unknown',
            'company': 'Unknown',
            'pain_points': ['Unable to analyze website'],
            'social_proof': [],
            'cost_of_inaction': ['Unable to analyze website'],
            'solutions': ['Unable to analyze website'],
            'objections': ['Unable to analyze website'],
            'competitive_advantages': ['Unable to analyze website']
        }
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

    # Helper function to extract first item from list or return string
    def extract_string(val):
        if isinstance(val, list) and val:
            return val[0].strip() if val[0] else None
        elif isinstance(val, str):
            return val.strip() or None
        return None

    # Create and return the Persona object
    persona = Persona(
        id=str(uuid.uuid4()),  # Add the required id field
        name='',  # Explicitly empty
        title=extract_string(persona_json.get('title')),
        company=extract_string(persona_json.get('company')),
        email='',  # Explicitly empty
        pain_points=ensure_list(persona_json.get('pain_points')),
        social_proof=process_social_proof(persona_json.get('social_proof')),
        cost_of_inaction=ensure_list(persona_json.get('cost_of_inaction')),
        solutions=ensure_list(persona_json.get('solutions')),
        objections=ensure_list(persona_json.get('objections')),
        competitive_advantages=ensure_list(persona_json.get('competitive_advantages'))
    )
    
    print(f"[PERSONA_SCRAPER] ✅ Persona created successfully: {persona.company} - {persona.title}")
    return persona
    
    