/**
 * theme-toggle.js
 * Manages Light ↔ Dark mode via localStorage + .dark class on <html> & <body>
 * DEFAULT IS LIGHT MODE unless localStorage contains 'dark'
 */
(function () {
  const STORAGE_KEY = 'momken-theme';
  const root = document.documentElement;

  // Helper to update all theme toggle icons & text across navbar and mobile menu
  function syncThemeUI(isDark) {
    const icon = document.getElementById('theme-icon');
    const text = document.getElementById('theme-text');
    const mobileIcon = document.getElementById('theme-icon-mobile');

    const symbol = isDark ? '🌙' : '☀️';
    const label  = isDark ? 'Dark Mode' : 'Light Mode';

    if (icon) icon.textContent = symbol;
    if (text) text.textContent = label;
    if (mobileIcon) mobileIcon.textContent = symbol;

    const btn = document.getElementById('theme-toggle-btn');
    if (btn) btn.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
  }

  // Master toggle function called by navbar theme buttons
  window.toggleTheme = function () {
    const isDark = root.classList.toggle('dark');
    if (document.body) {
      document.body.classList.toggle('dark', isDark);
    }
    localStorage.setItem(STORAGE_KEY, isDark ? 'dark' : 'light');

    const icon = document.getElementById('theme-icon');
    if (icon) {
      icon.style.transition = 'transform 0.3s ease, opacity 0.2s ease';
      icon.style.opacity = '0';
      icon.style.transform = 'rotate(180deg) scale(0.7)';
      setTimeout(() => {
        syncThemeUI(isDark);
        icon.style.opacity = '1';
        icon.style.transform = 'rotate(0deg) scale(1)';
      }, 150);
    } else {
      syncThemeUI(isDark);
    }
  };

  // Sync icon and text state on DOM load
  document.addEventListener('DOMContentLoaded', function () {
    const isDark = root.classList.contains('dark');
    if (document.body) {
      document.body.classList.toggle('dark', isDark);
    }
    syncThemeUI(isDark);
  });
})();
