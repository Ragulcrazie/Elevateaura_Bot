import json

with open('assets/questions/premium_aptitude_english_merged.json', encoding='utf-8') as f:
    data = json.load(f)

short_full = 0
missing_full = 0
correct = 0

for q in data:
    expl = q.get('explanation', '')
    expl_full = q.get('explanation_full', '')
    
    if not expl_full:
        missing_full += 1
    elif len(expl_full) < len(expl):
        short_full += 1
        if short_full <= 3:  # Show first 3 examples
            print(f"\nID: {q.get('id')}")
            print(f"  explanation ({len(expl)} chars): {expl[:150]}")
            print(f"  explanation_full ({len(expl_full)} chars): {expl_full[:150]}")
    else:
        correct += 1

print(f"\n=== SUMMARY ===")
print(f"Total questions: {len(data)}")
print(f"Correct (full > short): {correct}")
print(f"Wrong (full < short): {short_full}")
print(f"Missing explanation_full: {missing_full}")
