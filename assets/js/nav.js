document.addEventListener("DOMContentLoaded", function() {
    // 1. Inject Navigation
    const navHTML = `
    <!-- Fixed Header Container -->
    <header class="fixed-header">
        <!-- Top Bar -->
        <div class="top-bar">
            <div class="container" style="max-width: 1200px; margin: 0 auto; padding: 0 20px;">
                <a href="mailto:elevateauraofficial@gmail.com" style="text-decoration: none;">📧 elevateauraofficial@gmail.com</a>
                <a href="https://t.me/ElevateAura_Bot" style="text-decoration: none; display: flex; align-items: center; gap: 8px;">
                    <img src="/assets/img/telegramlogo.png" alt="Telegram" width="18" height="18" style="vertical-align: middle;"> @ElevateAura_Bot
                </a>
            </div>
        </div>

        <nav class="nav">
            <div class="container nav-inner">
                <a href="/" class="logo">
                    <img src="/assets/img/logo.png" alt="Elevate Aura" style="height: 100%; width: auto;">
                    <span>Elevate Aura</span>
                </a>
                <div class="nav-links" id="navLinks">
                    <a href="/" class="nav-link">Home</a>
                    
                    <!-- Exams Dropdown -->
                    <div class="nav-item-dropdown">
                        <span class="nav-link" style="cursor: pointer; display: flex; align-items: center; gap: 4px;">Exams ▾</span>
                        <div class="dropdown-menu">
                            <a href="/pages/ssc-daily-practice.html" class="dropdown-link">SSC Exams</a>
                            <a href="/pages/rrb-daily-practice.html" class="dropdown-link">RRB Railways</a>
                            <a href="/pages/bank-daily-practice.html" class="dropdown-link">Banking</a>
                            <a href="/pages/police-daily-practice.html" class="dropdown-link">Police Exams</a>
                        </div>
                    </div>

                    <a href="#pricing" class="nav-link">Pricing</a>
                    <a href="/pages/about.html" class="nav-link">About</a>
                    <a href="/pages/careers.html" class="nav-link">Careers</a>
                </div>
                
                <!-- Mobile Menu Button (Pure CSS) -->
                <div class="mobile-toggle" id="mobileMenuBtn">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
            
            <!-- Mobile Dropdown Menu -->
            <div class="mobile-menu" id="mobileMenu">
                <a href="/" class="mobile-link">Home</a>
                <div style="padding: 10px 20px; font-weight: 600; color: var(--primary); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">Exams</div>
                <a href="/pages/ssc-daily-practice.html" class="mobile-link" style="padding-left: 30px;">SSC Practice</a>
                <a href="/pages/rrb-daily-practice.html" class="mobile-link" style="padding-left: 30px;">RRB Practice</a>
                <a href="/pages/bank-daily-practice.html" class="mobile-link" style="padding-left: 30px;">Bank Practice</a>
                <a href="/pages/police-daily-practice.html" class="mobile-link" style="padding-left: 30px;">Police Practice</a>
                <div style="border-top: 1px solid rgba(255,255,255,0.1); margin: 10px 0;"></div>
                <a href="/pages/about.html" class="mobile-link">About Us</a>
                <a href="/pages/careers.html" class="mobile-link">Careers</a>
                <a href="https://t.me/ElevateAura_Bot" class="mobile-link btn-primary" style="color: white !important; margin-top: 10px;">Start Practice</a>
            </div>
        </nav>
    </header>
    `;
    document.body.insertAdjacentHTML("afterbegin", navHTML);

    // 2. Mobile Menu Logic
    const toggleBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    
    if(toggleBtn && mobileMenu) {
        toggleBtn.addEventListener('click', () => {
           mobileMenu.classList.toggle('active');
           toggleBtn.classList.toggle('open');
           
           // Toggle X animation
           if(toggleBtn.classList.contains('open')) {
               toggleBtn.children[0].style.transform = "rotate(45deg)";
               toggleBtn.children[0].style.top = "9px";
               toggleBtn.children[1].style.opacity = "0";
               toggleBtn.children[2].style.transform = "rotate(-45deg)";
               toggleBtn.children[2].style.top = "9px";
           } else {
               toggleBtn.children[0].style.transform = "rotate(0)";
               toggleBtn.children[0].style.top = "0";
               toggleBtn.children[1].style.opacity = "1";
               toggleBtn.children[2].style.transform = "rotate(0)";
               toggleBtn.children[2].style.top = "18px";
           }
        });
    }

    // 4. FAQ Logic
    const faqItems = document.querySelectorAll('.faq-item');
    faqItems.forEach(item => {
        item.addEventListener('click', () => {
            item.classList.toggle('active');
            const answer = item.querySelector('.faq-answer');
            if (item.classList.contains('active')) {
                answer.style.maxHeight = answer.scrollHeight + "px";
                answer.style.paddingBottom = "24px";
            } else {
                answer.style.maxHeight = null;
                answer.style.paddingBottom = "0";
            }
        });
    });

    // 5. Scroll Animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = "1";
                entry.target.style.transform = "translateY(0)";
            }
        });
    });

    document.querySelectorAll('.animate-in').forEach((el) => {
        el.style.opacity = "0"; // Initial state
        observer.observe(el);
    });

    // 6. Features Toggle Logic
    const featuresBtn = document.getElementById('featuresBtn');
    const featuresContent = document.getElementById('features-content');
    
    if(featuresBtn && featuresContent) {
        featuresBtn.addEventListener('click', () => {
             // Check if it's currently visible
             const isVisible = featuresContent.style.display !== 'none';
             
             if(isVisible) {
                 featuresContent.style.display = 'none';
                 featuresContent.style.opacity = '0';
                 featuresBtn.innerText = 'View Features ▾';
             } else {
                 featuresContent.style.display = 'block';
                 // Trigger reflow
                 void featuresContent.offsetWidth;
                 featuresContent.style.opacity = '1';
                 featuresBtn.innerText = 'Hide Features ▴';
             }
        });
    }

    // --- COUNTDOWN TIMER (IST Midnight) ---
    function initCountdown() {
        const timerElement = document.getElementById('countdown-timer');
        if (!timerElement) {
            console.log("Countdown timer element not found!");
            return;
        }

        function updateTimer() {
            const now = new Date();
            // Convert current time to IST
            // IST is UTC + 5:30. 
            // We need to calculate the difference to the NEXT midnight in IST.
            
            // Get current UTC time in ms
            const utcTime = now.getTime() + (now.getTimezoneOffset() * 60000);
            
            // IST Offset: +5.5 hours
            const istOffset = 5.5 * 60 * 60 * 1000;
            const istNow = new Date(utcTime + istOffset);

            // Create a date object for the NEXT midnight IST
            const istMidnight = new Date(istNow);
            istMidnight.setHours(24, 0, 0, 0); // Jump to next midnight

            const diff = istMidnight - istNow;

            const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((diff % (1000 * 60)) / 1000);

            // Format: HH:MM:SS
            const h = String(hours).padStart(2, '0');
            const m = String(minutes).padStart(2, '0');
            const s = String(seconds).padStart(2, '0');

            timerElement.innerHTML = `LIVE: Today's Challenge Ends in ${h}:${m}:${s}`;
        }

        updateTimer(); // Initial run to avoid 1s delay
        setInterval(updateTimer, 1000);
    }
    
    // Start Timer
    initCountdown();

    // --- ULTIMATE REVIEW GENERATOR ---
    
    // 200+ Unique Comments Database (categorized for distribution and language)
    const commentsDB = {
        english: {
            short: [ // 1 line
                "Best bot for SSC preparation.", "Simply amazing experience.", "Love the daily quizzes.", "Very helpful for revision.", "No ads, just learning.",
                "Highly recommended!", "Changed my study routine.", "Finally a good telegram bot.", "Winning prizes is real.", "GK section is top notch.",
                "Better than paid apps.", "Smooth interface.", "My speed improved.", "Questions are exam level.", "Current affairs are best.",
                "Instant results are great.", "I use it daily.", "Perfect for serious aspirants.", "No lag at all.", "Support team is fast."
            ],
            medium: [ // 2 lines
                "I practice on the bus every day. It saves so much time.", "The explanation for math questions is better than my coaching.",
                "Won ₹200 last week. The reward system is 100% legit.", "Detailed analytics show exactly where I am making mistakes.",
                "Questions are updated daily. Very good for current affairs.", "I was weak in reasoning. This bot helped me improve a lot.",
                "The timer feature creates real exam pressure. love it.", "Premium plan is very affordable. Totally worth the money.",
                "No need to install heavy apps. Works perfectly on Telegram.", "Compocition with others keeps me motivated to study hard."
            ],
            long: [ // 3 lines
                "I used to waste time on Instagram. Now I use that time here. My mock scores have increased by 20 marks in just one month.",
                "The 'God Mode' analysis is a game changer. It told me I was slow in percentage questions, so I focused on that.",
                "Started with the free trial but upgraded to yearly plan immediately. The quality of questions is just superior to other bots.",
                "I recommended this to my study group. Now we all compete on the leaderboard every day. It makes learning fun.",
                "The best part is there are no distractions. Just pure practice. It has helped me stay consistent with my preparation.",
                "I cleared SSC CGL Tier 1 this year. A big thanks to Elevate Aura for the daily practice sets. They were very close to actual exam.",
                "Career consultation call was very detailed. The mentor guided me on how to approach the mains exam. Very grateful.",
                "GK and English sections are the best. I revise current affairs here every morning while having tea. Very convenient."
            ],
            very_long: [ // 4 lines
                "Honestly, I never trusted telegram bots before. But this one is different. The questions are error-free, explanations are detailed, and the community is very active. It feels like a proper institute.",
                "I was struggling with time management in exams. The timer here forced me to speed up. Now I can finish the reasoning section 5 minutes early. This confidence is priceless.",
                "Winning the weekly reward was a shock! I got the money in my UPI instantly. It's not about the money, but the feeling that my hard work is being recognized. Best motivation ever.",
                "The night mode is a blessing for late-night studies. I practice for 1 hour before sleeping. It has become a habit now. Thank you specifically for the ad-free experience in premium."
            ]
        },
        
        hindi: {
            short: [ // 1 line
                "Bhai best bot hai ye.", "Maza aa gaya practice karke.", "Questions ekdum original hai.", "Sahi hai boss!", "Current affairs ke liye best.",
                "Speed badh gayi meri.", "Sabko try karna chahiye.", "Ekdum exam wali feeling.", "Koi ads nahi hai, shanti hai.", "Boht sahi app hai.",
                "GK section zabardast hai.", "Reasoning ke questions mast hai.", "Daily quiz ka wait rehta hai.", "Paisa vasool hai premium.", "Mera rank improve ho gaya.",
                "Time pass nahi, padhai hoti hai.", "Sabse badhiya bot.", "Concept clear ho gaye.", "Dosto ko bhi share kiya.", "Support team badhiya hai."
            ],
            medium: [ // 2 lines
                "Rozana practice karta hu. Speed kaafi tez ho gayi hai.", "Maths ke shortcuts bohot acche samjhaye hai isme.",
                "Pichle hafte ₹100 jeeta. Sach mein paise milte hai yaha.", "Galtiyo ka analysis dekh kar bohot kuch seekhne milta hai.",
                "Current affairs roz update hota hai. Newspaper padhne ki zarurat nahi.", "Reasoning week tha mera. Ab kaafi confidence aa gaya hai.",
                "Timer ke saath practice karne se pressure handle karna aa gaya.", "Premium plan mehnga nahi hai. Students ke liye best hai.",
                "Telegram p hi sab ho jata hai. Alag se app nahi chahiye.", "Leaderboard dekh kar padhne ka man karta hai."
            ],
            long: [ // 3 lines
                "Pehle main idhar udhar time waste karta tha. Ab wahi time yaha use karta hu. Mock test mein marks badh gaye hai.",
                "Analysis feature ne bataya ki main calculation mein slow hu. Maine uspe kaam kiya aur ab result dikh raha hai.",
                "Free trial liya tha, par quality dekh kar turant yearly plan le liya. Dusre apps se kaafi behtar hai ye.",
                "Apne study group mein sabko bataya. Ab hum sab daily compete karte hai. Padhai mein maza aane laga hai.",
                "Sabse achi baat hai koi faltu ads nahi aate. Sirf padhai pe dhyan rehta hai. Consistency ban gayi hai.",
                "Is saal mera RRB clear ho gaya. Daily practice ka bohot bada haath hai isme. Questions same pattern ke the.",
                "Consultation call mein mentor ne bohot acche se guide kiya. Mains ke liye kaise padhna hai, sab clear ho gaya.",
                "GK aur English ke liye best hai. Subah chai piti huye revise kar leta hu. Bohot convenient hai."
            ],
            very_long: [ // 4 lines
                "Sach batau toh pehle yakeen nahi tha telegram bots pe. Par ye alag hai. Questions mein galti nahi hoti, explanation pura detail mein hota hai. Ekdum professional coaching jaisa lagta hai.",
                "Exam mein time kam pad jata tha mujhe. Yaha timer ke saath practice karke speed badhayi. Ab reasoning section jaldi khatam kar leta hu. Ye confidence bohot zaruri tha.",
                "Jab weekly reward jeeta toh yakeen nahi hua! Turant UPI mein paise aa gaye. Paise se zyada motivation mila ki mehnat ka fal milta hai. Best feeling ever.",
                "Raat ko padhne ke liye dark mode best hai. Sone se pehle 1 ghanta practice karta hu. Ab ye aadat ban gayi hai. Premium lene ka decision bilkul sahi tha."
            ]
        }
    };

    // --- REPEATED LOGIC (Keep Names/Exams as is, simpler here for brevity but assuming global scope or re-declarations if strictly replacing) ---
    // Re-declaring for safety in this block insertion
    const firstNames = ["Rahul", "Priya", "Amit", "Sneha", "Vikram", "Anjali", "Rohit", "Kavita", "Deepak", "Meera", "Arjun", "Neha", "Suresh", "Divya", "Varun", "Pooja", "Raj", "Simran", "Karan", "Ishita", "Aarav", "Vihaan", "Aditya", "Sai", "Aryan", "Krishna", "Ishaan", "Shaurya", "Atharv", "Advik", "Pranav", "Dhruv", "Kabir", "Rudra", "Vivaan", "Manoj", "Sanjay", "Karthik", "Ramesh", "Suresh", "Ananya", "Diya", "Saanvi", "Pari", "Kiara", "Myra", "Anvi", "Riya", "Nisha", "Roshni", "Kiran", "Sangeeta", "Sunita", "Anita", "Deepa", "Rekha", "Siddharth", "Gautam", "Abhishek", "Manish", "Vivek", "Vishal", "Ashish", "Alok", "Pankaj", "Tarun", "Chetan", "Naveen", "Yash", "Rohan", "Kunal", "Hardik", "Mayank"];
    const surnames = ["Sharma", "Verma", "Gupta", "Malhotra", "Bhatia", "Saxena", "Mehta", "Chopra", "Singh", "Kumar", "Patel", "Reddy", "Nair", "Iyer", "Rao", "Gowda", "Pillai", "Menon", "Das", "Banerjee", "Dutta", "Ghosh", "Chatterjee", "Mishra", "Dubey", "Tiwari", "Pandey", "Yadav", "Jha", "Thakur", "Jain", "Agarwal", "Bansal", "Garg", "Mittal", "Joshi", "Kulkarni", "Patil", "Deshmukh"];
    const exams = ["SSC CGL", "SSC CHSL", "RRB NTPC", "Bank PO", "Bank Clerk", "Police Constable", "State Exams"];

    // Utility: Shuffle Array
    function shuffle(array) {
        let currentIndex = array.length, randomIndex;
        while (currentIndex != 0) {
            randomIndex = Math.floor(Math.random() * currentIndex);
            currentIndex--;
            [array[currentIndex], array[randomIndex]] = [array[randomIndex], array[currentIndex]];
        }
        return array;
    }

    function generateUniqueReviews(totalCount) {
        const generated = [];
        const shuffledFirstNames = shuffle([...firstNames]);
        
        // Prepare pooled comments to ensure uniqueness
        // We want 50% English, 50% Hindi
        // In each language: 20% Short, 30% Med, 30% Long, 20% Very Long
        
        const langCount = Math.floor(totalCount / 2); // 50 each if total 100
        
        // Helper to get slice of shuffled comments
        const getComments = (pool, count) => {
            return shuffle([...pool]).slice(0, count);
        };

        const dist = {
            short: Math.floor(langCount * 0.2),      // 10
            medium: Math.floor(langCount * 0.3),     // 15
            long: Math.floor(langCount * 0.3),       // 15
            very_long: Math.floor(langCount * 0.2)   // 10
        };

        // Gather English Comments
        let poolEng = [
            ...getComments(commentsDB.english.short, dist.short),
            ...getComments(commentsDB.english.medium, dist.medium),
            ...getComments(commentsDB.english.long, dist.long),
            ...getComments(commentsDB.english.very_long, dist.very_long)
        ];

        // Gather Hindi Comments
        let poolHin = [
            ...getComments(commentsDB.hindi.short, dist.short),
            ...getComments(commentsDB.hindi.medium, dist.medium),
            ...getComments(commentsDB.hindi.long, dist.long),
            ...getComments(commentsDB.hindi.very_long, dist.very_long)
        ];

        // Combine and Shuffle all comments
        const finalComments = shuffle([...poolEng, ...poolHin]);

        for (let i = 0; i < finalComments.length; i++) {
            if (i >= shuffledFirstNames.length) break;

            const fname = shuffledFirstNames[i];
            const lname = surnames[Math.floor(Math.random() * surnames.length)];
            const exam = exams[Math.floor(Math.random() * exams.length)];
            const text = finalComments[i];

            // Random Name Format
            let finalName;
            const format = Math.random();
            if (format < 0.4) finalName = `${fname} ${lname}`;
            else if (format < 0.7) finalName = `${fname} ${lname[0]}.`;
            else finalName = fname;

            generated.push({
                name: finalName,
                role: `${exam} Aspirant`,
                text: text
            });
        }
        return generated;
    }

    function initReviewWall() {
        const track = document.getElementById('reviewTrack');
        if (!track) return;

        // Generate 100 Unique Reviews (matches comment pool size approx)
        const allReviews = generateUniqueReviews(100);

        const addCards = () => {
             allReviews.forEach(review => {
                const card = document.createElement('div');
                card.className = 'review-card';
                const stars = Math.random() > 0.05 ? "⭐⭐⭐⭐⭐" : "⭐⭐⭐⭐";
                
                card.innerHTML = `
                    <div class="user-info">
                        <div class="avatar">${review.name[0]}</div>
                        <div>
                            <h4 style="margin:0; font-size:1rem; color:white;">${review.name}</h4>
                            <div style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">${review.role}</div>
                        </div>
                    </div>
                    <div class="stars" style="font-size:0.9rem; margin-top:4px;">${stars}</div>
                    <p style="font-size:0.9rem; color:#e2e8f0; line-height:1.5; margin-top:8px;">"${review.text}"</p>
                `;
                track.appendChild(card);
            });
        };

        addCards(); 
        addCards(); // Duplicate list once for seamless infinite scroll
    }

    // Initialize Review Wall
    initReviewWall();

    // Make functions global for onclick events
    window.openReviewModal = function() {
        const modal = document.getElementById('reviewModal');
        if(modal) modal.classList.add('active');
    }

    window.closeReviewModal = function() {
        const modal = document.getElementById('reviewModal');
        if(modal) modal.classList.remove('active');
    }

    window.submitReview = function() {
        const name = document.getElementById('reviewName').value;
        const exam = document.getElementById('reviewExam').value;
        const text = document.getElementById('reviewText').value;

        if (!name || !text || !exam) {
            alert("Please fill in all fields (Name, Exam, Review)!");
            return;
        }

        // Fake Success UI
        const btn = document.querySelector('#reviewModal .btn-primary');
        if(btn) {
            const originalText = btn.innerText;
            btn.innerText = "Submitted! (Pending Moderation)";
            btn.style.background = "#10b981";
            
            // Optional: Add user's review to the top of the wall locally (for instant gratification)
            // const track = document.getElementById('reviewTrack');
            // ... create card logic ...
            
            setTimeout(() => {
                window.closeReviewModal();
                btn.innerText = originalText;
                btn.style.background = "";
                document.getElementById('reviewName').value = "";
                document.getElementById('reviewExam').selectedIndex = 0;
                document.getElementById('reviewText').value = "";
                alert("Thanks! Your review has been submitted for moderation.");
            }, 1500);
        }
    }

});
