// Mock Telegram WebApp for Browser Testing
const tg = window.Telegram ? window.Telegram.WebApp : {
    initDataUnsafe: { user: null },
    ready: () => console.log("TG Ready (Mock)"),
    expand: () => console.log("TG Expand (Mock)"),
    MainButton: { hide: () => {} },
    platform: "unknown"
};

// Initialize
try {
    tg.expand();
    tg.ready(); 
    tg.MainButton.hide();
} catch(e) { console.warn("TG Init Error", e); }

// --- CONFIG ---
const API_BASE_URL = "https://elevateaura-bot.onrender.com"; // User's Render URL

console.log("ELEVATE AURA BOT: Script v34 Loaded");

// Visual Probe: Set background to Blue to prove script started
const p = document.getElementById('testCountDisplay');
if(p) { p.innerText = "v34 Start"; p.style.backgroundColor = "cyan"; }

// --- 1. PROCEDURAL GENERATION ENGINE ---

class SeededRandom {
    constructor(seed) {
        this.seed = seed;
    }
    
    // Lehmer RNG
    next() {
        this.seed = (this.seed * 48271) % 2147483647;
        return (this.seed - 1) / 2147483646;
    }

    range(min, max) {
        return Math.floor(this.next() * (max - min + 1)) + min;
    }
}

class NameFactory {
    static firstNames = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan", "Shaurya", "Atharva", "Dhruv", "Rohan", "Kabir"];
    static lastNames = ["Sharma", "Verma", "Gupta", "Malhotra", "Bhat", "Saxena", "Mehta", "Joshi", "Patel", "Singh", "Reddy", "Nair", "Iyer", "Rao", "Kumar"];
    static generate(rng) {
        const first = this.firstNames[rng.range(0, this.firstNames.length - 1)];
        const last = this.lastNames[rng.range(0, this.lastNames.length - 1)];
        return `${first} ${last}`;
    }
}

class GhostEngine {
    constructor(packId) {
        // Weekly Seed: Year + WeekNumber
        const now = new Date();
        const year = now.getFullYear();
        const week = getWeekNumber(now); // Helper needed
        this.seedString = `${year}-W${week}-P${packId}`;
        
        // Hash it
        let hash = 0;
        for (let i = 0; i < this.seedString.length; i++) hash = hash + this.seedString.charCodeAt(i);
        this.rng = new SeededRandom(hash);
        
        this.packId = packId;
    }

    generateScore() {
        // Score Curve: Normal distribution centered around 30-40 (out of 60)
        let baseScore = this.rng.range(10, 50);
        if (this.rng.next() > 0.8) baseScore += this.rng.range(5, 10); 
        if (baseScore > 60) baseScore = 60;
        return baseScore;
    }

    generatePace() {
        return this.rng.range(28, 55); // Seconds
    }

    generateGhosts(count) {
        const ghosts = [];
        for (let i = 0; i < count; i++) {
            ghosts.push({
                full_name: NameFactory.generate(this.rng),
                total_score: this.generateScore(),
                avg_pace: this.generatePace(),
                is_ghost: true
            });
        }
        return ghosts.sort((a, b) => b.total_score - a.total_score);
    }
}

// Helper for Week Number
function getWeekNumber(d) {
    d = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
    d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay()||7));
    var yearStart = new Date(Date.UTC(d.getUTCFullYear(),0,1));
    var weekNo = Math.ceil(( ( (d - yearStart) / 86400000) + 1)/7);
    return weekNo;
}

// --- 2. DATA LAYER ---

async function fetchLeaderboard(packId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/ghosts?pack_id=${packId}`);
        if (!response.ok) throw new Error("API Fail");
        const data = await response.json();
        
        const engine = new GhostEngine(packId);
        
        return data.ghosts.map(g => ({
            ...g,
            full_name: g.name || g.full_name || "Unknown Aspirant",
            total_score: engine.generateScore(), // Client-side hydration
            avg_pace: engine.generatePace(),     // Client-side hydration
            is_ghost: true
        }));

    } catch (e) {
         // ... (Fallback) ...
         const engine = new GhostEngine(packId);
         return engine.generateGhosts(50);
    }
}

// ... (fetchUserStats stays same) ...
// ... (initDashboard stays same) ...

// --- 3. UI RENDERING ---

// ... (renderHeader, updateTopHeader stay same) ...

function renderList(data) {
    const list = document.getElementById('leaderboard'); 
    if(!list) return;
    list.innerHTML = "";
    
    // Show Top 5
    const top5 = data.slice(0, 5);
    
    top5.forEach((p, index) => {
        const isUser = p.is_user;
        const rank = index + 1;
        
        // Style Matching:
        // User: Deep Blue/Indigo bg (like screenshot 'bg-[#2b2b63]')
        // Ghost: Dark Grey/Black (like screenshot 'bg-[#1f2937]')
        const bgClass = isUser ? 'bg-indigo-600 shadow-lg border border-indigo-400' : 'bg-gray-800';
        const textClass = isUser ? 'text-white' : 'text-gray-200';
        const subtitle = isUser ? "Just Started" : `Avg. Pace: ${p.avg_pace || 34}s`;
        
        const el = document.createElement('div');
        el.className = `flex justify-between items-center p-3 rounded-xl mb-2 ${bgClass}`;
        
        // Rank visual: #1, #2 ...
        // User has "YOU" avatar in screenshot?
        // We'll stick to Rank Number but style it nicely.
        
        el.innerHTML = `
            <div class="flex items-center space-x-3">
                 <div class="w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm bg-opacity-20 bg-white text-current">
                    #${rank}
                </div>
                <div>
                     <div class="font-bold text-sm ${textClass}">${p.full_name}</div>
                     <div class="text-[10px] opacity-70 ${textClass}">${subtitle}</div>
                </div>
            </div>
            <div class="font-bold text-yellow-400">${p.total_score} pts</div>
        `;
        list.appendChild(el);
    });
}

async function fetchUserStats(userId) {
    // If Guest
    if (!userId) return null;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/user_data?user_id=${userId}`);
        if (!response.ok) return null; // New user?
        return await response.json();
    } catch (e) {
        console.error("User Fetch Error", e);
        return null;
    }
}


// --- 3. UI RENDERING ---

async function initDashboard(passedUser = null) {
    // DEFENSIVE: Remove legacy visual artifacts if they exist (Cleanup)
    const legacyCard = document.querySelector('.bg-red-900\\/30'); 
    if(legacyCard) legacyCard.remove();

    let user = passedUser;
    
    // --- GUEST MODE LOGIC ---
    // If we passed null (timeout or simple browser open), we still want to show SOMETHING.
    if (!user) {
         // Create a Dummy "Guest" user for visual testing
         user = { id: 0, first_name: "Guest", last_name: "", username: "guest" };
         renderHeader(user.first_name);
         // Don't return, let it proceed to load ghosts!
    } else {
        renderHeader(user.first_name);
    }
    
    // 1. Determine Pack
    // Fetch User Stats to get rating/pack
    const userStats = await fetchUserStats(user.id);
    const packId = userStats ? userStats.pack_id : 10; // Default Pack 10
    
    // 2. Fetch Leaderboard (Ghosts + Real)
    let leaderboard = await fetchLeaderboard(packId);
    
    // 3. Inject User into Leaderboard
    const userEntry = {
        full_name: "You",
        total_score: userStats ? userStats.total_score : 0,
        is_user: true,
        rank: 0 // Will calc
    };
    
    leaderboard.push(userEntry);
    leaderboard.sort((a,b) => b.total_score - a.total_score);
    
    // 4. Calculate Rank
    const rank = leaderboard.findIndex(x => x.is_user) + 1;
    userEntry.rank = rank;
    
    // 5. Render List
    renderList(leaderboard);
    
    // 6. Update Top Header Stats
    updateTopHeader(rank, userEntry.total_score);

    // 7. Render Analytics
    // Calculate Percentile
    const total = leaderboard.length; // ~51
    const betterThan = total - rank;
    const percentile = betterThan / total;
    
    renderAnalytics(userEntry, total, percentile, userStats ? userStats.subscription_status : 'free');
}

function renderHeader(name) {
    const el = document.getElementById('userNameDisplay');
    if(el) el.innerText = `Hello, ${name}`;
}

function renderList(data) {
    const list = document.getElementById('leaderboard'); // Correct ID
    if(!list) return;
    list.innerHTML = "";
    
    // Show Top 10 + User Context
    // Simplification: Show Top 5 + User
    
    const top5 = data.slice(0, 5);
    
    top5.forEach((p, index) => {
        const isUser = p.is_user;
        const rank = index + 1;
        
        const el = document.createElement('div');
        el.className = `flex justify-between items-center p-3 rounded-lg ${isUser ? 'bg-indigo-900/50 border border-indigo-500' : 'bg-gray-800'}`;
        
        el.innerHTML = `
            <div class="flex items-center space-x-3">
                <div class="w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${rank <= 3 ? 'bg-yellow-500 text-black' : 'bg-gray-700 text-gray-300'}">
                    ${rank}
                </div>
                <div>
                     <div class="font-medium text-sm ${isUser ? 'text-indigo-300' : 'text-gray-200'}">${p.full_name}</div>
                     ${p.is_ghost ? '<div class="text-[10px] text-gray-500">Aspirant</div>' : ''}
                </div>
            </div>
            <div class="font-mono font-bold text-yellow-400">${p.total_score}</div>
        `;
        list.appendChild(el);
    });
}

function updateTopHeader(rank, score) {
    const rankEl = document.getElementById('rankDisplay');
    const scoreEl = document.getElementById('scoreDisplay');
    
    if (rankEl) rankEl.innerText = rank > 999 ? "999+" : rank;
    if (scoreEl) scoreEl.innerText = score;
    
    // Update Date/Pack Info
    const dateEl = document.getElementById('dateDisplay');
    if (dateEl) {
        const now = new Date();
        const options = { month: 'long', day: 'numeric' }; // "October 24"
        const month = now.toLocaleString('default', { month: 'long' });
        // Calculate Week of Month roughly
        const week = Math.ceil(now.getDate() / 7);
        const romanWeek = ["I", "II", "III", "IV", "V"][week-1] || "I";
        
        // Pack ID display
        // We don't have packId here easily unless we pass it. 
        // Just show generic.
        
        // Use theme text color instead of hardcoded white
        dateEl.className = "text-[var(--tg-theme-text-color)] font-bold text-sm flex items-center";
        dateEl.innerHTML = `
            <span>${month} ${romanWeek} Week</span> 
        `;
    }
    
    // Question Counter (Progress)
    const testCountEl = document.getElementById('testCountDisplay');
    if (testCountEl) {
         // Default to Done for visual polish
         testCountEl.textContent = "Goal Reached";
         testCountEl.style.color = "#000000"; 
         testCountEl.style.fontWeight = "bold";
         testCountEl.style.backgroundColor = "#10B981";
         testCountEl.style.padding = "2px 8px";
         testCountEl.style.borderRadius = "6px";
    }
}

function renderAnalytics(userEntry, total, percentile, subStatus) {
    const fasterCountEl = document.getElementById('fasterThanCount');
    if (fasterCountEl) {
        const fasterThan = Math.floor(percentile * 5683); // Fake "Total Aspirants" scaling
        fasterCountEl.innerText = fasterThan.toLocaleString();
    }

    // Chart Bars
    const bars = document.querySelectorAll('.dist-bar');
    if (bars.length === 5) {
        // Heights: [Low, Med, High, Med, Low] base
        const heights = [30, 50, 80, 60, 40];
        
        bars.forEach((bar, i) => {
             // +/- 10% variance
             const h = heights[i] + Math.floor(Math.random() * 20 - 10);
             bar.style.height = `${h}%`;
        });

        // Highlight User's Bar
        let userIndex = Math.floor(percentile * 5); 
        userIndex = Math.min(4, Math.max(0, userIndex)); // Clamp 0-4
        
        const targetBar = bars[userIndex]; // Define targetBar correctly
        if (targetBar) {
            targetBar.classList.remove('bg-gray-600');
            targetBar.classList.add('bg-yellow-500');
            targetBar.style.boxShadow = '0 0 10px rgba(234,179,8,0.5)';
        }
    }
}


function renderError(msg) {
    const container = document.getElementById('leaderboard'); 
    if(container) {
        container.innerHTML = `<div class="p-4 text-red-500 font-bold bg-gray-900 rounded">${msg}</div>`;
    }
}


// --- 4. LISTENERS ---
// document.getElementById('upgradeBtn').addEventListener('click', ...); // Keep default

// Global Error Handler
window.onerror = function(msg, url, lineNo, columnNo, error) {
    renderError(`Error: ${msg} (Line ${lineNo})`);
    return false;
};

// Polling mechanism
function waitForUser(attempts = 0) {
    // 1. Priority: URL Parameters
    const urlParams = new URLSearchParams(window.location.search);
    const urlUserId = urlParams.get('user_id');
    const urlName = urlParams.get('name');
    
    if (urlUserId) {
         const fakeUser = {
             id: parseInt(urlUserId),
             first_name: urlName || "Fighter",
             last_name: "",
             username: ""
         };
         initDashboard(fakeUser).catch(e => renderError("Login Error: " + e));
         return;
    }

    // 2. Fallback: Telegram Object
    if (tg.initDataUnsafe?.user) {
        initDashboard(tg.initDataUnsafe.user).catch(e => renderError("TG Init Error: " + e));
    } else if (attempts < 20) {
        setTimeout(() => waitForUser(attempts + 1), 100);
    } else {
        console.warn("User detection timed out.");
        initDashboard(null).catch(e => renderError("Guest Init Error: " + e));
    }
}

// Start
try {
    const probe = document.getElementById('testCountDisplay');
    if(probe) probe.innerText = "v34 Init";
    waitForUser(); 
} catch (e) {
    renderError("Init Failed: " + e.message);
}
