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
        Applies psychological "rubber-banding" based on user_score.
        """
        processed_ghosts = []
        progress_cap = self.get_daily_slot_progress()
        
        # 1. Generate Base Scores
        for g in ghosts:
            # Deterministic Seed based on Name + Date (so score increases consistently today)
            # We want score to ONLY go up, never down during the day.
            today_str = self.get_ist_time().strftime("%Y%m%d")
            seed_str = f"{g['id']}_{today_str}"
            rng = random.Random(seed_str)
            
            # Personal 'Activity' Multiplier (Some ghosts are faster)
            # 0.8 to 1.2
            activity_rate = 0.8 + (rng.random() * 0.4) 
            
            # Calculate how many tests this ghost has finished
            # Max 6.
            potential_tests = int(progress_cap * activity_rate)
            if potential_tests > 6: potential_tests = 6
            if potential_tests < 0: potential_tests = 0
            
            # Each test is 0-100 points.
            # Skill Check: Assume ghosts align with Pack skill roughly.
            # But here we just use random for "realistic" variance.
            daily_score = 0
            for _ in range(potential_tests):
                # Score per test: 3 to 10 questions correct (30 to 100 points)
                # Weighted slightly towards 6-9 range for realism
                correct_count = rng.choices(
                    population=[3, 4, 5, 6, 7, 8, 9, 10],
                    weights=[5, 10, 15, 20, 20, 15, 10, 5],
                    k=1
                )[0]
                test_score = correct_count * 10
                daily_score += test_score
                
            ghost_entry = {
                "user_id": g["id"], # Using uuid as ID
                "full_name": g.get("full_name") or g.get("name") or "Aspirant",
                "total_score": daily_score,
                "questions_answered": (daily_score // 10), # Roughly
                "average_pace": rng.randint(35, 55),
                "is_ghost": True
            }
            processed_ghosts.append(ghost_entry)
            
        # 2. Psychological Adjustment (The "Trigger" Logic)
        # Sort first
        processed_ghosts.sort(key=lambda x: x["total_score"], reverse=True)
        
        # If user is high (e.g. > 300), let them feel powerful but challenged.
        # Ensure Top 3 are slightly above or just below user.
        if user_score > 0:
            target_rank_score = user_score + random.randint(-20, 40)
            
            # Make the #1 ghost competitive
            if processed_ghosts[0]["total_score"] < user_score:
                # Buff top ghost to beat user slightly (Trigger)
                processed_ghosts[0]["total_score"] = user_score + 10
            
            # If user score is VERY high (Top tier), ensure broad distribution below
            pass

        return processed_ghosts
