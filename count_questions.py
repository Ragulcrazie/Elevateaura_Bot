import json
import os

ASSETS_DIR = r"f:\dev\quiz_mvp\assets\questions"

FILES = {
    "NEW_GK.json": "NEW_GK.json",
    "newgk.json (Reference)": "newgk.json" 
}

total = 0
for name, filename in FILES.items():
    path = os.path.join(ASSETS_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"{name}: {len(data)}")
            total += len(data)
    except Exception as e:
        print(f"{name}: not found or error ({e})")
