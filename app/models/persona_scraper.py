import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from .persona_model import Persona, SocialProof

def scrape_persona_from_url(url: str, description: str) -> Persona:
    """
    Scrape the given URL and extract persona-related information, using the description to guide extraction.
    """
    import re
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    desc_keywords = set(description.lower().split())

    def is_relevant(text, keywords=desc_keywords):
        text_words = set(text.lower().split())
        return bool(keywords & text_words)

    def extract_points(tags, keywords=None, min_len=20, max_points=3):
        points = []
        for tag in tags:
            for el in soup.find_all(tag):
                text = el.get_text(strip=True)
                if text and len(text) >= min_len:
                    if not keywords or is_relevant(text, keywords):
                        points.append(text)
                if len(points) >= max_points:
                    break
            if len(points) >= max_points:
                break
        return points

    h1 = soup.find('h1')
    name = h1.get_text(strip=True) if h1 else None

    # Title extraction
    meta_title = soup.find('meta', attrs={'name': 'title'})
    title = None
    if meta_title and meta_title.get('content'):
        title = meta_title['content'].strip()
    else:
        h2 = soup.find('h2')
        if h2 and h2.get_text(strip=True):
            title = h2.get_text(strip=True)
        else:
            h3 = soup.find('h3')
            if h3 and h3.get_text(strip=True):
                title = h3.get_text(strip=True)

    # Company extraction
    company = None
    meta_company = soup.find('meta', attrs={'name': 'company'})
    if meta_company and meta_company.get('content'):
        company = meta_company['content'].strip()
    else:
        strong = soup.find('strong')
        if strong and strong.get_text(strip=True):
            company = strong.get_text(strip=True)
        elif h1 and h1.get_text(strip=True):
            company = h1.get_text(strip=True)

    # Email extraction
    email = None
    emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", soup.get_text())
    if emails:
        email = emails[0]

    # Keyword sets for each field
    pain_keywords = desc_keywords | {"problem", "challenge", "issue", "pain", "struggle", "difficulty"}
    inaction_keywords = {"risk", "consequence", "cost", "loss", "missed", "fail", "failure"}
    solution_keywords = {"solution", "resolve", "fix", "address", "answer", "approach", "method"}
    objection_keywords = {"objection", "concern", "hesitation", "doubt", "barrier", "blocker"}
    advantage_keywords = {"advantage", "benefit", "edge", "superior", "unique", "better", "strength"}

    # Search both <li> and <p> for all fields, prefer <li> but fallback to <p>
    pain_points = extract_points(['li', 'p'], pain_keywords, min_len=20, max_points=3)
    cost_of_inaction = extract_points(['li', 'p'], inaction_keywords, min_len=20, max_points=2)
    solutions = extract_points(['li', 'p'], solution_keywords, min_len=20, max_points=2)
    objections = extract_points(['li', 'p'], objection_keywords, min_len=20, max_points=2)
    competitive_advantages = extract_points(['li', 'p'], advantage_keywords, min_len=20, max_points=2)

    # Social proof extraction
    social_proof = []
    for block in soup.find_all(['blockquote', 'q']):
        statement = block.get_text(strip=True)
        if statement:
            social_proof.append(SocialProof(statement=statement, source=url))
    # Also look for testimonial/review keywords in all <p> and <li>
    if not social_proof:
        for tag in ['p', 'li']:
            for el in soup.find_all(tag):
                text = el.get_text(strip=True)
                if any(kw in text.lower() for kw in ["testimonial", "review", "said", "feedback"]):
                    social_proof.append(SocialProof(statement=text, source=url))
                if len(social_proof) >= 2:
                    break
            if len(social_proof) >= 2:
                break

    def ensure_list(data):
        return data if data else []

    persona = Persona(
        name=name,
        title=title,
        company=company,
        email=email,
        pain_points=ensure_list(pain_points),
        social_proof=ensure_list(social_proof),
        cost_of_inaction=ensure_list(cost_of_inaction),
        solutions=ensure_list(solutions),
        objections=ensure_list(objections),
        competitive_advantages=ensure_list(competitive_advantages)
    )
    return persona
