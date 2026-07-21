/**
 * main.js — Shared UI logic
 * - Mobile hamburger menu toggle
 * - Countdown timer for event date
 */

// ═══════════════════════════════════════════════════════════════════════
// Mobile Menu Toggle
// ═══════════════════════════════════════════════════════════════════════

function toggleMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    const panel = menu?.querySelector('.slide-in, .slide-out');

    if (!menu) return;

    if (menu.classList.contains('hidden')) {
        // Open menu
        menu.classList.remove('hidden');
        menu.classList.add('flex');
        if (panel) {
            panel.classList.remove('slide-out');
            panel.classList.add('slide-in');
        }
        document.body.style.overflow = 'hidden';
    } else {
        // Close menu with animation
        if (panel) {
            panel.classList.remove('slide-in');
            panel.classList.add('slide-out');
        }
        setTimeout(() => {
            menu.classList.add('hidden');
            menu.classList.remove('flex');
            document.body.style.overflow = '';
        }, 280);
    }
}

// Close menu on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const menu = document.getElementById('mobile-menu');
        if (menu && !menu.classList.contains('hidden')) {
            toggleMobileMenu();
        }
    }
});


// ═══════════════════════════════════════════════════════════════════════
// Countdown Timer — August 8, 2026 09:00 AM
// ═══════════════════════════════════════════════════════════════════════

(function initCountdown() {
    const daysEl = document.getElementById('days');
    const hoursEl = document.getElementById('hours');
    const minutesEl = document.getElementById('minutes');
    const secondsEl = document.getElementById('seconds');

    // Only run if countdown elements exist on the page
    if (!daysEl) return;

    const eventDate = new Date('August 8, 2026 09:00:00').getTime();

    function pad(n) {
        return n < 10 ? '0' + n : String(n);
    }

    function updateCountdown() {
        const now = Date.now();
        const distance = eventDate - now;

        if (distance < 0) {
            daysEl.textContent = '00';
            hoursEl.textContent = '00';
            minutesEl.textContent = '00';
            secondsEl.textContent = '00';
            return;
        }

        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        daysEl.textContent = pad(days);
        hoursEl.textContent = pad(hours);
        minutesEl.textContent = pad(minutes);
        secondsEl.textContent = pad(seconds);
    }

    updateCountdown();
    setInterval(updateCountdown, 1000);
})();
