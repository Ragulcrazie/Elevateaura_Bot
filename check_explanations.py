import json
import random

with open('assets/questions/premium_aptitude_english_merged.json', encoding='utf-8') as f:
    data = json.load(f)

samples = random.sample(data, 5)

for i, q in enumerate(samples):
    expl = q.get('explanation', '')
    expl_full = q.get('explanation_full', '')
    print(f"\nQ{i+1} (ID: {q.get('id', 'unknown')})")
    print(f"  explanation length: {len(expl)}")
    print(f"  explanation_full length: {len(expl_full)}")
    print(f"  explanation preview: {expl[:100]}...")
    print(f"  explanation_full preview: {expl_full[:100]}...")
