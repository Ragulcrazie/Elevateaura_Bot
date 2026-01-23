import json
import os

ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets/questions"))
# Manually pointing to where we think issues are
FILES = [
    "premium_aptitude_english_merged.json",
    "premium_aptitude_hindi_merged.json",
    "premium_reasoning_english_merged.json",
    "premium_reasoning_hindi_merged.json"
]

def check():
    path = r"f:\dev\quiz_mvp\assets\questions"
    for filename in FILES:
        full_path = os.path.join(path, filename)
        print(f"Checking {filename}...")
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
                if "\0" in content:
                    print(f"❌ NULL BYTES FOUND in {filename}")
                else:
                    json.loads(content)
                    print(f"✅ Valid JSON")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    check()
