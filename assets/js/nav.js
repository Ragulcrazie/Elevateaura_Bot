document.addEventListener("DOMContentLoaded", function () {
    var navHTML = `
    <header class="fixed-header">
        <div class="top-bar">
            <div class="container">
                <a href="mailto:elevateauraofficial@gmail.com" style="text-decoration: none;">elevateauraofficial@gmail.com</a>
                <a href="https://www.linkedin.com/in/ragul-sekar/" target="_blank" rel="noopener" style="text-decoration: none; display: flex; align-items: center; gap: 8px;">
                    <span style="background: #0077b5; color: white; border-radius: 4px; padding: 2px 6px; font-weight: bold; font-size: 0.85rem;">in</span> Ragul Sekar
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
                    <a href="/#services" class="nav-link">Services</a>
                    <a href="/#process" class="nav-link">Process</a>
                    <a href="/#pricing" class="nav-link">Pricing</a>
                    <a href="/pages/about.html" class="nav-link">About</a>
                    <a href="/pages/careers.html" class="nav-link">Careers</a>
                    <a href="/pages/contact.html" class="nav-link">Contact</a>
                    <a href="mailto:elevateauraofficial@gmail.com" class="btn btn-primary" style="padding: 10px 20px; font-size: 0.9rem;">Book a Call</a>
                </div>
                <div class="mobile-toggle" id="mobileMenuBtn">
                    <span></span><span></span><span></span>
                </div>
            </div>

            <div class="mobile-menu" id="mobileMenu">
                <a href="/" class="mobile-link">Home</a>
                <a href="/#services" class="mobile-link">Services</a>
                <a href="/#process" class="mobile-link">Process</a>
                <a href="/#pricing" class="mobile-link">Pricing</a>
                <a href="/pages/about.html" class="mobile-link">About</a>
                <a href="/pages/careers.html" class="mobile-link">Careers</a>
                <a href="/pages/contact.html" class="mobile-link">Contact</a>
                <a href="mailto:elevateauraofficial@gmail.com" class="mobile-link" style="color: var(--primary-strong); margin-top: 10px;">Book a Call</a>
            </div>
        </nav>
    </header>
    `;
    document.body.insertAdjacentHTML("afterbegin", navHTML);

    var btn = document.getElementById('mobileMenuBtn');
    var menu = document.getElementById('mobileMenu');
    if (btn && menu) {
        btn.addEventListener('click', function () {
            menu.classList.toggle('active');
            btn.classList.toggle('open');
            if (btn.classList.contains('open')) {
                btn.children[0].style.transform = "rotate(45deg)";
                btn.children[0].style.top = "9px";
                btn.children[1].style.opacity = "0";
                btn.children[2].style.transform = "rotate(-45deg)";
                btn.children[2].style.top = "9px";
            } else {
                btn.children[0].style.transform = "rotate(0)";
                btn.children[0].style.top = "0";
                btn.children[1].style.opacity = "1";
                btn.children[2].style.transform = "rotate(0)";
                btn.children[2].style.top = "18px";
            }
        });
    }
});
