import json

with open('assets/questions/premium_aptitude_english_merged.json', encoding='utf-8') as f:
    data = json.load(f)

empty_full = []
missing_full = []

for q in data:
    expl_full = q.get('explanation_full')
    
    if expl_full is None:
        missing_full.append(q.get('id'))
    elif expl_full.strip() == '':
        empty_full.append(q.get('id'))

print(f"Questions with missing explanation_full: {len(missing_full)}")
if missing_full[:5]:
    print(f"  Examples: {missing_full[:5]}")

print(f"\nQuestions with empty explanation_full: {len(empty_full)}")
if empty_full[:5]:
    print(f"  Examples: {empty_full[:5]}")

print(f"\nTotal questions: {len(data)}")
print(f"Questions with valid explanation_full: {len(data) - len(missing_full) - len(empty_full)}")
