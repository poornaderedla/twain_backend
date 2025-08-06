import json
import os
from dotenv import load_dotenv
from typing import List
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from .persona_model import Persona, SocialProof

# loading the env file attributes
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")




def persona_scraper(url: str, description: str) -> Persona:
    """
    Scrapes web content, combines it with a description, sends it to the Gemini API,
    and parses the JSON response into a Persona model.
    """
    # Configure the Gemini API client
    genai.configure(api_key=gemini_api_key)


    # Scrape web content
    web_content = ''
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        print(gemini_api_key , description)
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
    prompt = f"""
    You are an expert B2B analyst specializing in deep market research and competitive analysis. Your task is to perform an extensive analysis of the content and extract comprehensive business insights.

    DETAILED EXTRACTION GUIDELINES:

    1. Organization Context (Look for these across the entire content):
       - title: Position or role type you're analyzing (e.g., "Chief Technology Officer", "IT Manager")
       - company: Company type or industry vertical

    2. Business Analysis (Provide detailed, multi-sentence points for each category):
       - pain_points: Identify and elaborate on:
           * Current operational challenges and their impact
           * Strategic business problems and their implications
           * Market pressures and competitive threats
           * Resource constraints and efficiency issues
           * Growth bottlenecks and scaling challenges
           Minimum 4-5 detailed points, each with context and impact.

       - social_proof: Create comprehensive proof points, each with:
           * statement: Detailed success metrics, case studies, or testimonials (2-3 sentences each)
           * source: Specific attribution (company name, role, or data source)
           Include at least 4-5 substantial proof points with metrics when possible.

       - cost_of_inaction: Analyze and detail:
           * Short-term financial impacts
           * Long-term strategic risks
           * Competitive disadvantages
           * Market share implications
           * Operational inefficiencies
           Minimum 4-5 points with specific consequences.

       - solutions: Document comprehensive solutions including:
           * Core features and their direct benefits
           * Implementation strategies
           * Expected outcomes
           * Integration capabilities
           * Success metrics
           Provide at least 5-6 detailed solution points.

       - objections: Address major concerns including:
           * Implementation challenges
           * Resource requirements
           * Change management issues
           * Technical limitations
           * Budget considerations
           List 4-5 significant objections with context.

       - competitive_advantages: Detail strategic benefits including:
           * Unique technological capabilities
           * Market positioning strengths
           * Operational efficiencies
           * Customer success factors
           * Innovation differentiators
           Minimum 4-5 substantial advantages.

    IMPORTANT:
    - Format text fields as strings, empty string if not found
    - social_proof must be an array of objects with 'statement' and 'source' fields
    - Other list fields should be arrays of strings
    - NEVER use null values (except for social_proof source field)
    - Be specific and business-focused
    - Include industry-specific terminology
    - Include quantitative metrics where possible

    Content to Analyze:
    {web_content}

    Additional Context:
    {description}

    Return ONLY a JSON object matching this structure (no additional text):
    {{"title": "", "company": "",
      "pain_points": [],
      "social_proof": [
          {{"statement": "Example success metric", "source": "Source if available"}}
      ],
      "cost_of_inaction": [],
      "solutions": [],
      "objections": [],
      "competitive_advantages": []}}
    """

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
    
    