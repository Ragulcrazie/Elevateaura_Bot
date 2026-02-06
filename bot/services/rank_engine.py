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

    def _ensure_ghost_name(self, g):
        """Helper to guarantee a name exists."""
        if not g.get("full_name") or g.get("full_name") == "Aspirant":
             names = ["Rahul", "Priya", "Amit", "Sneha", "Vikram", "Anjali", "Rohit", "Pooja", "Karan", "Neha", "Sanjay", "Riya", "Nisha", "Arjun", "Kavita"]
             surnames = ["Sharma", "Verma", "Singh", "Patel", "Gupta", "Kumar", "Yadav", "Das", "Jha", "Mehta", "Malhotra", "Reddy", "Nair", "Chopra", "Khan"]
             rng_name = random.Random(g.get('id', 0))
             g["full_name"] = f"{rng_name.choice(names)} {rng_name.choice(surnames)}"
        return g["full_name"]

    def _calculate_dynamic_pace(self, ghost_id, base_score, user_pace, is_winning_ghost):
        """Adjusts ghost pace to be competitive with the user."""
        # V3: Deterministic Consistency based on Ghost ID + Date
        # ensures same ghost has same pace in Daily vs Weekly for that day
        today_ord = self.get_ist_time().toordinal()
        
        # FIX: Handle UUIDs by hashing if not integer
        try:
            gid_int = int(ghost_id)
        except:
            # Simple hash for UUID string to integer
            gid_int = sum(ord(c) for c in str(ghost_id))
            
        seed_val = gid_int + today_ord
        rng = random.Random(seed_val)
        
        if not user_pace or user_pace < 5: return rng.randint(25, 45)
        
        if is_winning_ghost:
            # If user is fast, ensure variance so ghosts don't all clamp to 12s
            offset = rng.randint(1, 4)
            target = user_pace - offset
            if target < 12:
                # Spread out the elites (12, 13, 14, 15)
                return 12 + rng.randint(0, 3)
            return target
        else:
            return user_pace + rng.randint(4, 10)

    def generate_ghost_data(self, ghosts, user_score, user_pace=None, god_mode=False):
        """Daily Leaderboard Generation with PsyOps."""
        processed_ghosts = []
        now = self.get_ist_time()
        
        for g in ghosts:
            daily_score = self._calculate_single_day_score(g, now, is_completed_day=False)
            final_name = self._ensure_ghost_name(g)
            processed_ghosts.append({
                "user_id": g["id"], "full_name": final_name,
                "total_score": daily_score, "questions_answered": (daily_score // 10),
                "temp_pace": 0, "is_ghost": True
            })

        # --- PSYCHOLOGICAL MANIPULATION ---
        processed_ghosts.sort(key=lambda x: x["total_score"], reverse=True)
        
        # 1. God Mode (Force Loss)
        if god_mode:
            for i in range(3):
                processed_ghosts[i]["total_score"] = 600
                processed_ghosts[i]["questions_answered"] = 60

        # 2. Rivalry (Boost to beat user)
        if not god_mode and user_score > 400:
            top = processed_ghosts[0]
            if top["total_score"] < user_score:
                boost = 10 if user_score < 600 else 0
                top["total_score"] = min(600, user_score + boost)
                top["questions_answered"] = top["total_score"] // 10

        # 3. Hope Spot (Lower scores if user is losing)
        if user_score < 200 and not god_mode:
            for p in processed_ghosts[:5]:
                if p["total_score"] > 450:
                    p["total_score"] = random.randint(380, 440)
                    p["questions_answered"] = p["total_score"] // 10

        processed_ghosts.sort(key=lambda x: x["total_score"], reverse=True)
        
        # 4. Assign Dynamic Pace
        for idx, p in enumerate(processed_ghosts):
            is_top = (idx < 3)
            p["average_pace"] = self._calculate_dynamic_pace(p["user_id"], p["total_score"], user_pace, is_top)
            
        return processed_ghosts

    def generate_weekly_ghosts(self, ghosts, user_weekly_score, user_pace=None, god_mode=False):
        """Weekly Leaderboard with strict summation + PsyOps."""
        processed_ghosts = []
        now = self.get_ist_time()
        
        days_to_subtract = now.weekday() 
        start_of_week = now - datetime.timedelta(days=days_to_subtract)
        
        if not ghosts:
            ghosts = [{"id": 1000+i, "full_name": "" } for i in range(49)]

        for g in ghosts:
            total_weekly_score = 0
            for day_offset in range(days_to_subtract + 1):
                target_date = start_of_week + datetime.timedelta(days=day_offset)
                is_today = (target_date.date() == now.date())
                is_full = not is_today
                day_score = self._calculate_single_day_score(g, target_date, is_completed_day=is_full)
                total_weekly_score += day_score
            
            final_name = self._ensure_ghost_name(g)
            processed_ghosts.append({
                "user_id": g["id"], "full_name": final_name,
                "weekly_score": total_weekly_score, "is_ghost": True
            })
            
        processed_ghosts.sort(key=lambda x: x["weekly_score"], reverse=True)

        # --- PSYCHOLOGICAL MANIPULATION (Weekly) ---
        if god_mode:
            days_passed = days_to_subtract + 1
            max_possible = days_passed * 600
            for i in range(3):
                processed_ghosts[i]["weekly_score"] = max_possible
        
        if not god_mode and user_weekly_score > 0:
            top_score = processed_ghosts[0]["weekly_score"]
            if top_score < user_weekly_score:
                 processed_ghosts[0]["weekly_score"] = user_weekly_score + 20 # Rivalry
        
        processed_ghosts.sort(key=lambda x: x["weekly_score"], reverse=True)

        for idx, p in enumerate(processed_ghosts):
             is_top = (idx < 3)
             p["average_pace"] = self._calculate_dynamic_pace(p["user_id"], p["weekly_score"], user_pace, is_top)

        return processed_ghosts
