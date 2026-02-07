// Mock Telegram WebApp for Browser Testing
const TgApp = (typeof window.tg !== 'undefined') ? window.tg : (window.Telegram ? window.Telegram.WebApp : {
    initDataUnsafe: { user: null },
    ready: () => console.log("TG Ready (Mock)"),
    expand: () => console.log("TG Expand (Mock)"),
    MainButton: { hide: () => {} },
    platform: "unknown"
});

// Initialize
try {
    TgApp.expand();
    TgApp.ready(); 
    TgApp.MainButton.hide();
} catch(e) { console.warn("TG Init Error", e); }

// --- CONFIG ---
const API_BASE_URL = "https://elevateaura-bot.onrender.com"; // User's Render URL

// Global State
let NOTES_MAPPING = null;
let currentMode = 'daily'; // 'daily' or 'weekly'
let currentUserEntry = null; // Store for global access
const GITHUB_ASSETS_BASE = "https://raw.githubusercontent.com/Ragulcrazie/Elevateaura_Bot/main/";

console.log("ELEVATE AURA BOT: Script v105 BACKEND-LOGIC Loaded");
 
 // Visual Probe: Set background to unique color to prove script updated
 const p = document.getElementById('testCountDisplay');
 if(p) { p.innerText = "v105 OK"; p.style.backgroundColor = "#8b5cf6"; } // Violet

// --- 2. DATA LAYER ---
async function fetchLeaderboard(packId, userId, timestamp) {
    try {
        let url = `${API_BASE_URL}/api/ghosts?pack_id=${packId}&mode=${currentMode}`;
        if (userId) url += `&user_id=${userId}`;
        if (timestamp) url += `&t=${timestamp}`;

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
        
        // Requirement 7: Only show pace for Top 3 OR User
        // Requirement 7: Only show pace for Top 3 OR User
        let subtitle = "Aspirant"; 
        
        // Safe Pace Logic
        let rawPace = p.average_pace || p.avg_pace;
        if (!rawPace) {
             let seed = parseInt(p.user_id || p.id || 0);
             // Mix in Name hash to guarantee uniqueness even if IDs collide or are 0
             if (p.full_name) {
                 for(let i=0; i<p.full_name.length; i++) seed += p.full_name.charCodeAt(i);
             }
             rawPace = 27 + (seed % 19); 
        }
        const dispPace = Number(rawPace).toFixed(1).replace('.0', '');

        if (isUser) {
            subtitle = `⚡ Pace: ${dispPace}s`;
        } else if (rank <= 3) {
            subtitle = `⚡ Pace: ${dispPace}s`; 
        }
        
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
        
        // Only show ₹600 prize on Weekly Grand Prix (not Daily Rush)
        // currentMode is set by switchTab() in index.html
        const isWeeklyMode = (typeof currentMode !== 'undefined' && currentMode === 'weekly');
        const showPrize = (rank === 1 && isWeeklyMode);
        
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
            <div class="font-bold ${rank === 1 ? 'text-green-400' : 'text-yellow-400'}">
                ${p.total_score} pts${showPrize ? ' <span class="text-[10px] text-green-300">💰₹600</span>' : ''}
            </div>
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

async function initDashboard(passedUser = null, timestamp = null) {
    // DEFENSIVE: Remove legacy visual artifacts if they exist (Cleanup)
    const legacyCard = document.querySelector('.bg-red-900\\/30'); 
    if(legacyCard) legacyCard.remove();

    let user = passedUser;
    
    // --- GUEST MODE LOGIC ---
    // If we passed null (timeout or simple browser open), we still want to show SOMETHING.
    // Try to get name from Telegram object first if available even if initDashboard was called with null
    if (!user && TgApp.initDataUnsafe?.user) {
        user = TgApp.initDataUnsafe.user;
    }

    if (!user) {
         // Create a Dummy "Guest" user for visual testing
         user = { id: 0, first_name: "Aspirant", last_name: "", username: "guest" };
    }
    
    // 0. Pre-load Notes Mapping (Background)
    loadNotesMapping();
    
    // 1. Determine Pack
    // Fetch User Stats to get rating/pack
    let userStats = null;
    try {
        userStats = await fetchUserStats(user.id);
    } catch (e) {
        console.warn("User stats fetch failed (Network/Offline?), loading Default View", e);
    }
    
    const packId = userStats ? userStats.pack_id : 10; // Default Pack 10
    
    // RE-VERIFY NAME from DB if available (most reliable)
    // Sometimes Telegram initData is missing in simple web preview, but we have ID
    if (userStats && userStats.full_name && userStats.full_name !== "Unknown Aspirant") {
        user.first_name = userStats.full_name;
    }

    renderHeader(user.first_name || "Fighter");
    
    // 2. Fetch Leaderboard (Ghosts + Real)
    let leaderboard = [];
    try {
        leaderboard = await fetchLeaderboard(packId, user.id, timestamp);
    } catch (e) {
         console.warn("Leaderboard fetch failed. Using fallback.", e);
         // Fallback dummy leaderboard so UI doesn't look empty
         leaderboard = [
             { full_name: "Ghost Leader", total_score: 150, is_user: false },
             { full_name: "Elite Player", total_score: 120, is_user: false }
         ]; 
    }
    
    // NOTE: We trust the backend (main.py + RankEngine) to provide 49 ghosts/rivals.
    // If fewer are returned, we display what we have rather than inventing fake users on client.
    
    // 3. Inject User into Leaderboard
    const userEntry = {
        full_name: "You",
        total_score: userStats ? userStats.total_score : 0,
        is_user: true,
        id: user.id, // Needed for payment
        rank: 0, // Will calc
        average_pace: userStats ? userStats.average_pace : 34
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
    
    renderAnalytics(userEntry, total, percentile, userStats);

    // 7.5 Check and Display Ads (Free Users Only)
    try {
        await checkAndShowAd(user.id, userStats);
    } catch (e) {
        console.warn('Ad check failed (non-critical):', e);
    }

    // 8. Update Wallet UI
    const walletEl = document.getElementById('walletBalance');
    if(walletEl && userStats) {
        walletEl.innerText = userStats.wallet_stars || 0;
    }

    // 9. Update Red Dot (Lead Trap)
    const dot = document.getElementById('pendingActionDot');
    if(dot) {
        // Condition: High Score (>200) AND No Lead Captured Yet
        const hasScore = (userStats && userStats.total_score > 200);
        const hasLead = (userStats && userStats.lead_data); // exists
        
        if (hasScore && !hasLead) {
            dot.classList.remove('hidden');
        } else {
            dot.classList.add('hidden');
        }
    }
    
    // Store globally
    currentUserEntry = userEntry;
}

function renderHeader(name) {
    const el = document.getElementById('userNameDisplay');
    if(el) {
        el.innerHTML = `Hello, ${name} <button onclick="editProfileName()" class="opacity-50 hover:opacity-100 text-xs bg-gray-700 px-1 rounded animate-pulse">✏️</button>`;
    }
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

function renderAnalytics(userEntry, total, percentile, userStats) {
    const subStatus = userStats ? userStats.subscription_status : 'free';
    
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

    // --- TRUE POTENTIAL LOGIC (REAL) ---
    // Use API data if available, otherwise fallback to heuristic
    const currentScore = userEntry.total_score || 0;
    const questionsAnswered = userStats ? userStats.questions_answered : 0;
    
    // Dynamic Denominator Logic
    // If they haven't finished 60 questions, showing /600 is confusing.
    // Instead, show / (questionsAnswered * 10) OR project it.
    // Let's settle on: If < 10 questions, assume 100 base. If < 60, use actual potential max so far.
    // Actually, user wants to see "Potential" for the day. 
    // BUT if they only played 1 test (10 Qs), their max possible was 100.
    // So "Potential 100 / 600" is misleading. It should be "Potential 100 / 100" (for that test).
    
    let potentialBase = 600;
    if (questionsAnswered > 0 && questionsAnswered < 60) {
        // If they are mid-way, show potential relative to what they played + future?
        // No, simplest: Show potential relative to what they played.
        potentialBase = questionsAnswered * 10;
        // Edge case: If they answered 0? Base 100.
    } else if (questionsAnswered === 0) {
        potentialBase = 100;
    }
    
    // If we want to show True Daily Potential (600), we need to project.
    // "You scored 40/100. Your daily potential is 400/600".
    // Let's stick to the User Request: "user just complete 1 test (100 only)".
    // So if they played 1 test, max is 100.
    
    let potentialScore = 0;
    let weakSpots = [];

    if (userStats && userStats.potential_score) {
        potentialScore = userStats.potential_score;
        weakSpots = userStats.weak_spots || [];
    } else {
        // Fallback Heuristic
        const gap = 600 - currentScore;
        potentialScore = Math.floor(currentScore + (gap * 0.45)); 
        if (potentialScore > 600) potentialScore = 600;
        if (potentialScore < currentScore + 40) potentialScore = currentScore + 40;
        if (potentialScore > 600) potentialScore = 600; 
    }
    
    // Ensure potential is never less than current (rare edge case)
    if (potentialScore < currentScore) potentialScore = currentScore;
    
    // Cap potential at base
    if (potentialScore > potentialBase) potentialScore = potentialBase;

    const pointsLost = potentialScore - currentScore;

    // Render DOM
    const currEl = document.getElementById('potential_current');
    const potEl = document.getElementById('potential_max');
    const gapEl = document.getElementById('potential_gap');
    const unlockBtn = document.getElementById('upgradeBtn');
    
    // UPDATE DENOMINATORS
    const currBaseEl = currEl?.parentElement?.querySelector('.font-mono');
    const potBaseEl = potEl?.parentElement?.querySelector('.font-mono');
    
    if(currBaseEl) currBaseEl.innerText = `/${potentialBase}`;
    if(potBaseEl) potBaseEl.innerText = `/${potentialBase}`;
    
    // New: Insight Text Element
    const insightTextEl = document.querySelector('.border-l-2.border-red-500 p'); 

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

    // Dynamic Insight Text
    if (insightTextEl) {
        if (weakSpots.length > 0) {
            let topic1 = weakSpots[0].topic;
            let topic2 = weakSpots.length > 1 ? weakSpots[1].topic : null;
            
            // OBFUSCATE IF FREE
            if (subStatus !== 'premium') {
                topic1 = "🔒 Locked Topic";
                if (topic2) topic2 = "🔒 Locked Topic";
            }
            
            let msg = `You lost <span class="text-white font-bold">${pointsLost} points</span> mainly in <span class="text-yellow-400 font-bold">${topic1}</span>`;
            if (topic2) msg += ` and <span class="text-yellow-400 font-bold">${topic2}</span>`;
            
            if (subStatus !== 'premium') {
                 msg += `. <span class="italic text-gray-400">Unlock Premium to reveal & fix them.</span>`;
            } else {
                 msg += `. Your accuracy in these high-value topics is dragging you down.`;
            }
            
            insightTextEl.innerHTML = msg;
        } else if (pointsLost > 0) {
            // Generic but with correct points
             insightTextEl.innerHTML = `You left <span class="text-white font-bold">${pointsLost} points</span> on the table due to fixable weak spots. Speed is key, but accuracy is Queen.`;
        } else {
             // Perfect Score?
             insightTextEl.innerHTML = `You are playing at <span class="text-green-400 font-bold">Max Potential</span>! Keep maintaining this streak.`;
        }
    }

    // Button Action
    if (unlockBtn) {
        if (subStatus === 'premium') {
            // Premium users: Hide the button entirely for clean UI
            // They use AI Coach in Telegram chat instead
            unlockBtn.style.display = 'none';
        } else {
            // FREE VIEW (Ad-Supported Unlock)
            unlockBtn.innerHTML = `<span class="mr-2 text-lg">🎥</span> Watch Ad & Earn +1 ⭐`;
            unlockBtn.classList.remove('bg-indigo-600');
            unlockBtn.classList.add('bg-green-600', 'animate-pulse'); // Make it pop

            unlockBtn.onclick = () => {
                if(TgApp.HapticFeedback) TgApp.HapticFeedback.impactOccurred('medium');
                
                unlockBtn.innerHTML = "Loading Ad...";
                
                launchSmartAd(() => {
                     // Ad Success Callback - Call API to persist reward
                     fetch(`${API_BASE_URL}/api/reward_ad`, {
                         method: 'POST',
                         body: JSON.stringify({ user_id: userEntry.id }),
                         headers: { 'Content-Type': 'application/json' }
                     })
                     .then(res => res.json())
                     .then(data => {
                         if (data.success) {
                             const balEl = document.getElementById('walletBalance');
                             if(balEl) {
                                  balEl.innerText = data.new_balance; 
                                  alert("🎁 Reward: +1 Star Added! Insights Unlocked.");
                             }
                         } else {
                             alert("Reward Error: " + (data.error || "Please try again"));
                         }
                     })
                     .catch(e => {
                         console.error("Ad Reward API failed", e);
                         // Optimistic update if network fails? No, better warn.
                         alert("⚠️ Network Error saving reward. Check connection.");
                     });

                     // Reset Button
                     unlockBtn.innerHTML = `<span class="mr-2 text-lg">🎥</span> Watch Ad Again (+1 ⭐)`;
                });
            };
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
    // Close on backdrop click
    infoModal.addEventListener('click', (e) => {
        if (e.target === infoModal) toggleModal(); 
    });
    
    // --- RED DOT LOGIC for Info Button ---
    // Remove old listener if any (implicit by re-binding logic here isn't enough, but assuming fresh load)
    // We override the click.
    infoBtn.onclick = (e) => {
        e.preventDefault();
        const dot = document.getElementById('pendingActionDot');
        if (dot && !dot.classList.contains('hidden')) {
             // Open CAPTURE Modal (The Trap)
             openCaptureModal();
        } else {
             // Open INFO Modal
             toggleModal();
        }
    };
}

// --- LEAD CAPTURE LOGIC ---
let appLeadData = { exam: null, mode: null, phone: null };

function openCaptureModal() {
    document.getElementById('captureModal').classList.remove('hidden');
    if(TgApp.HapticFeedback) TgApp.HapticFeedback.impactOccurred('heavy');
}

function closeCaptureModal() {
    document.getElementById('captureModal').classList.add('hidden');
}

function selectLeadOption(type, value) {
    appLeadData[type] = value;
    
    // Visual Feedback
    const step = type === 'exam' ? 'captureStep1' : 'captureStep2';
    const nextStep = type === 'exam' ? 'captureStep2' : 'captureStep3';
    const nextDot = type === 'exam' ? 'pdot2' : 'pdot3';
    
    // Highlight Selected
    const sector = type === 'exam' ? '.lead-opt-exam' : '.lead-opt-mode';
    document.querySelectorAll(sector).forEach(btn => {
        if(btn.innerText.includes(value)) {
            btn.classList.add('bg-indigo-600', 'border-indigo-400');
            btn.classList.remove('bg-gray-700', 'border-gray-600');
        } else {
            btn.classList.remove('bg-indigo-600', 'border-indigo-400');
            btn.classList.add('bg-gray-700', 'border-gray-600');
        }
    });

    if(TgApp.HapticFeedback) TgApp.HapticFeedback.selectionChanged();

    // Auto Advance
    setTimeout(() => {
        document.getElementById(step).classList.add('hidden');
        document.getElementById(nextStep).classList.remove('hidden');
        document.getElementById(nextDot).classList.add('bg-yellow-500');
        document.getElementById(nextDot).classList.remove('bg-gray-600');
    }, 400);
}

function submitLead() {
    const phoneEl = document.getElementById('leadPhone');
    const phone = phoneEl.value.trim();
    
    if (phone.length < 10) {
        alert("Please enter a valid 10-digit number.");
        phoneEl.focus();
        if(TgApp.HapticFeedback) TgApp.HapticFeedback.notificationOccurred('error');
        return;
    }
    
    appLeadData.phone = phone;
    
    // Show Loading
    const btn = document.querySelector('#captureStep3 button');
    const originalText = btn.innerText;
    btn.innerText = "Generating Report...";
    
    // API Call
    if (currentUserEntry && currentUserEntry.id) {
        fetch(`${API_BASE_URL}/api/save_lead`, {
            method: 'POST',
            body: JSON.stringify({ user_id: currentUserEntry.id, lead_data: appLeadData }),
            headers: { 'Content-Type': 'application/json' }
        })
        .then(res => res.json())
        .then(data => {
            if(data.status === 'success') {
                if(TgApp.HapticFeedback) TgApp.HapticFeedback.notificationOccurred('success');
                
                // --- SMART REWARD TRIGGER ---
                closeCaptureModal();
                const dot = document.getElementById('pendingActionDot');
                if(dot) dot.classList.add('hidden'); 
                
                // Launch Ad sequence immediately after phone number submission
                alert("✅ Report Ready! Watch a short ad to unlock your detailed analysis.");
                
                launchSmartAd(() => {
                     const balEl = document.getElementById('walletBalance');
                     if(balEl) {
                          let bal = parseInt(balEl.innerText);
                          if(isNaN(bal)) bal = 0;
                          balEl.innerText = bal + 1; 
                          alert("🎁 Ad Watched! +1 Star Added to Wallet.");
                     }
                });
            } else {
                 alert("Error: " + (data.error || "Server Busy"));
                 btn.innerText = originalText;
            }
        })
        .catch(err => {
             console.error(err);
             alert("Network Error. Try again.");
             btn.innerText = originalText;
        });
    } else {
        alert("User ID missing. Reload.");
    }
}

// Button Handler for specific ID
const upgradeBtnMain = document.getElementById('upgradeBtn');
if (upgradeBtnMain) {
    upgradeBtnMain.addEventListener('click', () => {
        // Use the Telegram Main Button as a 'Confirm' for redemption
        TgApp.MainButton.setText("REDEEM PREMIUM (99 ⭐)");
        TgApp.MainButton.show();
        
        TgApp.MainButton.onClick(() => {
            TgApp.MainButton.hide();
            // Trigger the existing logic from index.html
            if (window.triggerPremiumRedemption) {
                window.triggerPremiumRedemption();
            } else {
                alert("Please reload the app.");
            }
        });
    });
}

// Global Error Handler
window.onerror = function(msg, url, lineNo, columnNo, error) {
    renderError(`Error: ${msg} (Line ${lineNo})`);
    return false;
};

// --- NEW LOGIC FOR V2 ---

function switchTab(mode) {
    if (currentMode === mode) return;
    currentMode = mode;
    
    // Update UI btns
    const btnDaily = document.getElementById('tabDaily');
    const btnWeekly = document.getElementById('tabWeekly');
    
    if (mode === 'daily') {
        btnDaily.className = "flex-1 py-1 text-xs font-bold rounded-md bg-gray-600 text-white shadow transition-all";
        btnWeekly.className = "flex-1 py-1 text-xs font-bold rounded-md text-gray-400 hover:bg-gray-700 transition-all";
        document.getElementById('lbTitle').innerText = "Today's Top Aspirants";
    } else {
        btnWeekly.className = "flex-1 py-1 text-xs font-bold rounded-md bg-yellow-600 text-white shadow transition-all";
        btnDaily.className = "flex-1 py-1 text-xs font-bold rounded-md text-gray-400 hover:bg-gray-700 transition-all";
        document.getElementById('lbTitle').innerText = "Grand Prix Leaders (Mon-Sun)";
    }
    
    // Re-fetch with cache bust
    const timestamp = new Date().getTime();
    
    if (TgApp.initDataUnsafe?.user) {
        initDashboard(TgApp.initDataUnsafe.user, timestamp);
    } else if (currentUserEntry) {
         // Create dummy user obj from stored entry
         initDashboard({ id: currentUserEntry.id, first_name: currentUserEntry.full_name }, timestamp);
    } else {
        initDashboard(null, timestamp);
    }
}

function triggerMaintenancePopup() {
    if(TgApp.HapticFeedback) TgApp.HapticFeedback.notificationOccurred('error');
    alert("⚠️ Withdrawal Paused for Compliance Upgrade.\n\nDue to new RBI Digital Wallet guidelines, cash withdrawals are temporarily suspended. Your balance is safe.\n\nCheck back in 48 hours.");
}

function triggerRedemption() {
    if(TgApp.HapticFeedback) TgApp.HapticFeedback.impactOccurred('medium');
    
    const balance = parseInt(document.getElementById('walletBalance').innerText);
    
    if (balance < 75) {
        alert(`Insufficient Balance!\n\nYou have ${balance} Stars.\nNeed 75 Stars for a 7-Day Pass.\n\nPlay more to earn.`);
        return;
    }
    
    const confirmRedeem = confirm(`💎 Redeem Reward?\n\nSpend 75 Stars to extend your Premium Validation by 7 Days?\n\nCurrent Balance: ${balance}`);
    
    if (confirmRedeem) {
        // Call API
        // For MVP, just alert success
        alert("✅ Success! Subscription Extended.\n\n(This is a simulation. In prod, this deducts stars and updates DB).");
        // Update UI locally
        document.getElementById('walletBalance').innerText = balance - 75;
    }
}

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
    if (TgApp.initDataUnsafe?.user) {
        initDashboard(TgApp.initDataUnsafe.user).catch(e => renderError("TG Init Error: " + e));
    } else if (attempts < 20) {
        setTimeout(() => waitForUser(attempts + 1), 100);
    } else {
        console.warn("User detection timed out.");
        // FORCE INIT with NULL (which becomes Guest)
        initDashboard(null).catch(e => renderError("Guest Init Error: " + e));
    }
}


// --- NEW HELPER: Load Notes Mapping ---
async function loadNotesMapping() {
    if (NOTES_MAPPING) return; // Already loaded
    try {
        const res = await fetch(GITHUB_ASSETS_BASE + "assets/notes_topic_language_mapping.json");
        NOTES_MAPPING = await res.json();
        console.log("Notes Mapping Loaded:", Object.keys(NOTES_MAPPING).length);
    } catch (e) {
        console.error("Failed to load notes mapping:", e);
    }
}

// --- AD INTEGRATION: Check and Display Monetag Ads ---
// --- SMART AD MEDIATION (Adsgram First -> Monetag Backup) ---

async function launchSmartAd(onReward) {
    if(TgApp.HapticFeedback) TgApp.HapticFeedback.impactOccurred('medium');
    
    // 1. Try ADSGRAM (High CPM Video)
    if (window.Adsgram) {
        try {
            const AdController = window.Adsgram.init({ blockId: "22529" });
            
            console.log("🎬 Launching Adsgram...");
            await AdController.show();
            
            // Success!
            console.log("✅ Adsgram Reward Earned");
            onReward();
            return;
            
        } catch (e) {
            console.warn("⚠️ Adsgram Failed/Skipped:", e);
            // Fallthrough to Monetag
        }
    } else {
        console.warn("⚠️ Adsgram SDK missing");
    }

    // 2. Fallback: MONETAG REWARDED (High Fill Rate)
    console.log("🎬 Launching Monetag Fallback...");
    
    if (typeof window.show_10557666 === 'function') {
        try {
            // EXPLICIT REWARDED CALL
            // We use the Promise-based return which typically indicates Rewarded completion
            window.show_10557666().then(() => {
                console.log("✅ Monetag Reward Earned");
                onReward();
            }, (e) => {
                console.warn("❌ Monetag Ad Closed/Failed", e);
                // Optional: Still reward if it was a close? No, strict.
                alert("Ad was closed or failed to load. No reward.");
            });
            
        } catch (e) {
            console.error("❌ All Ads Failed:", e);
            alert("No ads available right now. Please try again later.");
        }
    } else {
        console.error("❌ Monetag SDK missing");
        onReward(); // Emergency Access
    }
}

// Replaces old checkAndShowAd (Auto-show logic removed in favor of User-Initiated)
// We now only use this to potentially pre-load or check status, but mostly we rely on the button click.
async function checkAndShowAd(userId, userStats) {
    // Legacy function kept for API compatibility, but logic moved to 'Unlock' button
    console.log("Ad System Ready. Waiting for user trigger.");
}

function displayMonetagAd(code) {
    // Deprecated in V3 Smart System
}

// Start
try {
    const probe = document.getElementById('testCountDisplay');
    if(probe) probe.innerText = "v34 Init";
    waitForUser(); 
} catch (e) {
    renderError("Init Failed: " + e.message);
}
