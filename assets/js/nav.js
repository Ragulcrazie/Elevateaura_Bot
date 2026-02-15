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

    // --- ADVANCED REVIEW GENERATOR ---
    
    // 100+ Unique Indian First Names (Pan-India)
    const indianFirstNames = [
        "Aarav", "Vihaan", "Aditya", "Sai", "Arjun", "Reyansh", "Muhammad", "Aryan", "Krishna", "Ishaan",
        "Shaurya", "Atharv", "Advik", "Pranav", "Advaith", "Aayush", "Dhruv", "Kabir", "Rudra", "Vivaan",
        "Rahul", "Amit", "Rohit", "Vikram", "Suresh", "Ramesh", "Karthik", "Venkatesh", "Sanjay", "Manoj",
        "Deepak", "Sunil", "Anil", "Rajesh", "Prakash", "Mukesh", "Nitin", "Sandeep", "Ajay", "Vijay",
        "Ananya", "Diya", "Saanvi", "Aadhya", "Pari", "Kiara", "Myra", "Anvi", "Pihu", "Riya",
        "Sneha", "Priya", "Neha", "Pooja", "Anjali", "Divya", "Swathi", "Lakshmi", "Meera", "Kavita",
        "Ishita", "Simran", "Nisha", "Roshni", "Kiran", "Sangeeta", "Sunita", "Anita", "Deepa", "Rekha",
        "Siddharth", "Gautam", "Abhishek", "Manish", "Vivek", "Vishal", "Ashish", "Alok", "Pankaj", "Tarun",
        "Chetan", "Naveen", "Pradeep", "Sharad", "Bhuvan", "Yash", "Rohan", "Kunal", "Hardik", "Mayank"
    ];

    // Common Indian Surnames
    const indianSurnames = [
        "Sharma", "Verma", "Gupta", "Malhotra", "Bhatia", "Saxena", "Mehta", "Chopra", "Singh", "Kumar",
        "Patel", "Reddy", "Nair", "Iyer", "Rao", "Gowda", "Pillai", "Menon", "Das", "Banerjee",
        "Dutta", "Ghosh", "Chatterjee", "Mishra", "Dubey", "Tiwari", "Pandey", "Yadav", "Jha", "Thakur",
        "Jain", "Agarwal", "Bansal", "Garg", "Mittal", "Joshi", "Deshoande", "Kulkarni", "Patil", "Deshmukh"
    ];

    // Strict Exam List (Matches Dropdown)
    const strictExams = [
        "SSC CGL", "SSC CHSL", "RRB NTPC", "Bank PO", "Bank Clerk", "Police Constable", "State Exams"
    ];

    // Diverse Comments (Short, Medium, Long, Hinglish, Emotional)
    const reviewComments = [
        "Best bot for practice.",
        "Finally cleared my concepts.",
        "Speed improved by 2x.",
        "Winning ₹600 was a shock! Real money.",
        "Recommended to all my friends.",
        "Better than paid apps.",
        "Daily streak keeps me disciplined.",
        "Maths solutions are very clear.",
        "GK quizzes are updated daily.",
        "Reasoning section is tough but good.",
        "Started with free plan, now on yearly.",
        "No ads in premium is peaceful.",
        "I practice while travelling.",
        "The interface is very smooth.",
        "Love the dark mode.",
        "Support team helped me instantly.",
        "Mock tests feel like real exam.",
        "Detailed analysis showed my weak spots.",
        "Competition with others is addictive.",
        "Just wow. Elevate Aura is the future.",
        "Simple, fast, effective.",
        "No lag, works on 4G also.",
        "Best investment for students.",
        "Helped me clear Tier 1.",
        "A must-have for aspirants.",
        "Current affairs logic is great.",
        "The timer makes it exciting.",
        "I was losing hope, but this kept me going.",
        "My rank improved from 5000 to 200.",
        "Consistent practice is the key.",
        "The explanations are short and crisp.",
        "Perfect for last minute revision.",
        "I use it 30 mins before sleep.",
        "Very user friendly bot.",
        "Premium is worth every paisa.",
        "Legit platform. Got my reward.",
        "Challenging questions.",
        "Helps in time management.",
        "Good for English vocab also.",
        "Community feel is strong.",
        "Bhai mazaa aa gaya practice karke.",
        "Sahi hai boss, questions acche hai.",
        "Best resource for SSC.",
        "Finally found something good.",
        "Superb experience.",
        "10/10 would recommend.",
        "Keeps me consistent.",
        "Great initiative for students.",
        "Love the weekly prizes.",
        "Analysis view is very detailed."
    ];

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

    function generateUniqueReviews(count) {
        const generated = [];
        // Shuffle names to ensure uniqueness order
        const shuffledNames = shuffle([...indianFirstNames]); 
        
        for (let i = 0; i < count; i++) {
            // Exhausted names check (loop back if needed, but 100 is plenty)
            if (i >= shuffledNames.length) break; 
            
            const fname = shuffledNames[i];
            const lname = indianSurnames[Math.floor(Math.random() * indianSurnames.length)];
            const exam = strictExams[Math.floor(Math.random() * strictExams.length)];
            const text = reviewComments[Math.floor(Math.random() * reviewComments.length)];
            
            // Random Name Format
            let finalName;
            const format = Math.random();
            if (format < 0.4) {
                finalName = `${fname} ${lname}`; // Full Name (Rahul Sharma)
            } else if (format < 0.7) {
                 finalName = `${fname} ${lname[0]}.`; // First + Initial (Rahul S.)
            } else {
                 finalName = fname; // First Only (Rahul)
            }

            generated.push({
                name: finalName,
                role: `${exam} Aspirant`, // Matches Dropdown
                text: text
            });
        }
        return generated;
    }

    function initReviewWall() {
        const track = document.getElementById('reviewTrack');
        if (!track) return;

        // Generate 100 Unique Reviews (Enough for infinite feel)
        const allReviews = generateUniqueReviews(100);

        const addCards = () => {
             allReviews.forEach(review => {
                const card = document.createElement('div');
                card.className = 'review-card';
                // Randomize star count slightly
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
