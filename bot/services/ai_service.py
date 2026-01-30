
import json
import os
import random

class AIService:
    def __init__(self):
        self.data_path = "assets/ai/integrated_ai_data.json"
        self.data = []
        self.topic_map = {}
        self.load_data()

    def load_data(self):
        """Loads the integrated AI JSON file."""
        try:
            path = self.data_path
            if not os.path.exists(path):
                path = os.path.join(os.getcwd(), self.data_path)

            with open(path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
                
            # Create a lookup map for faster access
            self.topic_map = {item["topic"].lower(): item for item in self.data}
            print(f"Loaded {len(self.data)} AI topics.")
        except Exception as e:
            print(f"Error loading AI data: {e}")
            self.data = []
            self.topic_map = {}

    def _find_best_match(self, topic: str):
        """
        Finds the best matching item using:
        1. Exact Key Lookup
        2. Bidirectional Substring Match
        3. Token Overlap
        """
        if not topic: return None
        topic_lower = topic.strip().lower()

        # 1. Exact Map Lookup
        if topic_lower in self.topic_map:
            return self.topic_map[topic_lower]

        # 2. Fuzzy Search
        topic_words = set(topic_lower.replace("&", " ").replace("(", " ").replace(")", " ").split())
        best_match = None
        max_overlap = 0

        for item in self.data:
            it_topic = item.get("topic", "").lower()
            
            # Bidirectional Substring
            if topic_lower == it_topic or topic_lower in it_topic or it_topic in topic_lower:
                return item 
            
            # Token Overlap
            it_words = set(it_topic.replace("&", " ").replace("(", " ").replace(")", " ").split())
            overlap = len(topic_words.intersection(it_words))
            
            if overlap > max_overlap:
                max_overlap = overlap
                best_match = item
        
        if max_overlap >= 1: 
             return best_match
             
        return None

    def _get_random_fallback(self, lang, category, type_key):
        """Returns a random piece of advice from the same category."""
        candidates = [item for item in self.data if item.get("category") == category]
        if candidates:
            random_item = random.choice(candidates)
            content_list = random_item.get(type_key, {}).get(lang, [])
            if content_list:
                prefix = "🧠 " if type_key == "psych_hacks" else "Gen: "
                return prefix + random.choice(content_list)
        return None

    def get_shortcut(self, topic: str, lang="english", category="aptitude"):
        lang_code = "hi" if "hind" in lang.lower() else "en"
        match = self._find_best_match(topic)
        
        if match:
            shortcuts = match.get("shortcuts", {}).get(lang_code, [])
            if shortcuts: return random.choice(shortcuts)

        # Fallback
        fallback = self._get_random_fallback(lang_code, category, "shortcuts")
        return fallback or "Focus on accuracy before speed."

    def get_common_mistake(self, topic: str, lang="english", category="aptitude"):
        lang_code = "hi" if "hind" in lang.lower() else "en"
        match = self._find_best_match(topic)
        
        if match:
            mistakes = match.get("common_mistakes", {}).get(lang_code, [])
            if mistakes: return random.choice(mistakes)
            
        # Fallback
        fallback = self._get_random_fallback(lang_code, category, "common_mistakes")
        return fallback or "Don't guess randomly."

    def get_psych_hack(self, topic: str, lang="english", category="aptitude"):
        lang_code = "hi" if "hind" in lang.lower() else "en"
        match = self._find_best_match(topic)
        
        if match:
            hacks = match.get("psych_hacks", {}).get(lang_code, [])
            if hacks: return random.choice(hacks)

        # Fallback
        fallback = self._get_random_fallback(lang_code, category, "psych_hacks")
        return fallback or "Visualize the problem before solving it."

ai_service = AIService()
