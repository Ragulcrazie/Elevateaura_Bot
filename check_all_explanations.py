import json

files_to_check = [
    'assets/questions/premium_aptitude_english_merged.json',
    'assets/questions/premium_reasoning_english_merged.json'
]

for filepath in files_to_check:
    try:
        with open(filepath, encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n{'='*80}")
        print(f"FILE: {filepath}")
        print(f"{'='*80}")
        
        missing_full = []
        empty_full = []
        shorter_full = []
        
        for q in data:
            expl = q.get('explanation', '')
            expl_full = q.get('explanation_full')
            
            if expl_full is None:
                missing_full.append(q.get('id'))
            elif not expl_full or expl_full.strip() == '':
                empty_full.append(q.get('id'))
            elif len(expl_full) < len(expl):
                shorter_full.append({
                    'id': q.get('id'),
                    'expl_len': len(expl),
                    'full_len': len(expl_full)
                })
        
        print(f"Total questions: {len(data)}")
        print(f"Missing explanation_full: {len(missing_full)}")
        print(f"Empty explanation_full: {len(empty_full)}")
        print(f"Shorter explanation_full: {len(shorter_full)}")
        
        if shorter_full:
            print(f"\nProblematic questions (full < short):")
            for item in shorter_full[:10]:
                print(f"  {item['id']}: expl={item['expl_len']}, full={item['full_len']}")
        
    except Exception as e:
        print(f"Error checking {filepath}: {e}")
