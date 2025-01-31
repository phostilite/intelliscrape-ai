import re
from difflib import SequenceMatcher
from typing import Dict, Any

def calculate_name_match_score(search_name: str, result_text: str) -> float:
    """Calculate how well the name matches in the result."""
    if not search_name or not result_text:
        return 0.0
    
    search_name = search_name.lower()
    result_text = result_text.lower()
    
    # Exact match gets highest score
    if search_name in result_text:
        return 1.0
    
    # Check for partial name matches
    name_parts = search_name.split()
    matches = sum(1 for part in name_parts if part in result_text)
    if matches > 0:
        return matches / len(name_parts) * 0.8
    
    # Use sequence matcher for fuzzy matching
    return SequenceMatcher(None, search_name, result_text).ratio() * 0.6

def calculate_description_match_score(description: str, result_text: str) -> float:
    """Calculate how well the description matches in the result."""
    if not description or not result_text:
        return 0.0
    
    description = description.lower()
    result_text = result_text.lower()
    
    # Split into keywords and check matches
    keywords = set(re.findall(r'\w+', description))
    if not keywords:
        return 0.0
    
    result_words = set(re.findall(r'\w+', result_text))
    matches = len(keywords.intersection(result_words))
    
    return min(matches / len(keywords), 1.0)

def calculate_content_relevance_score(result: Dict[Any, Any], source_type: str) -> float:
    """Calculate the general relevance of the content."""
    score = 0.0
    
    # Base score from result metadata
    if 'title' in result and result['title']:
        score += 0.3
    if 'snippet' in result and result['snippet']:
        score += 0.2
    
    # Source type bonus
    source_weights = {
        'LinkedIn': 0.3,
        'GitHub': 0.25,
        'Twitter': 0.2,
        'Medium': 0.15,
        'Wikipedia': 0.2,
    }
    score += source_weights.get(source_type, 0.1)
    
    return min(score, 1.0)

def calculate_overall_score(name_score: float, desc_score: float, content_score: float) -> float:
    """Calculate the overall score with weighted components."""
    weights = {
        'name': 0.5,      # Name match is most important
        'description': 0.3,  # Description match is second
        'content': 0.2    # General content relevance is third
    }
    
    overall_score = (
        name_score * weights['name'] +
        desc_score * weights['description'] +
        content_score * weights['content']
    )
    
    return round(min(overall_score, 1.0), 3)
