
import json
import os
import random

class AIService:
    def __init__(self):
        self.base_path = "assets/ai"
        self.data = {}
        self.load_data()

    def load_data(self):
        """Loads all AI JSON files into memory."""
        files = {
            "english_aptitude": "aptitude_ai.json",
            "english_reasoning": "reasoning_ai.json",
            "english_gk": "gk_ai.json",
            "hindi_aptitude": "hindiaptitude_ai.json",
            "hindi_reasoning": "hindireasoning_ai.json",
            "hindi_gk": "hindigk_ai.json",
            "english_aptitude_psych": "pshacksaptitude_ai.json",
            "english_reasoning_psych": "pshacksreasoning.json",
            "english_gk_psych": "pshacksgk.json",
            "hindi_aptitude_psych": "pshacksapthindi.json",
            "hindi_reasoning_psych": "pshacksreasoninghindi.json",
            "hindi_gk_psych": "pshacksgkhindi.json"
        }

        for key, filename in files.items():
            path = os.path.join(self.base_path, filename)
            try:
                # Use absolute path if relative fails
                if not os.path.exists(path):
                    path = os.path.join(os.getcwd(), self.base_path, filename)

                with open(path, "r", encoding="utf-8") as f:
                    self.data[key] = json.load(f)
            except Exception as e:
                print(f"Error loading AI file {filename}: {e}")
                self.data[key] = []

    def get_context(self, lang="english", category="aptitude"):
        """Returns the data list for a specific language and category."""
        key = f"{lang.lower()}_{category.lower()}"
        return self.data.get(key, [])

    def _find_best_match(self, topic: str, data_list: list):
        """
        Finds the best matching item using:
        1. Exact Match
        2. Substring Match (Topic in JSON vs JSON in Topic)
        3. Token Overlap (Best Keyword Match)
        """
        if not topic:
            return None
            
        topic_lower = topic.lower()
        topic_words = set(topic_lower.replace("&", " ").replace("(", " ").replace(")", " ").split())
        
        best_match = None
        max_overlap = 0

        for item in data_list:
            it_topic = item.get("topic", "").lower()
            
            # 1. Exact or Substring (Bidirectional)
            # "History" in "Ancient Indian History" -> True
            if topic_lower == it_topic or topic_lower in it_topic or it_topic in topic_lower:
                return item # Immediate return on strong match
            
            # 2. Token Overlap
            it_words = set(it_topic.replace("&", " ").replace("(", " ").replace(")", " ").split())
            overlap = len(topic_words.intersection(it_words))
            
            if overlap > max_overlap:
                max_overlap = overlap
                best_match = item
        
        # Threshold: At least 1 significant word overlap
        if max_overlap >= 1: 
             return best_match
             
        return None

    def get_shortcut(self, topic: str, lang="english", category="aptitude"):
        data_list = self.get_context(lang, category)
        match = self._find_best_match(topic, data_list)
        
        if match:
            shortcuts = match.get("shortcuts", [])
            if shortcuts:
                return random.choice(shortcuts)

        # Fallback
        if data_list:
            random_topic = random.choice(data_list)
            shortcuts = random_topic.get("shortcuts", [])
            if shortcuts:
                return f"Gen: {random.choice(shortcuts)}"
        
        return "Focus on accuracy before speed. That is the ultimate shortcut."

    def get_common_mistake(self, topic: str, lang="english", category="aptitude"):
        data_list = self.get_context(lang, category)
        match = self._find_best_match(topic, data_list)
        
        if match:
            mistakes = match.get("common_mistakes", [])
            if mistakes:
                return random.choice(mistakes)
        
        # Fallback
        if data_list:
            random_topic = random.choice(data_list)
            mistakes = random_topic.get("common_mistakes", [])
            if mistakes:
                return f"Gen: {random.choice(mistakes)}"

        return "Don't guess randomly. Option elimination is your best friend."

    def get_psych_hack(self, topic: str, lang="english", category="aptitude"):
        key = f"{lang.lower()}_{category.lower()}_psych"
        data_list = self.data.get(key, [])
        match = self._find_best_match(topic, data_list)
        
        if match:
            hacks = match.get("psychology_hacks") or match.get("hacks") or []
            if hacks:
                return random.choice(hacks)

        # Fallback
        if data_list:
            random_topic = random.choice(data_list)
            hacks = random_topic.get("psychology_hacks") or random_topic.get("hacks") or []
            if hacks:
                return f"🧠 {random.choice(hacks)}"

        return "Visualize the problem before solving it. Your brain is a supercomputer; give it the right input."

ai_service = AIService()
