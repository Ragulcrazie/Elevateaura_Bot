const tg = window.Telegram.WebApp;

// Initialize
tg.expand();
tg.ready(); // Signal that we are initialized
tg.MainButton.hide();

// --- CONFIG ---
const API_BASE_URL = "https://elevateaura-bot.onrender.com"; // User's Render URL
// const API_BASE_URL = "http://localhost:8080"; // For local testing

// --- 1. PROCEDURAL GENERATION ENGINE ---

class SeededRandom {
    constructor(seed) {
        this.seed = seed % 2147483647;
        if (this.seed <= 0) this.seed += 2147483646;
    }

    next() {
        return this.seed = this.seed * 16807 % 2147483647;
    }

    nextFloat() {
        return (this.next() - 1) / 2147483646;
    }

    // Returns integer between min (inclusive) and max (inclusive)
    range(min, max) {
        return Math.floor(this.nextFloat() * (max - min + 1)) + min;
    }

    pick(array) {
        return array[this.range(0, array.length - 1)];
    }
}

class NameFactory {
    static NORTH = ["Amit", "Rahul", "Priya", "Sneha", "Rohit", "Ankit", "Manish", "Pooja", "Ritu", "Vikas"];
    static SOUTH = ["Karthik", "Vikram", "Anjali", "Divya", "Arjun", "Deepa", "Suresh", "Lakshmi", "Ramesh", "Swati"];
    static LAST_NORTH = ["Sharma", "Verma", "Singh", "Gupta", "Mishra", "Joshi", "Yadav", "Tiwari"];
    static LAST_SOUTH = ["Iyer", "Nair", "Reddy", "Menon", "Pillai", "Rao", "Krishnan", "Subramaniam"];
    
    static generate(rng) {
        const type = rng.range(1, 10);
        const region = rng.range(1, 2) === 1 ? 'NORTH' : 'SOUTH';
        
        const first = rng.pick(region === 'NORTH' ? this.NORTH : this.SOUTH);
        
        if (type <= 6) { 
            // 60% Formal: "Amit Sharma"
            const last = rng.pick(region === 'NORTH' ? this.LAST_NORTH : this.LAST_SOUTH);
            return `${first} ${last}`;
        } else if (type <= 8) {
            // 20% Initial: "Amit S."
            const lastInitial = String.fromCharCode(rng.range(65, 90));
            return `${first} ${lastInitial}.`;
        } else {
            // 20% Aspirant: "Rahul_SSC"
            const suffix = rng.pick(["SSC", "Bank", "CGL", "99", "Official", "Target"]);
            return `${first}_${suffix}`;
        }
    }
}

// Helper: Get ISO Week Number
function getWeekNumber(d) {
    d = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
    d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));
    var yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
    var weekNo = Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
    return weekNo;
}

// Helper: Get Roman Numeral for Week of Month (approx)
function getRomanWeekOfMonth(date) {
    const day = date.getDate();
    const week = Math.ceil(day / 7);
    const romans = ["I", "II", "III", "IV", "V"];
    return romans[Math.min(week - 1, 4)];
}

class GhostEngine {
    constructor(packId) {
        // Weekly Seed: Year + WeekNumber
        const now = new Date();
        const year = now.getFullYear();
        const week = getWeekNumber(now);
        this.seedString = `${year}-W${week}-P${packId}`;
        
        // Hash it
        let hash = 0;
        for (let i = 0; i < this.seedString.length; i++) hash = hash + this.seedString.charCodeAt(i);
        this.rng = new SeededRandom(hash);
        
        this.packId = packId;
    }

    // Fetch ghosts from Backend API (Real DB Profiles)
    async fetchCohort() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/ghosts?pack_id=${this.packId}`);
            if (response.ok) {
                const data = await response.json();
                if (data.ghosts && data.ghosts.length > 0) {
                    return data.ghosts.map(g => ({
                        name: g.name,
                        skill: g.base_skill_level || 1200, // Fallback if missing
                        rating: g.base_skill_level,
                        initials: g.name.slice(0, 2).toUpperCase()
                    }));
                }
            }
        } catch (e) {
            console.error("Ghost Fetch Error:", e);
        }
        
        console.warn("Falling back to local ghost generation");
        return this.generateFallbackCohort(50);
    }

    // Fallback: Generate ghosts locally if API fails
    generateFallbackCohort(size = 50) {
        // ... (Original logic as fallback)
        let hash = 0;
        for (let i = 0; i < this.seedString.length; i++) hash = hash + this.seedString.charCodeAt(i);
        const rng = new SeededRandom(hash);

        const ghosts = [];
        for (let i = 0; i < size; i++) {
            const name = NameFactory.generate(rng);
            const skill = rng.range(30, 95); 
            ghosts.push({ name, skill: skill * 20, initials: name.slice(0, 2).toUpperCase() });
        }
        return ghosts;
    }

    // Calculate current scores for the cohort based on Time of Day
    // Ghosts accumulate points throughout the day (0-600 logic)
    getDailyScores(cohort, userScore) {
        const now = new Date();
        // 8 AM to 10 PM activity window (14 hours)
        // 0.0 to 1.0 progress
        const hour = now.getHours();
        const progress = Math.max(0, Math.min(1, (hour - 8) / 14));
        
        // Random daily variance seed (Year-Month-Day)
        const dateStr = now.toISOString().split('T')[0];
        let dailyHash = 0;
        for (let i = 0; i < dateStr.length; i++) dailyHash = dailyHash + dateStr.charCodeAt(i);
        const dailyRng = new SeededRandom(dailyHash);

        return cohort.map(ghost => {
            // Normalize skill (DB is 800-2000, App expects logic 0-100 or absolute)
            // Let's us DB skill directly for 'luck' calculation
            // Normalized 0.5 to 1.5 multiplier
            
            const basePerformance = (ghost.rating || ghost.skill || 1200) / 1200; 
            
            // Daily Performance Variance (+/- 10%)
            const dailyLuck = (dailyRng.range(-10, 10) / 100);
            
            // Ghost Speed/Score Factor
            const performance = Math.min(1.2, Math.max(0.5, basePerformance + dailyLuck));
            
            // Calculate score: Max 600 * Progress * Performance
            let currentScore = Math.floor(600 * progress * performance);
            
            // Cap at 600 strict
            currentScore = Math.min(600, currentScore);
            
            // Round to nearest 10 (as tests are 100 pts)
            currentScore = Math.round(currentScore / 10) * 10;
            
            return {
                ...ghost,
                score: currentScore,
                is_bot: true,
                is_me: false
            };
        });
    }
}

// --- 2. MAIN LOGIC ---

async function initDashboard(passedUser = null) {
    let user = passedUser || tg.initDataUnsafe?.user;
    
    // Fallback for Desktop/Browser testing
    if (!user) {
        // Retry getting user from initData parsing? (Sometimes raw data is available)
        // For now, warn.
        console.warn("No Telegram User detected. Using Guest Mode.");
        user = { id: 0, first_name: "Guest", last_name: "", username: "guest" };
        
        // VISUAL DEBUG: Show error on screen for User to screenshot
        // Only if genuinely missing in a real env
        if (location.search.indexOf("debug") !== -1) { // Only if ?debug=true
             document.getElementById('headerDate').innerText += " (Guest Mode)";
        }
    }

    // 1. Fetch Real User Data
    let userData = null;
    try {
        // Skip API call for Guest (ID 0)
        if (user.id === 0) {
            userData = { full_name: "Guest User", total_score: 0, pack_id: 10 };
        } else {
            const response = await fetch(`${API_BASE_URL}/api/user_data?user_id=${user.id}`, {
                mode: 'cors'
            });
            if (response.ok) {
                userData = await response.json();
            } else {
                console.warn("API Error", response.status);
                // Fallback for dev/demo if API fails
                userData = { full_name: user ? (user.first_name + " " + (user.last_name || "")) : "You", total_score: 50, pack_id: 10 };
            }
        }
    } catch (e) {
        console.error("Network Error", e);
        userData = { full_name: user ? (user.first_name + " " + (user.last_name || "")) : "You", total_score: 50, pack_id: 10 };
    }

    // 2. Weekly Engine Setup
    // Use PackID from DB or Generate Random sticky one for guest
    const packId = userData.pack_id || userData.packId || 17; 
    const engine = new GhostEngine(packId);
    
    // FETCH REAL GHOSTS NOW
    const cohort = await engine.fetchCohort(); 
    
    // 3. Calculate Daily Scores
    const leaderboard = engine.getDailyScores(cohort, userData.total_score);

    // 4. Insert Real User
    const realUserEntry = {
        name: userData.full_name, 
        score: userData.total_score, // Daily Score from DB
        is_bot: false,
        initials: "YOU",
        is_me: true,
        pace: userData.average_pace && userData.average_pace > 0 ? Math.round(userData.average_pace) : 0
    };
    leaderboard.push(realUserEntry);

    // 5. Sort & Rank
    leaderboard.sort((a, b) => b.score - a.score); // Descending
    
    // Assign Ranks
    leaderboard.forEach((item, index) => {
        item.rank = index + 1;
    });

    // 6. Render
    renderHeader(realUserEntry);
    renderList(leaderboard);
    
    // 7. Update Top Header (Date & Progress)
    const qAnswered = userData.questions_answered || 0;
    updateTopHeader(packId, qAnswered);

    // 8. Render Analytics (Competitor Intelligence)
    renderAnalytics(realUserEntry, leaderboard.length, engine, userData.subscription_status);
    
    // 9. Info Modal Listeners
    setupHelpers();
}

function renderAnalytics(userEntry, totalOnBoard, engine, subStatus) {
    const isPro = true; // subStatus === "pro_99" || subStatus === "basic_49";
    // 1. "Faster Than" Logic
    // Simulate a larger pool than just the 50 shown
    const simulatedPool = 1500 + engine.rng.range(0, 500); 
    
    // Calculate Percentile based on rank in the visible leaderboard
    // Rank 1/50 = Top 2% (98th percentile)
    // Rank 25/50 = 50th percentile
    
    // Guard against Divide by Zero
    const total = totalOnBoard > 0 ? totalOnBoard : 1;
    
    // Percentile: 1.0 (Best) to 0.0 (Worst)
    const percentile = Math.max(0, (total - userEntry.rank) / total);
    
    const fasterThan = Math.floor(simulatedPool * percentile);
    const fasterCountEl = document.getElementById('fasterThanCount');
    if (fasterCountEl) {
        // Handle "0 aspirants" case gracefully (say 8-15 if you just joined)
        const fallback = 8 + Math.floor(Math.random() * 8); // 8 to 15
        const displayCount = fasterThan > 0 ? fasterThan : (userEntry.score > 0 ? fallback : 0);
        fasterCountEl.textContent = displayCount.toLocaleString();
    }

    // 2. Bar Chart Dynamic Rendering
    const bars = document.querySelectorAll('.dist-bar');
    if (bars.length === 5) {
        // Reset all
        bars.forEach(bar => {
            bar.className = 'dist-bar w-1/5 bg-gray-600 rounded-t transition-all duration-500';
            bar.style.boxShadow = 'none';
            // Randomize height slightly (bellcurve-ish)
        });

        // Heights: [Low, Med, High, Med, Low] base
        const heights = [30, 50, 80, 60, 40];
        // Add User's effect? No, just random distribution
        bars.forEach((bar, i) => {
             // +/- 10% random variance
             const h = heights[i] + Math.floor(Math.random() * 20 - 10);
             bar.style.height = `${h}%`;
        });

        // Highlight User's Bar
        // 5 Bars = 20% chunks. 
        // Percentile 0.9 (Top 10%) -> Index 4 (Rightmost)
        // Percentile 0.1 (Bottom 10%) -> Index 0 (Leftmost)
        let userIndex = Math.floor(percentile * 5); 
        userIndex = Math.min(4, Math.max(0, userIndex)); // Clamp 0-4

        if (targetBar) {
            targetBar.classList.remove('bg-gray-600');
            targetBar.classList.add('bg-yellow-500');
            targetBar.style.boxShadow = '0 0 10px rgba(234,179,8,0.5)';
        }
    }
    
    // 3. Populate "Weakness" Data (Randomize for realism)
    // List of scary sounding topics
    const TOPICS = [
        "Time Speed Distance", "Data Interpretation", "Syllogism", "Trigonometry", 
        "Seating Arrangement", "Probability", "Mensuration 3D", "Error Detection",
        "Reading Comprehension", "Number Series", "Puzzle (Floor Based)", "Geometry"
    ];
    
    // Pick 2 random topics based on User ID/Engine Seed so they stay consistent for the user
    // We can use engine.rng
    const t1 = TOPICS[engine.rng.range(0, 5)];
    const t2 = TOPICS[engine.rng.range(6, 11)];
    
    // Find the blurred elements (using text content is hard due to blur, so selects by structure)
    // We added them in HTML. We can just set their inner text even if blurred.
    // It adds to the realism if they inspect element.
    const blurRows = document.querySelectorAll('.filter.blur-\\[3px\\] span:first-child');
    if (blurRows.length >= 2) {
        blurRows[0].textContent = t1;
        blurRows[1].textContent = t2;
    }

    // --- PRO UNLOCK LOGIC ---
    if (isPro) {
        // 1. Hide the "Locked Content" overlay
        const lockOverlay = document.querySelector('.absolute.inset-0.z-10');
        if (lockOverlay) lockOverlay.style.display = 'none';

        // 2. Remove Blur from rows
        const blurryDivs = document.querySelectorAll('.filter.blur-\\[3px\\]');
        blurryDivs.forEach(div => {
             div.classList.remove('filter', 'blur-[3px]');
             div.classList.remove('bg-gray-800/50');
             div.classList.add('bg-red-900/40', 'border', 'border-red-800/50'); // Turn them into clear warnings
        });

        // 3. Change Header to "Unlocked"
        const headerBadge = document.querySelector('.bg-red-800');
        if (headerBadge) {
             headerBadge.textContent = "UNLOCKED";
             headerBadge.classList.replace('bg-red-800', 'bg-green-600');
        }
    }
}

function setupHelpers() {
    const infoBtn = document.getElementById('infoBtn');
    const modal = document.getElementById('infoModal');
    const closeBtn = document.getElementById('closeModal');
    
    if (infoBtn && modal) {
        infoBtn.onclick = () => {
             modal.classList.remove('hidden');
             // Inject Debug Data on Open
             const dId = document.getElementById('debugUserId');
             const dPlat = document.getElementById('debugPlatform');
             if(dId) dId.innerText = tg?.initDataUnsafe?.user?.id || "None";
             if(dPlat) dPlat.innerText = tg?.platform || "Unknown";
        };
    }
    if (closeBtn && modal) {
        closeBtn.onclick = () => modal.classList.add('hidden');
    }
}

// --- 3. UI RENDERING ---

function renderError(msg) {
    const container = document.getElementById('leaderboard');
    container.innerHTML = `<div class="p-4 text-center text-red-400 bg-red-900/20 rounded-xl">${msg}</div>`;
}

function renderHeader(userEntry) {
    // Update "Your Rank" card
    try {
        const rankEl = document.querySelector('.text-3xl.font-bold.text-yellow-500');
        const scoreEl = document.querySelector('.text-2xl.font-bold');
        
        if (rankEl) rankEl.textContent = `#${userEntry.rank}`;
        if (scoreEl) scoreEl.textContent = userEntry.score;
    } catch (e) {
        console.warn("Header render failed:", e);
    }
}

function renderList(data) {
    const container = document.getElementById('leaderboard');
    if (!container) return;
    
    container.innerHTML = '';
    
    // Show Top 100 only (though we generated ~51)
    data.slice(0, 100).forEach(user => {
        const row = document.createElement('div');
        // Highlight "Me" with a different background/border
        const bgClass = user.is_me 
            ? 'bg-indigo-900 border border-indigo-500 shadow-lg scale-[1.02]' 
            : 'bg-gray-800'; // Default card color manual fix or rely on css class 'card'
            
        // Use inline style for bg color to override 'card' class if needed, or just append classes
        row.className = `p-3 flex items-center justify-between rounded-xl mb-2 ${user.is_me ? 'bg-indigo-900 border border-indigo-500' : 'bg-[#2d3748]'}`;
        
        row.innerHTML = `
            <div class="flex items-center">
                <span class="font-bold w-8 text-gray-400 text-sm">#${user.rank}</span>
                <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold mr-3 ${user.is_me ? 'bg-yellow-500 text-black' : 'bg-blue-600 text-white'}">
                    ${user.initials}
                </div>
                <div>
                    <p class="font-medium text-sm ${user.is_me ? 'text-yellow-400' : 'text-gray-200'}">${user.name}</p>
                    ${user.is_me 
                        ? `<p class="text-[10px] text-indigo-300">${user.pace ? 'Avg. Pace: ' + user.pace + 's' : 'Just Started'}</p>`
                        : `<p class="text-[10px]" style="color: #a0aec0 !important;">Avg. Pace: ${user.score > 0 ? (50 - Math.floor(user.score/15) + Math.floor(Math.random()*5)) : Math.floor(Math.random()*20 + 30)}s</p>`
                    }
                </div>
            </div>
            <div class="font-bold text-yellow-400 text-sm">${user.score} pts</div>
        `;
        container.appendChild(row);
    });
}

function updateTopHeader(packId, questionsAnswered) {
    const now = new Date();
    const month = now.toLocaleString("default", { month: "long" });
    const romanWeek = getRomanWeekOfMonth(now);
    
    // Header Title: January II Week
    const dateEl = document.getElementById('headerDate');
    if (dateEl) {
        // Ensure Pack ID exists (default if 0 or null)
        const safePackId = packId || Math.floor(now.getDate() % 20) + 10;
        
        // Use theme text color instead of hardcoded white to support Light Mode
        dateEl.className = "text-[var(--tg-theme-text-color)] font-bold text-sm flex items-center";
        dateEl.innerHTML = `
            <span>${month} ${romanWeek} Week</span> 
            <span class="text-xs text-gray-400 ml-2 font-normal">• PACK ${safePackId}</span>
        `;
    }
    
    // Question Counter (Progress)
    const testCountEl = document.getElementById('testCountDisplay') || document.getElementById('testCount');
    
    if (testCountEl) {
        // Enforce max 60
        const displayCount = Math.min((questionsAnswered || 0), 60);
        const isMax = displayCount >= 60;
        
        testCountEl.textContent = isMax ? "Goal Reached" : `Progress: ${displayCount}/60`;
        
        testCountEl.style.color = "#000000"; 
        testCountEl.style.fontWeight = "bold";
        testCountEl.style.backgroundColor = isMax ? "#10B981" : "#fbbf24"; // Green if Done, Amber if Pending
        testCountEl.style.padding = "2px 8px";
        testCountEl.style.borderRadius = "6px";
    }
}

// --- 4. LISTENERS ---
// document.getElementById('upgradeBtn').addEventListener('click', ...); // Keep existing logic

// Global Error Handler
window.onerror = function(msg, url, lineNo, columnNo, error) {
    renderError(`Error: ${msg} (Line ${lineNo})`);
    return false;
};

// Start
try {
    // Polling mechanism to wait for Telegram to inject data
function waitForUser(attempts = 0) {
    // 1. Priority: URL Parameters (Smart Solution)
    const urlParams = new URLSearchParams(window.location.search);
    const urlUserId = urlParams.get('user_id');
    const urlName = urlParams.get('name');
    
    if (urlUserId) {
         // Instant Login!
         const fakeUser = {
             id: parseInt(urlUserId),
             first_name: urlName || "Fighter",
             last_name: "",
             username: ""
         };
         initDashboard(fakeUser);
         return;
    }

    // 2. Fallback: Telegram Object
    if (tg.initDataUnsafe?.user) {
        initDashboard(tg.initDataUnsafe.user);
    } else if (attempts < 20) {
        // Try again in 100ms
        setTimeout(() => waitForUser(attempts + 1), 100);
    } else {
        // Time out
        console.warn("User detection timed out.");
        initDashboard(null);
    }
}

// Start with polling
try {
    waitForUser(); 
} catch (e) {
    renderError("Init Failed: " + e.message);
}
} catch (e) {
    renderError("Init Failed: " + e.message);
}

