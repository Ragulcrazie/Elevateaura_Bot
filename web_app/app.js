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

// Visual Probe: Set background to Green to prove script updated
const p = document.getElementById('testCountDisplay');
if(p) { p.innerText = "v58 INFO"; p.style.backgroundColor = "#3B82F6"; }

// --- 2. DATA LAYER ---
async function fetchLeaderboard(packId, userId) {
    try {
        let url = `${API_BASE_URL}/api/ghosts?pack_id=${packId}`;
        if (userId) url += `&user_id=${userId}`;

        const response = await fetch(url);
        if (!response.ok) throw new Error("API Fail");
        const data = await response.json();
        
        return data.ghosts || [];
    } catch (e) {
         console.error("Leaderboard Fetch Error", e);
         return [];
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
    
    // Show All 50 (User + 49 Ghosts)
    const listItems = data;
    
    listItems.forEach((p, index) => {
        const isUser = p.is_user;
        const rank = index + 1;
        
        // Style Matching:
        // User: Deep Blue/Indigo bg (like screenshot 'bg-[#2b2b63]')
        // Ghost: Dark Grey/Black (like screenshot 'bg-[#1f2937]')
        const bgClass = isUser ? 'bg-indigo-600 shadow-lg border border-indigo-400' : 'bg-gray-800';
        const textClass = isUser ? 'text-white' : 'text-gray-200';
        const subtitle = isUser ? "Just Started" : `Avg. Pace: ${p.avg_pace || 34}s`;
        
        const el = document.createElement('div');
        let rankHtml = '';
        let rankBgClass = 'bg-gray-700 text-gray-300'; // Default
        
        if (rank === 1) {
            rankHtml = '🥇';
            rankBgClass = 'bg-yellow-500 text-black shadow-lg shadow-yellow-500/50 scale-110 border-2 border-yellow-200';
        } else if (rank === 2) {
            rankHtml = '🥈';
            rankBgClass = 'bg-gray-300 text-black shadow-lg shadow-gray-400/50 scale-105 border-2 border-gray-100';
        } else if (rank === 3) {
            rankHtml = '🥉';
            rankBgClass = 'bg-amber-700 text-white shadow-lg shadow-amber-800/50 scale-105 border-2 border-amber-600';
        } else {
            rankHtml = `#${rank}`;
            rankBgClass = 'bg-gray-700 text-gray-300';
        }

        // Apply visual distinction to the row itself for top 3
        let rowClass = `flex justify-between items-center p-3 rounded-xl mb-2 ${bgClass}`;
        
        el.className = rowClass;
        
        el.innerHTML = `
            <div class="flex items-center space-x-3">
                 <div class="w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${rankBgClass} transition-all duration-300">
                    ${rankHtml}
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
    // Try to get name from Telegram object first if available even if initDashboard was called with null
    if (!user && tg.initDataUnsafe?.user) {
        user = tg.initDataUnsafe.user;
    }

    if (!user) {
         // Create a Dummy "Guest" user for visual testing
         user = { id: 0, first_name: "Guest", last_name: "", username: "guest" };
    }
    
    // 1. Determine Pack
    // Fetch User Stats to get rating/pack
    const userStats = await fetchUserStats(user.id);
    const packId = userStats ? userStats.pack_id : 10; // Default Pack 10
    
    // RE-VERIFY NAME from DB if available (most reliable)
    // Sometimes Telegram initData is missing in simple web preview, but we have ID
    if (userStats && userStats.full_name && userStats.full_name !== "Unknown Aspirant") {
        user.first_name = userStats.full_name;
    }

    renderHeader(user.first_name || "Fighter");
    
    // 2. Fetch Leaderboard (Ghosts + Real)
    let leaderboard = await fetchLeaderboard(packId, user.id);
    
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
    updateTopHeader(rank, userEntry.total_score, userStats ? userStats.questions_answered : 0);

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



function updateTopHeader(rank, score, questionsAnswered) {
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
         // Cap at 60 for display safety
         const displayVal = Math.min(questionsAnswered, 60);
         testCountEl.textContent = `${displayVal}/60`; // e.g. "10/60"
         
         // Color Logic
         testCountEl.style.color = "#FFFFFF"; // White text
         testCountEl.style.fontWeight = "bold";
         testCountEl.style.padding = "2px 8px";
         testCountEl.style.borderRadius = "6px";
         
         if (displayVal === 0) {
             testCountEl.style.backgroundColor = "#6B7280"; // Gray for 0
         } else if (displayVal < 60) {
             testCountEl.style.backgroundColor = "#F59E0B"; // Amber/Orange for In Progress
         } else {
             testCountEl.style.backgroundColor = "#10B981"; // Green for Done (60/60)
         }
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

    // --- TRUE POTENTIAL LOGIC (Psychological Hook) ---
    // Calculate simple heuristic for potential if we don't have deep data
    const currentScore = userEntry.total_score || 0;
    
    // Formula: Close 40% of the gap to 600, but ensure at least +50 boost
    // If score is very low (e.g. 0), potential is 120.
    const gap = 600 - currentScore;
    let potentialScore = Math.floor(currentScore + (gap * 0.45)); 
    
    // Safety caps
    if (potentialScore > 600) potentialScore = 600;
    if (potentialScore < currentScore + 40) potentialScore = currentScore + 40; // Ensure visible gap
    if (potentialScore > 600) potentialScore = 600; // Cap again

    const pointsLost = potentialScore - currentScore;

    // Render DOM
    const currEl = document.getElementById('potential_current');
    const potEl = document.getElementById('potential_max');
    const gapEl = document.getElementById('potential_gap');
    const unlockBtn = document.getElementById('unlockPotentialBtn');

    if (currEl) currEl.innerText = currentScore;
    if (potEl) {
        // Count up animation for potential
        let start = currentScore;
        const duration = 1000;
        const startTime = performance.now();
        
        function animate(time) {
            const elapsed = time - startTime;
            const progress = Math.min(elapsed / duration, 1);
            // Ease out quart
            const ease = 1 - Math.pow(1 - progress, 4);
            
            const currentVal = Math.floor(start + (pointsLost * ease));
            potEl.innerText = currentVal;
            
            if (progress < 1) requestAnimationFrame(animate);
        }
        requestAnimationFrame(animate);
    }
    if (gapEl) gapEl.innerText = `${pointsLost} points`;

    // Button Action
    if (unlockBtn) {
        unlockBtn.onclick = () => {
            // Trigger Telegram Payment or Info Modal
            // data-product="potential_analysis"
            tg.MainButton.setText("UNLOCK ANALYSIS (500 Stars)");
            tg.MainButton.show();
            // Just simulate click for now or open info modal
            document.getElementById('upgradeBtn').click(); // Reuse existing flow
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
// Info Button Modal Logic
const infoBtn = document.getElementById('infoBtn');
const infoModal = document.getElementById('infoModal');
const closeModal = document.getElementById('closeModal');

if (infoBtn && infoModal && closeModal) {
    const toggleModal = () => infoModal.classList.toggle('hidden');
    infoBtn.addEventListener('click', toggleModal);
    closeModal.addEventListener('click', toggleModal);
    
    // Close on backdrop click
    infoModal.addEventListener('click', (e) => {
        if (e.target === infoModal) toggleModal();
    });
}

// Button Handler for specific ID
const upgradeBtnMain = document.getElementById('upgradeBtn');
if (upgradeBtnMain) {
    upgradeBtnMain.addEventListener('click', () => {
        // In real app, this calls /create_invoice
        console.log("Upgrade Clicked");
        
        // MVP: Show Telegram Main Button as "Pay"
        tg.MainButton.setText("PAY 500 STARS ⭐");
        tg.MainButton.show();
        
        // Optional: Shake effect or specific logic
        tg.HapticFeedback.notificationOccurred('success');
        
        // Show Payment Modal or Alert
        // For now, let's just use native confirm to simulate
        // const confirmed = confirm("Upgrade to Premium for Deep Analytics?");
    });
}

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
