const tg = window.Telegram.WebApp;

// Initialize
tg.expand();
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

class GhostEngine {
    constructor(dateStr, testId, packId) {
        // Create a unique numeric seed from inputs
        // Simple hash: Sum of char codes
        const seedString = `${dateStr}-${testId}-${packId}`;
        let hash = 0;
        for (let i = 0; i < seedString.length; i++) hash = hash + seedString.charCodeAt(i);
        
        this.rng = new SeededRandom(hash);
        this.packId = packId;
    }

    generateLeaderboard(size = 50) {
        const ghosts = [];
        
        // Base score for this Pack (e.g., Pack 12 => ~1200 rating => ~120 score range?)
        // Let's assume Pack ID = Rating / 100. So Pack 12 = 1200 Rating.
        // In our new system, max score is 100 per test.
        // We simulate that higher packs assume better performance.
        // Pack 10 (Avg) -> Scores around 40-70
        // Pack 20 (Pro) -> Scores around 80-100
        
        const baseScore = Math.min(this.packId * 5, 80); // Cap base at 80
        
        for (let i = 0; i < size; i++) {
            const name = NameFactory.generate(this.rng);
            
            // Bell Curve Simulation
            // Random variation between -20 and +15
            const variance = this.rng.range(-20, 15);
            let score = baseScore + variance;
            
            // Clamp score between 0 and 100 (Max for one test)
            // Or if we are showing Daily Total (Max 600), we scale it.
            // Let's assume this view is for "Daily Total" so max 600.
            score = Math.floor(score * 6); // Scale to 600-point system roughly
            if (score < 0) score = 0;
            if (score > 600) score = 600;

            ghosts.push({
                rank: 0, // Assigned later
                name: name,
                score: score,
                is_bot: true,
                initials: name.slice(0, 2).toUpperCase()
            });
        }
        
        // Top 3 Heroes (Always High Scorers for this pack)
        ghosts[0].score = Math.min(600, ghosts[0].score + 50);
        ghosts[1].score = Math.min(600, ghosts[1].score + 30);
        
        return ghosts;
    }
}

// --- 2. MAIN LOGIC ---

async function initDashboard() {
    let user = tg.initDataUnsafe?.user;
    
    // Fallback for Desktop/Browser testing
    if (!user) {
        console.warn("No Telegram User detected. Using Guest Mode.");
        user = { id: 0, first_name: "Guest", last_name: "", username: "guest" };
        // We do NOT return here anymore; we proceed as Guest.
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

    // 2. Generate Ghosts
    const today = new Date().toISOString().split('T')[0]; // "2024-01-24"
    const engine = new GhostEngine(today, 1, userData.packId || 10);
    const leaderboard = engine.generateLeaderboard(50); // 50 Ghosts

    // 3. Insert Real User
    const realUserEntry = {
        name: userData.full_name, // Use name from DB
        score: userData.total_score,
        is_bot: false,
        initials: "YOU",
        is_me: true
    };
    leaderboard.push(realUserEntry);

    // 4. Sort & Rank
    leaderboard.sort((a, b) => b.score - a.score);
    
    // Assign Ranks
    leaderboard.forEach((item, index) => {
        item.rank = index + 1;
    });

    // 5. Render
    renderHeader(realUserEntry);
    renderList(leaderboard);
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
                    ${user.is_me ? '<p class="text-[10px] text-indigo-300">That\'s You!</p>' : `<p class="text-[10px] opacity-60">Avg Pace: ${Math.floor(Math.random() * 20 + 20)}s</p>`}
                </div>
            </div>
            <div class="font-bold text-yellow-400 text-sm">${user.score} pts</div>
        `;
        container.appendChild(row);
    });
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
    initDashboard();
} catch (e) {
    renderError("Init Failed: " + e.message);
}

