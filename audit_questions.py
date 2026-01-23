import json
import os
from collections import Counter

FILE_PATH = r"assets\all.json"

def audit():
    if not os.path.exists(FILE_PATH):
        print(f"File not found: {FILE_PATH}")
        return

    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON: {e}")
        return

    total_entries = len(data)
    unique_ids = set()
    unique_questions = set()
    topics = Counter()
    
    duplicates_id = 0
    duplicates_text = 0

    print(f"{'METRIC':<25} | {'VALUE':<10}")
    print("-" * 40)
    print(f"{'Total Entries':<25} | {total_entries:<10}")

    for idx, q in enumerate(data):
        if not isinstance(q, dict):
            # print(f"Skipping invalid item at index {idx}: {type(q)}")
            continue

        # Check ID uniqueness
        if q.get('id') in unique_ids:
            duplicates_id += 1
        else:
            unique_ids.add(q.get('id'))

        # Check Question Text uniqueness (normalized)
        q_text = q.get('question', '').strip().lower()
        if q_text in unique_questions:
            duplicates_text += 1
        else:
            unique_questions.add(q_text)
            
        # Count Topics
        topics[q.get('topic', 'Unknown')] += 1

    print(f"Unique IDs: {len(unique_ids)}")
    print(f"Unique Questions: {len(unique_questions)}")
    # print("-" * 40)
    # print("TOPICS DISTRIBUTION:")
    # for topic, count in topics.most_common():
    #     print(f" - {topic}: {count}")

if __name__ == "__main__":
    audit()
