import json

with open('assets/questions/premium_aptitude_english_merged.json', encoding='utf-8') as f:
    data = json.load(f)

same_content = 0
different_content = 0

for q in data[:20]:  # Check first 20
    expl = q.get('explanation', '')
    expl_full = q.get('explanation_full', '')
    
    if expl == expl_full:
        same_content += 1
        print(f"\nID: {q.get('id')} - SAME CONTENT")
        print(f"  Length: {len(expl)}")
        print(f"  Content: {expl[:100]}...")
    else:
        different_content += 1

print(f"\n=== SUMMARY (first 20) ===")
print(f"Same content: {same_content}")
print(f"Different content: {different_content}")
