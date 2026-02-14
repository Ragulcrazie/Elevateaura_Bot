document.addEventListener("DOMContentLoaded", function() {
    // 1. Inject Navigation
    const navHTML = `
    <nav class="nav">
        <div class="container nav-inner">
            <a href="/" class="logo">Elevate Aura</a>
            <div class="nav-links" id="navLinks">
                <a href="/" class="nav-link">Home</a>
                <a href="/pages/ssc-daily-practice.html" class="nav-link">SSC</a>
                <a href="/pages/rrb-daily-practice.html" class="nav-link">RRB</a>
                <a href="/pages/bank-daily-practice.html" class="nav-link">Bank</a>
                <a href="/pages/about.html" class="nav-link">About</a>
                <a href="/pages/careers.html" class="nav-link">Careers</a>
                <a href="https://t.me/ElevateAura_Bot" class="btn btn-primary" style="padding: 10px 24px; font-size: 0.9rem;">Start Practice</a>
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
            <a href="/pages/ssc-daily-practice.html" class="mobile-link">SSC Practice</a>
            <a href="/pages/rrb-daily-practice.html" class="mobile-link">RRB Practice</a>
            <a href="/pages/bank-daily-practice.html" class="mobile-link">Bank Practice</a>
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

    // 3. Scroll Animations
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
