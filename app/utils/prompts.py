"""
Prompt templates for generating various types of content using AI models.
This module contains functions that generate structured prompts for different
content generation tasks like persona creation, idea generation, and message creation.
"""

from app.models.persona_model import Persona



# prompt that generates the persona 
def create_persona_prompt(web_content , description ):
    persona_create_prompt = f"""
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
    return persona_create_prompt


def create_idea_generation_prompt(num_ideas: int, persona_data: Persona) -> str:
    """
    Generate a prompt for AI to create outreach ideas based on persona data.
    
    Args:
        num_ideas: Number of ideas to generate
        persona_data: Persona object containing target information
        
    Returns:
        str: Formatted prompt string for idea generation
    """
    # Craft a detailed prompt using the persona's key insights
    idea_generation_prompt = f"""
    You are a highly skilled B2B sales strategist. Your task is to generate {num_ideas} compelling and creative outreach ideas based on a detailed persona profile.

    Your response must be in JSON format and contain a single key, "ideas," which holds a list of strings. Each string must be a concise, one-sentence outreach idea.

    The ideas should focus on:
    - Directly addressing the persona's pain points.
    - Highlighting a specific solution or competitive advantage.
    - Connecting with the persona's goals.

    Persona Data:
    - Title: {persona_data.title or 'Not specified'}
    - Company: {persona_data.company or 'Not specified'}
    - Pain Points: {', '.join(persona_data.pain_points)}
    - Solutions: {', '.join(persona_data.solutions)}
    - Competitive Advantages: {', '.join(persona_data.competitive_advantages)}
    - Social Proof: {', '.join([f'"{sp.statement}" from {sp.source}' for sp in persona_data.social_proof])}
    
    Return ONLY a JSON object like this:
    {{"ideas": ["Idea 1", "Idea 2", "Idea 3"]}}
    """
    return idea_generation_prompt




def create_email_content_prompt(num_messages: int, persona_data: Persona) -> str:
    """
    Generate a prompt for AI to create email content based on persona data.
    
    Args:
        num_messages: Number of email messages to generate
        persona_data: Persona object containing target information
        
    Returns:
        str: Formatted prompt string for email content generation
    """
    emails_generation_prompt = f"""
    You are an expert sales copywriter. Your task is to generate {num_messages} compelling email messages for a B2B sales campaign. Each message must be tailored to the persona provided.

    The emails should be professional yet engaging, with a clear value proposition.
    
    Persona Data:
    - Title: {persona_data.title or 'Not specified'}
    - Company: {persona_data.company or 'Not specified'}
    - Pain Points: {', '.join(persona_data.pain_points)}
    - Solutions: {', '.join(persona_data.solutions)}
    - Social Proof: {', '.join([f'"{sp.statement}"' for sp in persona_data.social_proof])}
    
    Return ONLY a JSON object with a key "messages" containing a list of objects. Each object must have a "subject" and a "body" field.
    
    Example JSON format:
    {{
      "messages": [
        {{ "subject": "Subject for Message 1", "body": "Body of Message 1" }},
        {{ "subject": "Subject for Message 2", "body": "Body of Message 2" }}
      ]
    }}
    """
    return emails_generation_prompt



def create_linked_content_prompt(num_messages: int, persona_data: Persona) -> str:
    """
    Generate a prompt for AI to create LinkedIn message content based on persona data.
    
    Args:
        num_messages: Number of LinkedIn messages to generate
        persona_data: Persona object containing target information
        
    Returns:
        str: Formatted prompt string for LinkedIn content generation
    """
    linkedin_generation_prompt = f"""
    You are an expert LinkedIn outreach specialist. Your task is to generate {num_messages} personalized and concise LinkedIn messages for a B2B sales campaign. Each message must be tailored to the persona provided.

    The messages should be brief, friendly, and focus on starting a conversation.
    
    Persona Data:
    - Title: {persona_data.title or 'Not specified'}
    - Company: {persona_data.company or 'Not specified'}
    - Pain Points: {', '.join(persona_data.pain_points)}
    - Solutions: {', '.join(persona_data.solutions)}
    
    Return ONLY a JSON object with a key "messages" containing a list of objects. Each object must have a "body" field. Do not include a subject line.
    
    Example JSON format:
    {{
      "messages": [
        {{ "body": "Body of Message 1" }},
        {{ "body": "Body of Message 2" }}
      ]
    }}
    """