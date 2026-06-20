/**
 * Do'kon Market — Liquid Glass UI Interactions
 * Zero-dependency modern JS for UI animations only.
 * Does not handle any backend/API logic.
 */

document.addEventListener('DOMContentLoaded', () => {
    
    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) return;

    /* 1. Navbar Scroll Effect
       -------------------------------------------------- */
    const navbar = document.querySelector('.navbar');
    const scrollThreshold = 50;
    
    // Initial check
    if (window.scrollY > scrollThreshold) {
        navbar?.classList.add('scrolled');
    }

    window.addEventListener('scroll', () => {
        if (window.scrollY > scrollThreshold) {
            navbar?.classList.add('scrolled');
        } else {
            navbar?.classList.remove('scrolled');
        }
    }, { passive: true });


    /* 2. Scroll Reveal Animations (Intersection Observer)
       -------------------------------------------------- */
    const revealElements = document.querySelectorAll('.product-card, .form-section, .order-summary-checkout, .cart-item');
    
    // Add default reveal class to elements we want to animate
    revealElements.forEach(el => {
        el.classList.add('reveal');
        // Wrap parent in stagger if it's a grid/list
        if (el.parentElement && (el.parentElement.classList.contains('products-grid') || el.parentElement.classList.contains('cart-items'))) {
            el.parentElement.classList.add('stagger-children');
        }
    });

    const observerOptions = {
        root: null,
        rootMargin: '0px 0px -50px 0px',
        threshold: 0.1
    };

    const scrollObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
                // Optional: stop observing once revealed for better performance
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Re-select now that classes are added
    document.querySelectorAll('.reveal').forEach(el => {
        scrollObserver.observe(el);
    });


    /* 3. Mobile Bottom Nav Visibility Toggle
       Hide when scrolling down, show when scrolling up
       -------------------------------------------------- */
    const bottomNav = document.querySelector('.mobile-bottom-nav');
    let lastScrollY = window.scrollY;
    let ticking = false;

    if (bottomNav) {
        window.addEventListener('scroll', () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    const currentScrollY = window.scrollY;
                    
                    // Allow rubber-banding at top/bottom without triggering hide/show
                    if (currentScrollY <= 0 || (window.innerHeight + currentScrollY) >= document.body.offsetHeight) {
                        bottomNav.style.transform = 'translateY(0)';
                    } else if (currentScrollY > lastScrollY && currentScrollY > 100) {
                        // Scrolling down — hide (push down by 100%)
                        bottomNav.style.transform = 'translateY(150%)';
                    } else {
                        // Scrolling up — show
                        bottomNav.style.transform = 'translateY(0)';
                    }
                    
                    // Smooth transition
                    bottomNav.style.transition = 'transform 0.4s cubic-bezier(0.16, 1, 0.3, 1)';
                    
                    lastScrollY = currentScrollY;
                    ticking = false;
                });
                ticking = true;
            }
        }, { passive: true });
    }


    /* 4. Filter Bar Smooth Scroll
       If there's a filter bar and URL has params, scroll to it smoothly
       -------------------------------------------------- */
    if (window.location.search) {
        const filterBar = document.querySelector('.filter-bar');
        const headerOffset = 100; // Account for sticky nav
        
        // Only auto-scroll if it's not a fresh visit (e.g. they just applied a filter)
        // Checking for ?page= or ?color= or ?min_price
        if (filterBar && (window.location.search.includes('page=') || window.location.search.includes('color=') || window.location.search.includes('price='))) {
            setTimeout(() => {
                const elementPosition = filterBar.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }, 300); // slight delay to allow layout to settle
        }
    }


    /* 5. Lazy Load Image Enhancements (Fade In)
       -------------------------------------------------- */
    const productImages = document.querySelectorAll('.product-image img');
    
    productImages.forEach(img => {
        // Add skeleton class to parent initially
        if (!img.complete) {
            img.parentElement.classList.add('skeleton');
            img.style.opacity = '0';
        }
        
        img.addEventListener('load', () => {
            img.parentElement.classList.remove('skeleton');
            img.style.opacity = '1';
            img.style.transition = 'opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1), transform 0.7s cubic-bezier(0.16, 1, 0.3, 1)';
        });
        
        // Fallback if already cached
        if (img.complete) {
            img.parentElement.classList.remove('skeleton');
            img.style.opacity = '1';
        }
    });

});
