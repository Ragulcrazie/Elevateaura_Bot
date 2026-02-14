document.addEventListener("DOMContentLoaded", function() {
    // 1. Inject Navigation
    const navHTML = `
    <nav class="nav">
        <div class="container nav-inner">
            <a href="/" class="logo">Elevate Aura</a>
            <div class="nav-links">
                <a href="/pages/ssc-daily-practice.html" class="nav-link">SSC</a>
                <a href="/pages/rrb-daily-practice.html" class="nav-link">RRB</a>
                <a href="/pages/bank-daily-practice.html" class="nav-link">Bank</a>
                <a href="/pages/about.html" class="nav-link">About</a>
                <a href="/pages/careers.html" class="nav-link">Careers</a>
                <a href="https://t.me/ElevateAura_Bot" class="btn btn-primary" style="padding: 10px 24px; font-size: 0.9rem;">Start Practice</a>
            </div>
            <div class="mobile-toggle">â˜°</div>
        </div>
    </nav>
    `;
    document.body.insertAdjacentHTML("afterbegin", navHTML);

    // 2. Scroll Animations
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
