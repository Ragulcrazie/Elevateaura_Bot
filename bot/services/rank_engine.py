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

    def _calculate_single_day_score(self, ghost, date_obj, is_completed_day=False):
        """
        Helper: Calculates a deterministic score for a specific ghost on a specific date.
        If is_completed_day is True, assumes full daily progress (End of Day).
        If False, uses current wall-clock progress.
        """
        date_str = date_obj.strftime("%Y%m%d")
        
        # 1. Deterministic Seed for this specific day
        # e.g. "1001_20241024"
        seed_str = f"{ghost['id']}_{date_str}"
        rng = random.Random(seed_str)
        
        # 2. Determine Progress Cap
        if is_completed_day:
            progress_cap = 6.0 # Max possible tests
        else:
            progress_cap = self.get_daily_slot_progress() # Current time
            
        # 3. Personal 'Activity' Multiplier (Skill)
        # We derive 'skill' from ID so it's consistent across days for the same ghost
        # Ghost ID 1001 will always be lazy or active regardless of date
        skill_seed = f"{ghost['id']}_skill"
        rng_skill = random.Random(skill_seed)
        
        # Assign a 'Persona' based on ID
        base_skill = 0.8 + (rng_skill.random() * 0.4) # 0.8 to 1.2
        
        # Calculate Tests Finished (Max 6)
        potential_tests = int(progress_cap * base_skill)
        
        # Random variance for this specific day (some days they play less)
        # But we need it deterministic for the date
        daily_variance = rng.randint(-1, 1)
        potential_tests += daily_variance
        
        # Clamp
        if potential_tests > 6: potential_tests = 6
        if potential_tests < 0: potential_tests = 0
        
        daily_score = 0
        for _ in range(potential_tests):
            # Score per test: 30-100 pts
            # Use day-specific RNG
            correct_count = rng.choices(
                population=[3, 4, 5, 6, 7, 8, 9, 10],
                weights=[5, 10, 15, 20, 20, 15, 10, 5],
                k=1
            )[0]
            daily_score += (correct_count * 10)
            
        return daily_score

    def generate_ghost_data(self, ghosts, user_score):
        """
        Daily Leaderboard Generation.
        """
        processed_ghosts = []
        now = self.get_ist_time()
        
        for g in ghosts:
            # Use Helper
            daily_score = self._calculate_single_day_score(g, now, is_completed_day=False)
            
            # Name Fixing (CRITICAL FIX)
            if not g.get("full_name") or g.get("full_name") == "Aspirant":
                 names = ["Rahul", "Priya", "Amit", "Sneha", "Vikram", "Anjali", "Rohit", "Pooja", "Karan", "Neha", "Sanjay", "Riya", "Nisha", "Arjun", "Kavita"]
                 surnames = ["Sharma", "Verma", "Singh", "Patel", "Gupta", "Kumar", "Yadav", "Das", "Jha", "Mehta", "Malhotra", "Reddy", "Nair", "Chopra", "Khan"]
                 rng_name = random.Random(g['id'])
                 g["full_name"] = f"{rng_name.choice(names)} {rng_name.choice(surnames)}"
            
            # --- Pace Logic (Visual only) ---
            # (Simplified for brevity, same as before)
            rng = random.Random(f"{g['id']}_{now.strftime('%Y%m%d')}")
            pace = 34
            if daily_score > 300: pace = rng.randint(22, 35)
            
            processed_ghosts.append({
                "user_id": g["id"],
                "full_name": g["full_name"], # Use the definitely corrected name
                "total_score": daily_score,
                "questions_answered": (daily_score // 10),
                "average_pace": pace,
                "is_ghost": True
            })
            
        # Mind Games implementation... (Rabbit/Hunter)
        # [Preserved existing Mind Game logic would go here, simplified for this patch]
        # For strict consistency requested by user, we apply purely math first.
        # If we add mind games, we must ensure they don't break the "Week = Sum(Daily)" rule excessively.
        # For now, let's return the Raw Deterministic Scores to prove the fix.
        
        processed_ghosts.sort(key=lambda x: x["total_score"], reverse=True)
        return processed_ghosts

    def generate_weekly_ghosts(self, ghosts, user_weekly_score):
        """
        Weekly Leaderboard: STRICT SUMMATION.
        Weekly Score = Sum(Previous Days Daily Scores) + Today's Daily Score
        """
        processed_ghosts = []
        now = self.get_ist_time()
        
        # 1. Identify Start of Week (Monday)
        # weekday(): Mon=0, Tue=1...
        days_to_subtract = now.weekday() 
        start_of_week = now - datetime.timedelta(days=days_to_subtract)
        
        # FALLBACK for empty ghosts
        # FALLBACK: If DB returned no ghosts, generate procedural ones
        week_seed = f"{now.strftime('%Y_%W')}"
        if not ghosts:
            ghosts = [{"id": 1000+i, "full_name": "" } for i in range(50)]
            names = ["Rahul", "Priya", "Amit", "Sneha", "Vikram", "Anjali", "Rohit", "Pooja", "Karan", "Neha", "Sanjay", "Riya", "Nisha", "Arjun", "Kavita"]
            surnames = ["Sharma", "Verma", "Singh", "Patel", "Gupta", "Kumar", "Yadav", "Das", "Jha", "Mehta", "Malhotra", "Reddy", "Nair", "Chopra", "Khan"]
            
            for i, g in enumerate(ghosts):
                rng_name = random.Random(i + int(week_seed.replace("_", "")))
                g["full_name"] = f"{rng_name.choice(names)} {rng_name.choice(surnames)}"

        for g in ghosts:
            total_weekly_score = 0
            
            # 2. Iterate from Monday up to Today
            for day_offset in range(days_to_subtract + 1):
                target_date = start_of_week + datetime.timedelta(days=day_offset)
                
                # Is this today?
                is_today = (target_date.date() == now.date())
                
                # If it's a past day, they completed it (True). 
                # If it's today, they are in progress (False).
                is_full = not is_today
                
                day_score = self._calculate_single_day_score(g, target_date, is_completed_day=is_full)
                total_weekly_score += day_score
                
            # Ensure name exists (Fix for 'Aspirant' bug)
            if not g.get("full_name") or g.get("full_name") == "Aspirant":
                 names = ["Rahul", "Priya", "Amit", "Sneha", "Vikram", "Anjali", "Rohit", "Pooja", "Karan", "Neha", "Sanjay", "Riya", "Nisha", "Arjun", "Kavita"]
                 surnames = ["Sharma", "Verma", "Singh", "Patel", "Gupta", "Kumar", "Yadav", "Das", "Jha", "Mehta", "Malhotra", "Reddy", "Nair", "Chopra", "Khan"]
                 rng_name = random.Random(g['id'])
                 g["full_name"] = f"{rng_name.choice(names)} {rng_name.choice(surnames)}"

            processed_ghosts.append({
                "user_id": g["id"],
                "full_name": g.get("full_name"),
                "weekly_score": total_weekly_score,
                "is_ghost": True
            })
            
        processed_ghosts.sort(key=lambda x: x["weekly_score"], reverse=True)
        return processed_ghosts
