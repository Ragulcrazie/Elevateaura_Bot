import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, '.')

from bot.services.question_loader import loader
import json

# Load 10 questions to check
questions = loader.get_questions(count=10, lang="english", category="aptitude")

print("=" * 80)
print("CHECKING EXPLANATION FIELDS IN LOADED QUESTIONS")
print("=" * 80)

for i, q in enumerate(questions[:5]):  # Only first 5 to keep output manageable
    print(f"\n--- Question {i+1}: {q.get('id')} ---")
    
    expl = q.get('explanation', '')
    expl_full = q.get('explanation_full', '')
    
    print(f"Has 'explanation': {bool(expl)} (length: {len(expl)})")
    print(f"Has 'explanation_full': {bool(expl_full)} (length: {len(expl_full)})")
    
    # Check which one is longer
    if len(expl_full) > len(expl):
        print(f"Status: CORRECT - explanation_full is longer")
    elif len(expl_full) < len(expl):
        print(f"Status: PROBLEM - explanation_full is SHORTER!")
        print(f"  explanation length: {len(expl)}")
        print(f"  explanation_full length: {len(expl_full)}")
    else:
        print(f"Status: WARNING - Both are the same length")

# Save to file for inspection
with open('question_debug.json', 'w', encoding='utf-8') as f:
    json.dump(questions[:5], f, indent=2, ensure_ascii=False)

print("\n" + "=" * 80)
print("First 5 questions saved to question_debug.json for inspection")
