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

    // --- REVIEW WALL LOGIC ---
    const reviews = [
        { name: "Rahul S.", role: "SSC CGL Aspirant", text: "The AI explanations are a game changer. Cleared Tier 1 thanks to this!" },
        { name: "Priya M.", role: "Bank PO", text: "Winning ₹600 was the best motivation. It's real and it works." },
        { name: "Amit K.", role: "RRB NTPC", text: "No app install needed. I practice on the bus every day." },
        { name: "Sneha R.", role: "Police Constable", text: "Simple, fast, and effective. The leaderboards are addictive!" },
        { name: "Vikram J.", role: "UPSC Prelims", text: "Good for CSAT practice. The questions are high quality." },
        { name: "Anjali D.", role: "SSC CHSL", text: "Finally a platform that rewards hard work. Love the daily streaks." },
        { name: "Rohit P.", role: "Bank Clerk", text: "My speed improved by 40% in just 2 weeks. Analysis is detailed." },
        { name: "Kavita S.", role: "General Awareness", text: "Current affairs quizzes are top notch. Must try." }
    ];

    function initReviewWall() {
        const track = document.getElementById('reviewTrack');
        if (!track) return;

        // Function to add cards
        const addCards = () => {
             reviews.forEach(review => {
                const card = document.createElement('div');
                card.className = 'review-card';
                card.innerHTML = `
                    <div class="user-info">
                        <div class="avatar">${review.name[0]}</div>
                        <div>
                            <h4 style="margin:0; font-size:1rem; color:white;">${review.name}</h4>
                            <div style="font-size:0.8rem; color:var(--text-muted);">${review.role}</div>
                        </div>
                    </div>
                    <div class="stars">⭐⭐⭐⭐⭐</div>
                    <p style="font-size:0.9rem; color:#e2e8f0; line-height:1.5;">"${review.text}"</p>
                `;
                track.appendChild(card);
            });
        };

        // Initial Load
        addCards();
        // Duplicate for seamless loop
        addCards();
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
        const text = document.getElementById('reviewText').value;

        if (!name || !text) {
            alert("Please fill in all fields!");
            return;
        }

        // Fake Success UI
        const btn = document.querySelector('#reviewModal .btn-primary');
        if(btn) {
            const originalText = btn.innerText;
            btn.innerText = "Submitted! (Pending Moderation)";
            btn.style.background = "#10b981";
            
            setTimeout(() => {
                window.closeReviewModal();
                btn.innerText = originalText;
                btn.style.background = "";
                document.getElementById('reviewName').value = "";
                document.getElementById('reviewText').value = "";
                alert("Thanks! Your review has been submitted for moderation.");
            }, 1500);
        }
    }

});
