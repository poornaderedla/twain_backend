import json
import google.generativeai as genai

from app.models.persona_model import Persona
from app.models.sequence_model import MessageOutput
from app.utils import prompts


def generate_email_content(persona_data: Persona, num_messages: int = 3) -> MessageOutput:
    """Generates email message content based on the persona."""
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = prompts.create_email_content_prompt(num_messages=num_messages, persona_data=persona_data)
    try:
        ai_response = model.generate_content(prompt)
        response_text = ai_response.text.strip()
        if response_text.startswith('```json'): response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif response_text.startswith('```'): response_text = response_text.split('```')[1].split('```')[0].strip()
        messages_json = json.loads(response_text)
        return MessageOutput(**messages_json)
    except Exception as e:
        print(f"Error calling Gemini API for emails or parsing JSON: {e}")
        return MessageOutput(messages=[])

def generate_linkedin_content(persona_data: Persona, num_messages: int = 3) -> MessageOutput:
    """Generates LinkedIn message content based on the persona."""
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = prompts.create_linked_content_prompt(num_messages=num_messages, persona_data=persona_data)
    try:
        ai_response = model.generate_content(prompt)
        response_text = ai_response.text.strip()
        if response_text.startswith('```json'): response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif response_text.startswith('```'): response_text = response_text.split('```')[1].split('```')[0].strip()
        messages_json = json.loads(response_text)
        return MessageOutput(**messages_json)
    except Exception as e:
        print(f"Error calling Gemini API for LinkedIn or parsing JSON: {e}")
        return MessageOutput(messages=[])
