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

console.log("ELEVATE AURA BOT: Script v42 Loaded");

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
        id: user.id, // Needed for payment
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
    
    renderAnalytics(userEntry, total, percentile, userStats);
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
    const unlockBtn = document.getElementById('unlockPotentialBtn');
    
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
    // Button Action
    if (unlockBtn) {
        if (subStatus === 'premium') {
             // PREMIUM VIEW
             unlockBtn.innerHTML = `<span class="mr-2 text-lg">💬</span> Talk to AI Mentor (Premium)`;
             // Change Gradient to Green/Teal
             unlockBtn.className = "w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-bold py-3 rounded-lg flex items-center justify-center transition-all shadow-lg active:scale-95 group-hover:shadow-[0_0_20px_rgba(16,185,129,0.3)]";
             
             unlockBtn.onclick = () => {
                 openMentorChat(userEntry.full_name || "Aspirant", weakSpots, pointsLost, userStats.language);
                 if(tg.HapticFeedback) tg.HapticFeedback.impactOccurred('medium');
             };
             
             // --- CHAT LOGIC ---
             function openMentorChat(name, weakSpots, pointsLost, lang) {
                 const modal = document.getElementById('chatModal');
                 const container = document.getElementById('chatContainer');
                 const status = document.getElementById('chatStatus');
                 
                 container.innerHTML = ""; // Clear old chat
                 modal.classList.remove('hidden');
                 
                 const topic = weakSpots.length > 0 ? weakSpots[0].topic : 'Focus';
                 const isHindi = lang === 'hindi';
                 
                 // --- SCRIPT ENGINE ---
                 // A diverse set of scripts to feel "Infinite"
                 const scripts = [
                     {
                         type: "strategy",
                         condition: (p) => p > 50,
                         msgs: [
                             `Hey ${name}, I've been engaged in analyzing your score patterns. 🧐`,
                             `You lost <b class="text-red-400">${pointsLost} points</b> today. That's not just a number; that's the difference between "Selected" and "Waitlisted".`,
                             `Your main enemy right now is <b>${topic}</b>. You are spending too much time thinking instead of reacting.`,
                             `💡 <b>Quick Fix:</b> For the next 24 hours, do not solve full problems. Just look at 50 questions of ${topic} and primarily identify the <i>First Step</i>. Speed comes from recognition, not calculation.`
                         ]
                     },
                     {
                         type: "tough_love",
                         condition: (p) => true,
                         msgs: [
                             `Listen to me, ${name}.`,
                             `I see you are consistently struggling with <b>${topic}</b>. Is it a lack of concept or lack of practice?`,
                             `The Top 500 players solve ${topic} questions in under 45 seconds. You are averaging higher.`,
                             `🔥 <b>My Challenge:</b> Solve 20 questions of ${topic} today anytime you get 5 minutes free. No excuses.`
                         ]
                     },
                     {
                         type: "technical_seating",
                         condition: (p) => topic.includes('Seating'),
                         msgs: [
                             `I noticed you specifically froze on <b>Seating Arrangement</b>.`,
                             `Most students rush to draw the circle. That's a rookie mistake.`,
                             `🧠 <b>AI Tip:</b> Spend the first 15 seconds ONLY reading the 'Definite Information' (like "A is right of B"). Ignore "Possible" information until the end.`,
                             `Try this technique in tomorrow's test. I'm tracking your improvement.`
                         ]
                     },
                     {
                         type: "technical_syllogism",
                         condition: (p) => topic.includes('Syllogism'),
                         msgs: [
                             `Syllogisms are leaking your marks, ${name}.`,
                             `Are you still confused by "Only a few"?`,
                             `Remember: "Only a few A are B" = "Some A are B" + "Some A are NOT B".`,
                             `Draw two separate lines in your Venn diagram for this. It stops 90% of negative marking.`
                         ]
                     },
                     {
                         type: "motivation_high",
                         condition: (p) => pointsLost < 30, // Good score
                         msgs: [
                             `Impressive work today, ${name}! 🚀`,
                             `You are very close to your Max Potential. Only <b class="text-yellow-400">${pointsLost} points</b> left on the table.`,
                             `Don't get complacent. The ghosts in the top 10 are relentless.`,
                             `Polish your <b>${topic}</b> just a little more, and you will be untouchable.`
                         ]
                     }
                 ];
                 
                 // Fallback script
                 const fallback = [
                      `Hello ${name}. 👋`,
                      `I analyzed your performance. You have high potential, but <b>${topic}</b> is dragging your rank down.`,
                      `Make ${topic} your obsession for the next hour. Read the Concept Notes I unlocked for you.`,
                      `See you on the leaderboard tomorrow.`
                 ];
                 
                 // Select Script
                 let selectedScript = scripts.find(s => s.condition(pointsLost))?.msgs || fallback;
                 
                 // If Hindi
                 if (isHindi) {
                     // Simple mock translation for demo (In real app, we'd have Hindi versions in array)
                     selectedScript = [
                         `नमस्ते ${name}। मैंने आपके स्कोर का विश्लेषण किया है।`,
                         `आज आपने <b>${topic}</b> में अंक गंवाए।`,
                         `💡 <b>सुझाव:</b> अगले एक घंटे तक केवल ${topic} के आसान सवालों का अभ्यास करें।`,
                         `कल बेहतर प्रदर्शन करें!`
                     ];
                 }

                 // Executor
                 let delay = 500;
                 
                 // Initial Conversation Loop
                 function playSequence(msgs) {
                     let localDelay = 500;
                     msgs.forEach((msg, i) => {
                         setTimeout(() => {
                             status.innerText = "typing...";
                             const isLast = i === msgs.length - 1;
                             
                             setTimeout(() => {
                                 appendMsg(msg, 'ai');
                                 status.innerText = "Online";
                                 tg.HapticFeedback.impactOccurred('light');
                                 
                                 // If it's the last message, show relevant chips
                                 if (isLast) {
                                     showChipsForTopic(topic);
                                 }
                             }, 1000 + (msg.length * 10)); 
                             
                         }, localDelay);
                         localDelay += 2000 + (msg.length * 20);
                     });
                 }
                 
                 playSequence(selectedScript);
                 
                 // --- CHIP LOGIC ---
                 function showChipsForTopic(t) {
                     const chipsContainer = document.createElement('div');
                     chipsContainer.className = "p-4 border-t border-gray-800 bg-gray-900 grid grid-cols-2 gap-2 animate-fade-in-up";
                     chipsContainer.id = "activeChips";
                     
                     // Define potential doubts based on topic
                     let chips = [
                         { text: "💡 Give me a Shortcut", action: "shortcut" },
                         { text: "📉 Common Mistakes?", action: "mistakes" },
                         { text: "🧠 Psychology Hack", action: "psych" },
                         { text: "👋 End Session", action: "end" }
                     ];
                     
                     // Custom overrides
                     if (t.toLowerCase().includes("seating")) {
                         chips = [
                             { text: "⚡ Speed Trick", action: "shortcut_seating" },
                             { text: "❌ What to skip?", action: "skip_strategy" },
                             { text: "🔍 Visual Probe", action: "visual_probe" }
                         ];
                     }
                     
                     chips.forEach(chip => {
                         const btn = document.createElement('button');
                         btn.className = "bg-gray-800 hover:bg-gray-700 text-green-400 text-xs font-bold py-3 px-2 rounded-lg border border-gray-700 transition-all active:scale-95";
                         btn.innerText = chip.text;
                         btn.onclick = () => handleUserResponse(chip.text, chip.action, t);
                         chipsContainer.appendChild(btn);
                     });
                     
                     // Replace the Input Area
                     const modal = document.getElementById('chatModal');
                     const existingFooter = modal.querySelector('.border-t');
                     if(existingFooter) existingFooter.remove();
                     modal.appendChild(chipsContainer);
                 }
                 
                 function handleUserResponse(text, action, t) {
                     // 1. Remove chips
                     const chips = document.getElementById('activeChips');
                     if(chips) chips.remove();
                     
                     // 2. Show User Message
                     appendMsg(text, 'user');
                     
                     // 3. AI Reply after delay
                     setTimeout(() => {
                         status.innerText = "typing...";
                         setTimeout(() => {
                             const response = getAIResponse(action, t);
                             appendMsg(response, 'ai');
                             status.innerText = "Online";
                             tg.HapticFeedback.notificationOccurred('success');
                             
                             // 4. Show "Close" or "More" options? 
                             // For one-time build, let's just end or show a "Back to Quiz" button
                             if (action !== 'end') {
                                 setTimeout(() => showFinalOptions(), 1000);
                             }
                         }, 1500);
                     }, 500);
                 }
                 
                 function getAIResponse(action, t) {
                     // 1. Resolve Topic Key
                     const key = Object.keys(TopicKnowledgeBase).find(k => t.toLowerCase().includes(k)) || 'default';
                     // 2. Resolve Language (default to English if undefined)
                     const safeLang = (lang === 'hindi') ? 'hindi' : 'english';
                     const data = TopicKnowledgeBase[key][safeLang];

                     switch(action) {
                         case "shortcut":
                         case "shortcut_seating":
                             return data.shortcut; // Returns the HTML string from KB
                         case "mistakes":
                         case "skip_strategy":
                             return data.mistake;
                         case "psych":
                         case "visual_probe":
                             return safeLang === 'hindi' ? 
                                 "🧠 <b>मनोवैज्ञानिक हैक:</b> टाइमर को मत देखो। जब आप टाइमर देखते हैं, तो आपका दिमाग 20% धीमा हो जाता है। बस प्रश्न पर ध्यान दें।" : 
                                 "🧠 <b>Psych Hack:</b> Do not look at the timer. When you check the time, your IQ drops by 20% due to cortisol. Flow state requires ignorance of time.";
                         case "end":
                             return safeLang === 'hindi' ? "जाओ और फोड़ दो! मैं देख रहा हूँ। 😉" : "Go crush it. I'm watching. 😉";
                         default:
                             return "Focus on accuracy first. Speed follows.";
                     }
                 }
                 
                 function showFinalOptions() {
                     const chipsContainer = document.createElement('div');
                     chipsContainer.className = "p-4 border-t border-gray-800 bg-gray-900 flex justify-center animate-fade-in";
                     
                     const btn = document.createElement('button');
                     btn.className = "w-full bg-gradient-to-r from-green-600 to-emerald-600 text-white font-bold py-3 rounded-lg shadow-lg";
                     btn.innerText = "😤 I'm Ready to Train";
                     btn.onclick = () => {
                         document.getElementById('chatModal').classList.add('hidden');
                         // Trigger quiz start or close
                     };
                     chipsContainer.appendChild(btn);
                     document.getElementById('chatModal').appendChild(chipsContainer);
                 }

                 function appendMsg(html, sender) {
                     const div = document.createElement('div');
                     if (sender === 'ai') {
                        div.className = "bg-gray-800 p-3 rounded-xl rounded-tl-none border border-gray-700 text-sm max-w-[85%] self-start animate-fade-in text-gray-200";
                     } else {
                        div.className = "bg-green-600/20 p-3 rounded-xl rounded-tr-none border border-green-500/30 text-sm max-w-[85%] self-end text-right text-green-200 animate-fade-in";
                     }
                     div.innerHTML = html;
                     container.appendChild(div);
                     container.scrollTop = container.scrollHeight;
                 }
             }
             
             // --- CENTRAL KNOWLEDGE BASE (Single Source of Truth) ---
             const TopicKnowledgeBase = {
                 'seating': {
                     hindi: {
                         concept: "<b>बैठकी व्यवस्था (Seating Arrangement):</b> हमेशा Fixed Position वाले वाक्यों से शुरुआत करें।",
                         shortcut: "⚡ <b>शॉर्टकट:</b> 'A, B और C के बीच में है' (Possible) जैसे वाक्यों को छोड़ दें। केवल 'A, B के दायें दूसरा है' (Definite) को पहले प्लॉट करें।",
                         mistake: "📉 <b>गलती:</b> लोग Left/Right में भ्रमित हो जाते हैं। खुद को उस जगह पर बैठा हुआ मानकर अपना हाथ देखें।",
                         full_note: `<h4>🌀 बैठकी व्यवस्था (Seating Arrangement)</h4><br>
                                    <p><b>मुख्य नियम:</b></p>
                                    <ul>
                                      <li>हमेशा <b>Circles</b> के लिए केंद्र की ओर (Facing Center) और बाहर की ओर (Facing Outside) का ध्यान रखें।</li>
                                      <li><b>Linear</b> में Left/Right का निर्धारण अपने हाथ के अनुसार करें।</li>
                                    </ul>`
                     },
                     english: {
                         concept: "<b>Seating Arrangement:</b> Always start with Definite Statements.",
                         shortcut: "⚡ <b>Shortcut:</b> Ignore 'Possibility cases' (e.g. A is between B and C) at the start. Only plot 'Definite Information' (e.g. A is 2nd to right of B).",
                         mistake: "📉 <b>Common Mistake:</b> Confusing Left/Right when facing South or Outside. Use your own hand as a reference physically.",
                         full_note: `<h4>🌀 Seating Arrangement Mastery</h4><br>
                                    <p><b>Core Rules:</b></p>
                                    <ul>
                                      <li>For <b>Circular</b>: Always note if facing Center (Left=Clockwise) or Outside (Left=Anti-Clockwise).</li>
                                      <li>For <b>Linear</b>: Your Left/Right is the person’s Left/Right if facing North.</li>
                                    </ul>`
                     }
                 },
                 'syllogism': {
                     hindi: {
                         concept: "<b>न्याय निगमन (Syllogism):</b> वेन डायग्राम (Venn Diagram) विधि सबसे सटीक है।",
                         shortcut: "⚡ <b>शॉर्टकट:</b> 'Only a few A are B' का मतलब है -> Some A are B (✅) AND Some A are NOT B (❌)। दो लाइनें खींचें।",
                         mistake: "📉 <b>गलती:</b> संभावना (Possibility) पूछे जाने पर Definite जवाब देना। अगर डायग्राम में लिंक नहीं है, तो 'No' न कहें, 'Cant Say' कहें।",
                         full_note: `<h4>🟢 न्याय निगमन (Syllogism) - Venn Diagram Method</h4><br>
                                    <p><b>Golden Rule:</b> "Only a few A are B" का मतलब है: Some A are B <b>AND</b> Some A are NOT B.</p>`
                     },
                     english: {
                         concept: "<b>Syllogism:</b> The Venn Diagram method is the gold standard.",
                         shortcut: "⚡ <b>Shortcut:</b> 'Only a few A are B' means -> Some A are B (✅) AND Some A are NOT B (❌). Draw a slash on the line.",
                         mistake: "📉 <b>Common Mistake:</b> Assuming 'Some A is not B' just because circles don't touch. If they don't touch, the relation is 'Unknown', not 'No'.",
                         full_note: `<h4>🟢 Syllogism - Venn Diagram Method</h4><br>
                                    <p><b>Golden Rule:</b> "Only a few A are B" means: Some A are B <b>AND</b> Some A are NOT B.</p>`
                     }
                 },
                 'default': {
                     hindi: {
                         concept: "इस विषय के लिए अवधारणात्मक स्पष्टता (Conceptual Clarity) की आवश्यकता है।",
                         shortcut: "⚡ <b>शॉर्टकट:</b> विकल्पों को एलिमिनेट (Option Elimination) करना सीखें। सीधा उत्तर ढूंढने के बजाय गलत उत्तर हटाएं।",
                         mistake: "📉 <b>गलती:</b> प्रश्न को पूरा न पढ़ना और जल्दबाजी में 'NOT following' को 'Following' समझ लेना।",
                         full_note: `<h4>🚀 Quick Review</h4><p>Detailed notes are being prepared.</p>`
                     },
                     english: {
                         concept: "This topic requires Conceptual Clarity and speed.",
                         shortcut: "⚡ <b>Shortcut:</b> Use <b>Option Elimination</b>. Instead of solving fully, remove the options that are obviously wrong (e.g. wrong units or digits).",
                         mistake: "📉 <b>Common Mistake:</b> Misreading the question. E.g., Solving for 'False' when the question asked for 'True'. Slow down the reading.",
                         full_note: `<h4>🚀 Quick Review</h4><p>Detailed notes are being prepared.</p>`
                     }
                 }
             };

             const notesBtn = document.createElement('button');
             notesBtn.className = "mt-3 w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs font-bold py-3 rounded-lg flex items-center justify-center transition-all shadow-lg active:scale-95 border border-indigo-400/30";
             notesBtn.innerHTML = `<span class="mr-2">👑</span> Revise Concepts`;
             
             notesBtn.onclick = () => {
                 const lang = userStats.language === 'hindi' ? 'hindi' : 'english';
                 
                 let finalContent = "";
                 
                 if (weakSpots.length > 0) {
                     weakSpots.forEach((ws, index) => {
                         if (index > 0) finalContent += "<div class='my-6 h-px bg-gray-700 w-full'></div>";
                         
                         // Fetch from KB
                         const key = Object.keys(TopicKnowledgeBase).find(k => ws.topic.toLowerCase().includes(k)) || 'default';
                         const data = TopicKnowledgeBase[key][lang];
                         
                         // Combine Full Note
                         finalContent += data.full_note;
                         finalContent += `<div class="mt-4 bg-gray-800 p-3 rounded-lg">${data.shortcut}</div>`;
                         finalContent += `<div class="mt-2 bg-red-900/20 border border-red-500/20 p-3 rounded-lg text-gray-400 text-xs">${data.mistake}</div>`;
                     });
                 } else {
                     const data = TopicKnowledgeBase['default'][lang];
                     finalContent = data.full_note + `<br>${data.shortcut}`;
                 }

                 const modal = document.getElementById('notesModal');
                 const titleEl = document.getElementById('noteTitle');
                 const bodyEl = document.getElementById('noteContent');
                 
                 if (modal && bodyEl) {
                     titleEl.innerText = `Revising ${weakSpots.length} Topics`;
                     bodyEl.innerHTML = finalContent;
                     modal.classList.remove('hidden');
                     
                     // Add User Watermark
                     const wm = document.createElement('div');
                     wm.innerText = `ID: ${userEntry.id}`;
                     wm.className = "absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-gray-700/20 text-4xl font-black rotate-45 pointer-events-none select-none z-0";
                     if(!bodyEl.querySelector('.watermark')) {
                         wm.classList.add('watermark');
                         bodyEl.appendChild(wm);
                     }
                 }
                 if(tg.HapticFeedback) tg.HapticFeedback.impactOccurred('light');
             };
             
             unlockBtn.parentNode.appendChild(notesBtn);
             
             // ... [Rest of code] ...

             // INSIDE openMentorChat -> getAIResponse
             // We need to move getAIResponse to use TopicKnowledgeBase
             
             // [NOTE: Since getAIResponse is inside the function scope below, we will modify it there. 
             //  But wait, openMentorChat function definition was BEFORE this replace block in previous edits?
             //  No, openMentorChat was defined inside the click handler scope in previous edits or global?
             //  Let's look at file... It's defined on line 417.
             //  I need to make sure TopicKnowledgeBase is accessible to openMentorChat.]
             

             
             // Hide Insight Warning Color if desired, or keep it as diagnosis
        } else {
            // FREE VIEW (Paywall)
            unlockBtn.onclick = () => {
                // Trigger Telegram Payment or Info Modal
                try {
                    tg.MainButton.setText("PAY 500 STARS ⭐ (TEST MODE)");
                    tg.MainButton.show();
                    // FIX: Use proper haptic method
                    if(tg.HapticFeedback) tg.HapticFeedback.impactOccurred('light');
                    
                    // --- DUMMY PAYMENT HANDLER ---
                    const handlePayment = () => {
                        const originalText = "PAY 500 STARS ⭐ (TEST MODE)";
                        tg.MainButton.showProgress(true); // Spinner
                        
                        // Call Simulate API
                        return fetch(`${API_BASE_URL}/api/simulate_payment`, {
                            method: 'POST',
                            body: JSON.stringify({ user_id: userEntry.id }),
                            headers: { 'Content-Type': 'application/json' }
                        })
                        .then(res => res.json())
                        .then(data => {
                             tg.MainButton.hideProgress();
                             if(data.status === 'success') {
                                 tg.MainButton.setText("SUCCESS! 🎉");
                                 tg.HapticFeedback.notificationOccurred('success');
                                 setTimeout(() => {
                                     tg.MainButton.hide();
                                     window.location.reload(); // Reload to see Premium View
                                 }, 1500);
                             } else {
                                 tg.MainButton.setText("ERROR ❌"); // Short error
                                 alert("Error: " + data.error);
                                 setTimeout(() => tg.MainButton.setText(originalText), 2000);
                             }
                             // Cleanup
                             tg.MainButton.offClick(handlePayment);
                        })
                        .catch(e => {
                            tg.MainButton.hideProgress();
                            tg.MainButton.setText("NET ERROR ❌");
                            alert("Network Error: " + e.message);
                            setTimeout(() => tg.MainButton.setText(originalText), 2000);
                        });
                    };
                    
                    // Cleanup old listeners just in case
                    tg.MainButton.offClick(handlePayment); 
                    tg.MainButton.onClick(handlePayment);
                } catch(e) {
                    console.error("TG Button Error", e);
                    alert("Payment Error: " + e.message + ". Try reloading.");
                }
            }
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
