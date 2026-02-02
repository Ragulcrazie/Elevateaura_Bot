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

    def generate_weekly_ghosts(self, ghosts, user_weekly_score):
        """
        Generates accumulated scores for the Weekly Leaderboard (Mon-Sun).
        Range: 0 to 4200 points (600 pts/day * 7 days).
        
        The Logic:
        - The 'Invincible Alpha' (Rank 1) is nearly perfect.
        - The 'Top 10' are elite.
        - The User must fight for Rank 10.
        """
        processed_ghosts = []
        now = self.get_ist_time()
        
        # 1. Calculate 'Week Progress' (1.0 = Mon, 7.0 = Sun)
        # Weekday: Mon=0, Sun=6. So we want (weekday + 1).
        day_of_week = now.weekday() + 1 
        daily_progress = self.get_daily_slot_progress() / 6.0 # 0.0 to 1.0 progress within today
        
        # Effective days elapsed (e.g. Wed noon = 2.5 days)
        total_days_progress = (day_of_week - 1) + daily_progress
        
        # Max theoretical score so far: 600 * days
        max_score_so_far = int(total_days_progress * 600)
        
        week_seed = f"{now.strftime('%Y_%W')}"

        week_seed = f"{now.strftime('%Y_%W')}"

        # FALLBACK: If DB returned no ghosts, generate procedural ones
        if not ghosts:
            ghosts = [{"id": 1000+i, "full_name": f"Aspirant {i+1}"} for i in range(50)]
            # Ideally use better names, but this prevents crash/empty list
            names = ["Rahul", "Priya", "Amit", "Sneha", "Vikram", "Anjali", "Rohit", "Pooja", "Karan", "Neha"]
            surnames = ["Sharma", "Verma", "Singh", "Patel", "Gupta", "Kumar", "Yadav", "Das", "Jha", "Mehta"]
            for i, g in enumerate(ghosts):
                rng_name = random.Random(i + int(week_seed.replace("_", "")))
                g["full_name"] = f"{rng_name.choice(names)} {rng_name.choice(surnames)}"

        for i, g in enumerate(ghosts):
            # Seed based on ID + Week (Consistent for whole week)
            ghost_seed = f"{g.get('id', i)}_{week_seed}"
            rng = random.Random(ghost_seed)
            
            # Skill Level (0.0 to 1.0)
            if i < 10:
                skill = 0.92 + (rng.random() * 0.08) # Elites (92-100%)
            else:
                skill = rng.random() * 0.9 # Normals

            # --- SPLIT LOGIC: Previous Days + Today ---
            
            # 1. Previous Days Score (Fully Completed Days)
            completed_days = day_of_week - 1
            max_previous = completed_days * 600
            previous_score = int(max_previous * skill)
            
            # 2. Today's Score (In Progress)
            # Use 'daily_progress' (0.0 to 1.0) to limit max
            # Apply randomness for "Has this ghost played yet today?"
            
            # Chance to have played today: Based on daily_progress
            # e.g. at 9AM (0.25), 25% chance they started.
            # But high skill bots play early.
            
            has_played_fraction = daily_progress # Simple linear
            current_day_max = 600
            
            # Calculate today's theoretical score for this ghost
            today_potential = int(current_day_max * skill * daily_progress)
            
            # Add noise to Today ONLY
            today_noise = rng.randint(-30, 30)
            today_score = max(0, today_potential + today_noise)
            
            # Clamp Today
            if today_score > current_day_max: today_score = current_day_max
            
            # Total
            final_score = previous_score + today_score
            
            # Final Cap check
            total_max_possible = int(day_of_week * 600) # e.g. Mon=600, Tue=1200
            if final_score > total_max_possible: final_score = total_max_possible
            
            # Round to nearest 10
            final_score = (final_score // 10) * 10
            
            processed_ghosts.append({
                "user_id": g.get("id", i),
                "full_name": g.get("full_name") or g.get("name") or "Aspirant",
                "weekly_score": final_score, 
                "is_ghost": True
            })
            
        # --- RIGGING: The Invincible Alpha ---
        # Ensure Rank 1 is always slightly ahead of "Perfect Human Pace" to be the benchmark.
        # But user requested "9 Bots + 1 User". 
        # So we ensure the top 9 are very strong.
        
        processed_ghosts.sort(key=lambda x: x["weekly_score"], reverse=True)
        return processed_ghosts
