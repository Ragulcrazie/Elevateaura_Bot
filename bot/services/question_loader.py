import json
import random
import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# Paths to assets
# MOVED: Assets are now inside the bot folder for Cloud Deployment
ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../assets/questions"))

FILES = {
    "english": {
        "aptitude": "premium_aptitude_english_merged.json",
        "reasoning": "premium_reasoning_english_merged.json",
        "gk": "../all.json"
    },
    "hindi": {
        "aptitude": "premium_aptitude_hindi_merged.json",
        "reasoning": "premium_reasoning_hindi_merged.json",
        "gk": "hindigknew.json"
    }
}

class QuestionLoader:
    def __init__(self):
        self.cache = {
            "english": {"aptitude": [], "reasoning": [], "gk": []},
            "hindi": {"aptitude": [], "reasoning": [], "gk": []}
        }
        self.load_all()

    def load_all(self):
        """
        Loads all JSON files into memory.
        """
        for lang, categories in FILES.items():
            for cat, filename in categories.items():
                path = os.path.join(ASSETS_DIR, filename)
                if os.path.exists(path):
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            
                            # De-duplication Logic
                            unique_map = {}
                            for q in data:
                                if isinstance(q, dict) and "id" in q:
                                    unique_map[q["id"]] = q
                            
                            unique_list = list(unique_map.values())
                            self.cache[lang][cat] = unique_list
                            
                            logger.info(f"Loaded {len(unique_list)} unique questions types from {filename} (Raw: {len(data)})")
                    except Exception as e:
                        logger.error(f"Failed to load {filename}: {e}")
                else:
                    logger.warning(f"File not found: {path}")

    def get_questions(self, count: int = 5, lang: str = "english", category: str = "aptitude") -> List[Dict]:
        """
        Returns 'count' random questions for the given language and category.
        """
        pool = self.cache.get(lang, {}).get(category, [])
        if not pool:
            logger.warning(f"No questions found for {lang}/{category}. Returning empty.")
            return []
        
        # Shuffle and return unique sample
        return random.sample(pool, min(count, len(pool)))

# Singleton instance
loader = QuestionLoader()
