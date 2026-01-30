
import json
import os

BASE_PATH = "assets/ai"
OUTPUT_FILE = "assets/ai/integrated_ai_data.json"

FILES_MAP = [
    # Aptitude
    {"filename": "aptitude_ai.json", "lang": "en", "type": "standard", "category": "aptitude"},
    {"filename": "hindiaptitude_ai.json", "lang": "hi", "type": "standard", "category": "aptitude"},
    {"filename": "pshacksaptitude_ai.json", "lang": "en", "type": "psych", "category": "aptitude"},
    {"filename": "pshacksapthindi.json", "lang": "hi", "type": "psych", "category": "aptitude"},
    
    # Reasoning
    {"filename": "reasoning_ai.json", "lang": "en", "type": "standard", "category": "reasoning"},
    {"filename": "hindireasoning_ai.json", "lang": "hi", "type": "standard", "category": "reasoning"},
    {"filename": "pshacksreasoning.json", "lang": "en", "type": "psych", "category": "reasoning"},
    {"filename": "pshacksreasoninghindi.json", "lang": "hi", "type": "psych", "category": "reasoning"},

    # GK
    {"filename": "gk_ai.json", "lang": "en", "type": "standard", "category": "gk"},
    {"filename": "hindigk_ai.json", "lang": "hi", "type": "standard", "category": "gk"},
    {"filename": "pshacksgk.json", "lang": "en", "type": "psych", "category": "gk"},
    {"filename": "pshacksgkhindi.json", "lang": "hi", "type": "psych", "category": "gk"},
]

def load_json(filename):
    path = os.path.join(BASE_PATH, filename)
    if not os.path.exists(path):
        print(f"Warning: {filename} not found.")
        return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(f"ERROR processing {filename}: {e}")
            return []

def normalize_topic(topic):
    # Normalize for key lookup (e.g. trim spaces, fix minor copy-paste issues)
    # But preserve original casing for display if needed
    return topic.strip()

master_data = {}

for entry in FILES_MAP:
    data = load_json(entry["filename"])
    lang = entry["lang"]
    ftype = entry["type"]
    category = entry["category"]

    for item in data:
        raw_topic = item.get("topic", "Unknown")
        topic_key = normalize_topic(raw_topic)

        if topic_key not in master_data:
            master_data[topic_key] = {
                "topic": topic_key,
                "category": category, 
                "shortcuts": {"en": [], "hi": []},
                "common_mistakes": {"en": [], "hi": []},
                "psych_hacks": {"en": [], "hi": []}
            }
        
        # Ensure category is set (first file defines it, subsequent ones should match or ignored)
        # Verify category consistency? 
        # Actually, let's trust the file map.
        
        if ftype == "standard":
            shortcuts = item.get("shortcuts", [])
            mistakes = item.get("common_mistakes", [])
            
            if shortcuts:
                master_data[topic_key]["shortcuts"][lang].extend(shortcuts)
            if mistakes:
                master_data[topic_key]["common_mistakes"][lang].extend(mistakes)

        elif ftype == "psych":
            hacks = item.get("psychology_hacks") or item.get("hacks") or []
            if hacks:
                master_data[topic_key]["psych_hacks"][lang].extend(hacks)

# Convert dict to list
final_list = list(master_data.values())

# Sort by category then topic
final_list.sort(key=lambda x: (x["category"], x["topic"]))

print(f"Merged {len(final_list)} unique topics.")

# Save
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(final_list, f, indent=2, ensure_ascii=False)

print(f"Successfully saved to {OUTPUT_FILE}")
