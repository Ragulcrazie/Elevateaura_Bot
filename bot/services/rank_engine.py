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
                
                
            # Score Calculation Logic...
            ghost_entry = {
                "user_id": g["id"], 
                "full_name": g.get("full_name") or g.get("name") or "Aspirant",
                "total_score": daily_score,
                "questions_answered": (daily_score // 10),
                "is_ghost": True
            }
            
            # --- PACE CALCULATION RELATIVE TO SCORE ---
            # High Score (Elite) usually implies faster reading/solving.
            # Low Score usually implies struggle (slow) OR guessing (super fast).
            
            # Base Pace by default
            pace = rng.randint(32, 48)
            
            # If High Score (>300), they are "Sharp"
            if daily_score > 300:
                pace = rng.randint(22, 35) # Fast 20-35s
            
            # If Very High Score (>500), they are "Machines"
            if daily_score > 500:
                pace = rng.randint(18, 28) # Super Fast
                
            # If Low Score (<100) but played tests, determine if "Struggler" or "Guesser"
            if daily_score < 100 and daily_score > 0:
                if rng.random() > 0.5:
                     pace = rng.randint(50, 80) # Struggler (Slow)
                else:
                     pace = rng.randint(12, 18) # Guesser (Rushing)
                     
            ghost_entry["average_pace"] = pace
            processed_ghosts.append(ghost_entry)
            
        # --- 2. Psychological Adjustments (Mind Game) ---
        # Logic is now STRICT: No ghost can ever exceed 600 points or 60 questions.
        # This keeps the simulation 100% realistic.
        
        if user_score > 0:
            # Sort first by raw score
            processed_ghosts.sort(key=lambda x: x["total_score"], reverse=True)
            
            # --- HELPER: Safe Setter ---
            def set_safe_score(ghost, target_score):
                # Clamp to [0, 600]
                safe_score = max(0, min(600, target_score))
                # Ensure multiple of 10
                safe_score = (safe_score // 10) * 10 
                ghost["total_score"] = safe_score
                # Derive questions answered (Logic: Average 9 pts per question?)
                # Actually, simpler: points / 10 is safest assumption for "questions correct".
                # But questions_answered tracks attempts. 
                # To be realistic: If score is 600, attempts MUST be 60.
                # If score is 300, attempts is likely ~35-40.
                # Let's cap attempts at 60.
                attempts = min(60, int(safe_score / 8.5)) # Slight buffer for wrong answers
                if attempts < (safe_score / 10): attempts = int(safe_score / 10) # Min possible
                ghost["questions_answered"] = attempts
            
            # A. The Rabbit (Chase)
            rabbit_target = user_score + 30
            rabbit_idx = 3 
            if rabbit_idx < len(processed_ghosts):
                # Only boost if within realistic limits of the day
                current_max_possible = int(progress_cap * 100) + 50 # Allowance
                if rabbit_target <= current_max_possible: 
                     set_safe_score(processed_ghosts[rabbit_idx], rabbit_target)

            # B. The Hunter (Fear)
            hunter_target = max(0, user_score - 20)
            hunter_idx = 8 
            if hunter_idx < len(processed_ghosts):
                 set_safe_score(processed_ghosts[hunter_idx], hunter_target)

            # C. The Alpha (Winner)
            if processed_ghosts[0]["total_score"] < user_score:
                 alpha_target = user_score + 10
                 set_safe_score(processed_ghosts[0], alpha_target)
                 
        # Re-sort after adjustments
        processed_ghosts.sort(key=lambda x: x["total_score"], reverse=True)
        return processed_ghosts
