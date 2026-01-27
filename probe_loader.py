import sys
import os
import json

# Setup path to import bot modules
sys.path.append(os.getcwd())

from bot.services.question_loader import loader

def probe():
    print("Loading Questions...")
    # Force reload to be sure
    loader.load_all()
    
    # Check English Aptitude
    print("\n--- English Aptitude Sample ---")
    qs = loader.get_questions(count=3, lang="english", category="aptitude")
    for q in qs:
        print(f"ID: {q.get('id')}")
        print(f"Keys: {list(q.keys())}")
        print(f"Explanation Full: {q.get('explanation_full')}")
        print("-" * 20)

    # Check Hindi Aptitude
    print("\n--- Hindi Aptitude Sample ---")
    qs = loader.get_questions(count=3, lang="hindi", category="aptitude")
    for q in qs:
        print(f"ID: {q.get('id')}")
        print(f"Keys: {list(q.keys())}")
        print(f"Explanation Full: {q.get('explanation_full')}")
        print("-" * 20)

if __name__ == "__main__":
    probe()
