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

    def _calculate_weekly_pace(self, ghost_id, rank, user_pace, total_ghosts):
        """
        Weekly pace psychology — always relative to user's pace.
        Returns clean rounded integer pace (no decimals).
        
        Zones:
          Rank 1-3  (Throne):  Slightly faster than user (pressure)
          Rank 4-7  (Battle):  Neck-and-neck with user
          Rank 8-10 (Hope):    Slower than user (feel superior)
          Rank 11+  (FOMO):    Noticeably slower
        """
        # Deterministic seed for consistency
        today_ord = self.get_ist_time().toordinal()
        try:
            gid_int = int(ghost_id)
        except:
            gid_int = sum(ord(c) for c in str(ghost_id))
        rng = random.Random(gid_int + today_ord + rank)
        
        # Default if no user pace available
        if not user_pace or user_pace < 5:
            return rng.randint(25, 40)
        
        user_pace = int(round(user_pace))  # Clean integer
        
        if rank <= 3:
            # THRONE ZONE: 2-5s faster than user (scary but not impossible)
            offset = rng.randint(2, 5)
            pace = user_pace - offset
            # Floor: never below 12s (unrealistic)
            if pace < 12:
                pace = 12 + rng.randint(0, 2)
        elif rank <= 7:
            # BATTLE ZONE: ±2s of user (neck and neck)
            offset = rng.randint(-2, 2)
            pace = user_pace + offset
        elif rank <= 10:
            # HOPE ZONE: 3-8s slower (user feels faster)
            offset = rng.randint(3, 8)
            pace = user_pace + offset
        else:
            # FOMO ZONE: clearly slower
            offset = rng.randint(6, 15)
            pace = user_pace + offset
        
        # Clamp to realistic range
        if pace < 12: pace = 12
        if pace > 55: pace = 55
        
        return pace

    def generate_weekly_ghosts(self, ghosts, user_weekly_score, user_pace=None, god_mode=False):
        """
        Weekly Leaderboard with DEEP psychological pressure.
        
        Prize-aware zones:
          Rank 1-3:  ₹200/₹120/₹80  → Throne Zone (hardest competition)
          Rank 4-7:  ₹50-₹30         → Battle Zone (tight clustering)
          Rank 8-10: ₹20-₹15         → Hope Zone (always within reach)
          Rank 11+:  No prize         → FOMO Zone (just outside prizes)
        """
        processed_ghosts = []
        now = self.get_ist_time()
        
        # Calculate week progress
        days_to_subtract = now.weekday()  # 0=Mon, 6=Sun
        start_of_week = now - datetime.timedelta(days=days_to_subtract)
        days_passed = days_to_subtract + 1  # How many days of the week so far
        max_possible_score = days_passed * 600  # Theoretical ceiling
        
        if not ghosts:
            ghosts = [{"id": 1000+i, "full_name": "" } for i in range(49)]

        # --- STEP 1: Calculate base weekly scores for all ghosts ---
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

        # --- STEP 2: GOD MODE (Unbeatable - for users who won last week) ---
        if god_mode:
            for i in range(min(3, len(processed_ghosts))):
                processed_ghosts[i]["weekly_score"] = max_possible_score

        # --- STEP 3: PSYCHOLOGICAL ZONE MANIPULATION ---
        if not god_mode and user_weekly_score > 0:
            
            # Find where user WOULD rank naturally
            user_natural_rank = 1
            for p in processed_ghosts:
                if p["weekly_score"] > user_weekly_score:
                    user_natural_rank += 1
            
            # === THRONE ZONE (Rank 1-3): Make Top 3 TOUGH but reachable ===
            # Always ensure 2-3 ghosts are slightly above user when they're near top
            if user_natural_rank <= 5:
                # User is close to podium — make it a FIGHT
                # Rank 1 ghost: user's score + 20-50 pts
                boost_1 = random.Random(now.toordinal() + 1).randint(20, 50)
                target_score_1 = min(user_weekly_score + boost_1, max_possible_score)
                if processed_ghosts[0]["weekly_score"] < target_score_1:
                    processed_ghosts[0]["weekly_score"] = target_score_1
                
                # Rank 2 ghost: user's score + 10-30 pts
                if len(processed_ghosts) > 1:
                    boost_2 = random.Random(now.toordinal() + 2).randint(10, 30)
                    target_score_2 = min(user_weekly_score + boost_2, max_possible_score)
                    if processed_ghosts[1]["weekly_score"] < target_score_2:
                        processed_ghosts[1]["weekly_score"] = target_score_2
                
                # Rank 3 ghost: user's score + 5-20 pts (closest rival)
                if len(processed_ghosts) > 2:
                    boost_3 = random.Random(now.toordinal() + 3).randint(5, 20)
                    target_score_3 = min(user_weekly_score + boost_3, max_possible_score)
                    if processed_ghosts[2]["weekly_score"] < target_score_3:
                        processed_ghosts[2]["weekly_score"] = target_score_3
            
            elif user_natural_rank <= 10:
                # User is in prize zone but NOT podium
                # Make Rank 1 strong but don't crush
                top_score = processed_ghosts[0]["weekly_score"]
                if top_score < user_weekly_score:
                    processed_ghosts[0]["weekly_score"] = user_weekly_score + random.Random(now.toordinal()).randint(30, 80)
                    processed_ghosts[0]["weekly_score"] = min(processed_ghosts[0]["weekly_score"], max_possible_score)
            
            else:
                # User is outside top 10 — RIVALRY to pull them back in
                # Top ghost always ahead
                if processed_ghosts[0]["weekly_score"] < user_weekly_score:
                    processed_ghosts[0]["weekly_score"] = user_weekly_score + 20

            # === BATTLE ZONE (Rank 4-7): Tight clustering ===
            # Make ranks 4-7 very close to each other (anxiety-inducing)
            if len(processed_ghosts) >= 7:
                # Determine the score anchor for battle zone
                # Anchor should be around user's score ± 30 when user is in this range
                if 4 <= user_natural_rank <= 7:
                    battle_anchor = user_weekly_score
                else:
                    # Use natural score of rank 4 as anchor
                    battle_anchor = processed_ghosts[3]["weekly_score"]
                
                for i in range(3, min(7, len(processed_ghosts))):
                    rng_battle = random.Random(now.toordinal() + i + 100)
                    spread = rng_battle.randint(-15, 15)
                    decay = (i - 3) * rng_battle.randint(5, 15)  # Slight decrease per rank
                    new_score = battle_anchor + spread - decay
                    new_score = max(new_score, 0)
                    new_score = min(new_score, max_possible_score)
                    # Only adjust if it makes the zone tighter
                    processed_ghosts[i]["weekly_score"] = new_score

            # === HOPE ZONE (Rank 8-10): Just barely ahead of user ===
            # If user is outside top 10, make rank 8-10 tantalizingly close
            if user_natural_rank > 10 and len(processed_ghosts) >= 10:
                for i in range(7, 10):
                    rng_hope = random.Random(now.toordinal() + i + 200)
                    # Place them just 10-40 pts above user
                    offset = rng_hope.randint(10, 40)
                    hope_score = user_weekly_score + offset
                    hope_score = min(hope_score, max_possible_score)
                    processed_ghosts[i]["weekly_score"] = hope_score

            # === FOMO ZONE (Rank 11): Close to Rank 10 ===
            if len(processed_ghosts) > 10:
                rank_10_score = processed_ghosts[9]["weekly_score"]
                rng_fomo = random.Random(now.toordinal() + 300)
                fomo_gap = rng_fomo.randint(5, 25)
                processed_ghosts[10]["weekly_score"] = max(rank_10_score - fomo_gap, 0)

        # --- STEP 4: HOPE SPOT for low scorers (don't make it hopeless) ---
        if user_weekly_score < 200 and not god_mode:
            for p in processed_ghosts[:5]:
                if p["weekly_score"] > max_possible_score * 0.7:
                    rng_lower = random.Random(p["user_id"])
                    p["weekly_score"] = int(max_possible_score * rng_lower.uniform(0.4, 0.65))

        # --- STEP 5: Final sort + ensure descending order ---
        processed_ghosts.sort(key=lambda x: x["weekly_score"], reverse=True)

        # --- STEP 6: Assign PACE (relative to user, clean integers) ---
        for idx, p in enumerate(processed_ghosts):
            rank = idx + 1
            p["average_pace"] = self._calculate_weekly_pace(
                p["user_id"], rank, user_pace, len(processed_ghosts)
            )

        return processed_ghosts

