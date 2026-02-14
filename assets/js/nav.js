document.addEventListener("DOMContentLoaded", function() {
    // 1. Inject Navigation
    const navHTML = `
    <!-- Top Bar -->
    <div class="top-bar">
        <div class="container" style="max-width: 1200px; margin: 0 auto; padding: 0 20px;">
            <a href="mailto:elevateauraofficial@gmail.com" style="text-decoration: none;">📧 elevateauraofficial@gmail.com</a>
            <a href="https://t.me/ElevateAura_Bot" style="text-decoration: none;">✈️ @ElevateAura_Bot</a>
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
});
