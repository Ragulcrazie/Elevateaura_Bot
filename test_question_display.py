import sys
sys.path.insert(0, '.')

from bot.services.question_loader import loader
import re

def format_explanation(text: str) -> str:
    """
    Formats the explanation by adding newlines and bolding 'Step X'.
    """
    if not text: return "No explanation available."
    # Regex: Find 'Step <number>:' and replace with '\n\n**Step <number>:**'
    formatted = re.sub(r'(Step \d+:)', r'\n\n**\1**', text)
    
    # Remove duplicate numbering pattern like "**Step 1:** 1:" -> "**Step 1:**"
    formatted = re.sub(r'(\*\*Step \d+:\*\*) \d+:', r'\1', formatted)
    
    # If no steps were found, try splitting by sentences for readability
    if len(formatted) == len(text):
        formatted = re.sub(r'\. +', '.\n\n', text)
        
    return formatted.strip()

# Load some questions
questions = loader.get_questions(count=3, lang="english", category="aptitude")

for i, q in enumerate(questions):
    print(f"\n{'='*80}")
    print(f"QUESTION {i+1}: {q.get('id')}")
    print(f"{'='*80}")
    print(f"Question: {q.get('question', 'N/A')[:100]}...")
    
    expl = q.get('explanation', '')
    expl_full = q.get('explanation_full', '')
    
    print(f"\n--- SHORT EXPLANATION (length: {len(expl)}) ---")
    print(expl[:200])
    
    print(f"\n--- FULL EXPLANATION (length: {len(expl_full)}) ---")
    print(expl_full[:200])
    
    print(f"\n--- FORMATTED FULL EXPLANATION ---")
    formatted = format_explanation(expl_full)
    print(formatted[:300])
