import random
import datetime

class RankEngine:
    def __init__(self):
        # IST is UTC+5:30
        self.tz = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

    def get_ist_time(self):
        return datetime.datetime.now(self.tz)

    def get_daily_slot_progress(self):
        """
        Returns a float representing how 'deep' we are into the 6-test daily cycle.
        Returning 1.0 means ~1 test could be done. 6.0 means all 6 could be done.
        
        Schedule Assumption:
        - 00:00 - 06:00: Ghost Period (Some night owls play, most don't) -> 0.5 tests
        - 06:00 - 09:00: Morning Rush -> 1.5 tests
        - 09:00 - 13:00: Work Mode -> 2.5 tests
        - 13:00 - 18:00: Afternoon -> 4.5 tests
        - 18:00 - 23:59: Evening Grind -> 6.0 tests
        """
        now = self.get_ist_time()
        hour = now.hour
        
        if hour < 6: return 0.5  # Early night
        if hour < 9: return 1.5  # Morning
        if hour < 13: return 2.5 # Pre-lunch
        if hour < 18: return 4.5 # Afternoon
        return 6.0               # Night (Full capacity)

    def generate_ghost_data(self, ghosts, user_score):
        """
        Takes raw ghost rows and hydrates them with dynamic daily scores.
        Applies psychological "rubber-banding" based on user_score to create engagement.
        Roles:
        - The Alpha: Top ranker, high score.
        - The Rabbit: Always 20-40 points ahead of user (Chase Motivation).
        - The Hunter: Always 10-20 points behind user (Fear of Loss).
        - The Safety Net: Bottom 20% are lazy (0-50 pts) so user isn't last.
        """
        processed_ghosts = []
        progress_cap = self.get_daily_slot_progress()
        today_str = self.get_ist_time().strftime("%Y%m%d")
        
        # --- 1. Generate Base Scores ---
        for i, g in enumerate(ghosts):
            # Deterministic Seed
            seed_str = f"{g['id']}_{today_str}"
            rng = random.Random(seed_str)
            
            # Personal 'Activity' Multiplier
            # Normal Ghosts: 0.8 - 1.2
            # Safety Net (Bottom 20% by index): Lazy
            is_safety_net = (i >= len(ghosts) * 0.8)
            
            if is_safety_net:
                activity_rate = 0.1 # Very lazy
            else:
                activity_rate = 0.8 + (rng.random() * 0.4)
            
            # Calculate Tests Finished (Max 6)
            potential_tests = int(progress_cap * activity_rate)
            if potential_tests > 6: potential_tests = 6
            if potential_tests < 0: potential_tests = 0
            
            daily_score = 0
            for _ in range(potential_tests):
                # Score per test: 30-100 pts
                correct_count = rng.choices(
                    population=[3, 4, 5, 6, 7, 8, 9, 10],
                    weights=[5, 10, 15, 20, 20, 15, 10, 5],
                    k=1
                )[0]
                daily_score += (correct_count * 10)
                
            ghost_entry = {
                "user_id": g["id"], 
                "full_name": g.get("full_name") or g.get("name") or "Aspirant",
                "total_score": daily_score,
                "questions_answered": (daily_score // 10),
                "average_pace": rng.randint(35, 55),
                "is_ghost": True
            }
            processed_ghosts.append(ghost_entry)
            
        # --- 2. Psychological Adjustments (Mind Game) ---
        # Only apply if user has played (score > 0) to avoid weirdness when user is new
        if user_score > 0:
            # Sort first by raw score
            processed_ghosts.sort(key=lambda x: x["total_score"], reverse=True)
            
            # Identify Roles based on current sorted positions
            # We treat the list as mutable
            
            # A. The Rabbit (Chase): Find someone just above user, or create one
            # Target: User + 30 pts (approx)
            rabbit_target = user_score + 30
            # Find a ghost to be the rabbit (e.g., index 5 or 6, or someone close)
            # We'll just pick index 3 (Rank 4) to be the "Standard Rabbit" if they aren't already huge
            rabbit_idx = 3 
            if rabbit_idx < len(processed_ghosts):
                processed_ghosts[rabbit_idx]["total_score"] = rabbit_target
                processed_ghosts[rabbit_idx]["questions_answered"] = rabbit_target // 10
                
            # B. The Hunter (Fear): Find someone just behind
            # Target: User - 20 pts (approx)
            hunter_target = max(0, user_score - 20)
            hunter_idx = 8 # Rank 9 (Arbitrary "someone behind")
            if hunter_idx < len(processed_ghosts):
                 processed_ghosts[hunter_idx]["total_score"] = hunter_target
                 processed_ghosts[hunter_idx]["questions_answered"] = hunter_target // 10

            # C. The Alpha (Winner): Ensure #1 is impressive
            if processed_ghosts[0]["total_score"] < user_score:
                 # If user is #1, make the alpha fight back
                 processed_ghosts[0]["total_score"] = user_score + 10
                 processed_ghosts[0]["questions_answered"] = (user_score + 10) // 10
                 
        # Re-sort after adjustments
        processed_ghosts.sort(key=lambda x: x["total_score"], reverse=True)
        return processed_ghosts
