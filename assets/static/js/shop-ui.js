/**
 * Shop UI — iOS-inspired interactions
 * Lightweight, gesture-friendly, zero dependencies.
 */

document.addEventListener('DOMContentLoaded', () => {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    /* 1. Navbar - consistent liquid glass, no scroll behavior change */
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        // Ensure consistent liquid glass appearance, no scroll-based opacity changes
        navbar.style.background = 'rgba(0, 0, 0, 0.45)';
    }

    /* 2. Scroll Reveal (Intersection Observer)
       -------------------------------------------------- */
    if (!prefersReducedMotion) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    observer.unobserve(entry.target);
                }
            });
        }, { rootMargin: '0px 0px -40px 0px', threshold: 0.05 });

        document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
    } else {
        document.querySelectorAll('.reveal').forEach(el => el.classList.add('revealed'));
    }

    /* 3. Bottom Nav hide/show on scroll
       -------------------------------------------------- */
    const bottomNav = document.querySelector('.mobile-bottom-nav');
    if (bottomNav) {
        let lastScrollY = 0;
        let ticking = false;
        window.addEventListener('scroll', () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    const sy = window.scrollY;
                    if (sy <= 0 || (window.innerHeight + sy) >= document.body.offsetHeight) {
                        bottomNav.style.transform = 'translateX(-50%) translateY(0)';
                    } else if (sy > lastScrollY && sy > 80) {
                        bottomNav.style.transform = 'translateX(-50%) translateY(calc(100% + 20px))';
                    } else {
                        bottomNav.style.transform = 'translateX(-50%) translateY(0)';
                    }
                    lastScrollY = sy;
                    ticking = false;
                });
                ticking = true;
            }
        }, { passive: true });
    }

    /* 4. Image lazy load fade-in
       -------------------------------------------------- */
    document.querySelectorAll('.product-image img').forEach(img => {
        if (!img.complete) {
            img.parentElement?.classList.add('skeleton');
            img.style.opacity = '0';
        }
        img.addEventListener('load', () => {
            img.parentElement?.classList.remove('skeleton');
            img.style.opacity = '1';
            img.style.transition = 'opacity 0.4s ease';
        }, { once: true });
        if (img.complete) {
            img.parentElement?.classList.remove('skeleton');
            img.style.opacity = '1';
        }
    });

    /* 5. Promo Banner
       -------------------------------------------------- */
    const promoBanner = document.getElementById('promoBanner');
    if (promoBanner) {
        promoBanner.style.display = localStorage.getItem('promoDismissed') ? 'none' : 'flex';
    }

    /* 6. Quick-add haptic feedback (subtle scale)
       -------------------------------------------------- */
    document.querySelectorAll('.quick-add-btn, .btn, .cart-link, .filter-toggle-btn').forEach(btn => {
        btn.addEventListener('touchstart', () => {
            btn.style.transform = 'scale(0.97)';
        }, { passive: true });
        btn.addEventListener('touchend', () => {
            btn.style.transform = '';
        }, { passive: true });
    });
});

/* ── Global Functions ─────────────────────────────────────────── */
function toggleMobileSearch() {
    const overlay = document.getElementById('mobileSearchOverlay');
    const input = document.getElementById('mobileSearchInput');
    if (!overlay) return;
    const isOpen = overlay.classList.contains('open');
    if (isOpen) {
        overlay.classList.remove('open');
        input?.blur();
    } else {
        overlay.classList.add('open');
        setTimeout(() => input?.focus(), 200);
    }
}

function dismissPromoBanner() {
    const el = document.getElementById('promoBanner');
    if (el) { el.style.display = 'none'; localStorage.setItem('promoDismissed', 'true'); }
}

function toggleFilterPanel() {
    document.getElementById('filterPanel')?.classList.toggle('active');
}

function selectColor(id, name, el) {
    document.getElementById('selectedColor').value = id;
    document.getElementById('colorNameDisplay').textContent = name;
    document.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('active'));
    el.classList.add('active');
}

function selectSize(id, name, el) {
    document.getElementById('selectedSize').value = id;
    document.getElementById('sizeNameDisplay').textContent = name;
    document.querySelectorAll('.size-pill').forEach(p => p.classList.remove('active'));
    el.classList.add('active');
}