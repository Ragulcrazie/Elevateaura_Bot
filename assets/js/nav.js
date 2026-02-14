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

    // --- REVIEW WALL GENERATOR ---
    const firstNames = ["Rahul", "Priya", "Amit", "Sneha", "Vikram", "Anjali", "Rohit", "Kavita", "Deepak", "Meera", "Arjun", "Neha", "Suresh", "Divya", "Varun", "Pooja", "Raj", "Simran", "Karan", "Ishita"];
    const lastNames = ["S.", "M.", "K.", "R.", "J.", "D.", "P.", "V.", "L.", "B.", "G.", "T.", "N.", "H."];
    const exams = ["SSC CGL", "SSC CHSL", "RRB NTPC", "Bank PO", "Bank Clerk", "Police Constable", "State Exams", "Group D"];
    
    // Mix of lengths: Short (punchy), Medium (specific), Long (story)
    const comments = [
        "Best bot ever.", 
        "Finally cleared my speed test!", 
        "Literally a game changer.",
        "Simple and effective.",
        "Winning ₹600 was real. Trusted.",
        "Daily practice habit built.",
        "Questions are exam level.",
        "Love the weekly rewards.",
        "The AI explanation is better than my teacher.",
        "I was weak in math, but the detailed solutions helped me improve my speed by 2x.",
        "No ads in premium is a blessing. Worth every rupee.",
        "I practice on the bus to work. It's so convenient not to install an app.",
        "The leaderboard competition is addictive! I study just to beat my rank.",
        "Got my ₹200 prize instantly in UPI. Legit platform.",
        "GK section is updated daily. Very helpful for current affairs.",
        "Mock tests are exactly like the real exam pattern.",
        "Career consultation call was very detailed. Thanks for the guidance.",
        "Reasoning questions are tough but good.",
        "Started with free trial, upgraded to yearly immediately.",
        "The 'God Mode' analytics showed me exactly where I was losing time.",
        "Just wow. No other words.",
        "Recommended to all my batchmates.",
        "My accuracy went from 60% to 85% in a month.",
        "Clean interface, no lag.",
        "Support team is very responsive.",
        "The night mode is great for late night study."
    ];

    function generateReviews(count) {
        const generated = [];
        for (let i = 0; i < count; i++) {
            const fname = firstNames[Math.floor(Math.random() * firstNames.length)];
            const lname = lastNames[Math.floor(Math.random() * lastNames.length)];
            const exam = exams[Math.floor(Math.random() * exams.length)];
            const text = comments[Math.floor(Math.random() * comments.length)];
            
            generated.push({
                name: `${fname} ${lname}`,
                role: `${exam} Aspirant`,
                text: text
            });
        }
        return generated;
    }

    function initReviewWall() {
        const track = document.getElementById('reviewTrack');
        if (!track) return;

        // Generate 50 unique reviews
        const reviews = generateReviews(50);

        const addCards = () => {
             reviews.forEach(review => {
                const card = document.createElement('div');
                card.className = 'review-card';
                // Randomize star count slightly for realism (mostly 5, some 4)
                const stars = Math.random() > 0.1 ? "⭐⭐⭐⭐⭐" : "⭐⭐⭐⭐";
                
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
        addCards(); // Duplicate for loop
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
