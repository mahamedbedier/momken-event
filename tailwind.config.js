/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class', // JS-controlled dark mode via .dark on <html>
  content: [
    "./templates/**/*.html",
    "./static/js/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        /* ── Core Palette — Light & Dark ── */
        darkBg:    '#0a0a0a',
        lightBg:   '#f8f9fc',
        cardBg:    '#0d0d0d',
        cardLight: '#ffffff',

        /* Logo mosaic accent colors */
        accent: {
          red:     '#e11d48',
          magenta: '#c026d3',
          cyan:    '#06b6d4',
          yellow:  '#facc15',
        },

        /* Legacy aliases */
        brand:      '#e11d48',
        neonRose:   '#e11d48',
        holoCyan:   '#06b6d4',
        holoPurple: '#c026d3',
        textMuted:  '#9ca3af',
      },
      fontFamily: {
        sans: ['Outfit', 'system-ui', 'sans-serif'],
      },
      keyframes: {
        glowPulse: {
          '0%, 100%': { boxShadow: '0 0 15px rgba(225,29,72,0.4), 0 0 30px rgba(225,29,72,0.1)' },
          '50%':      { boxShadow: '0 0 25px rgba(225,29,72,0.7), 0 0 50px rgba(225,29,72,0.3)' },
        },
        glowPulseCyan: {
          '0%, 100%': { boxShadow: '0 0 15px rgba(6,182,212,0.3), 0 0 30px rgba(6,182,212,0.1)' },
          '50%':      { boxShadow: '0 0 25px rgba(6,182,212,0.6), 0 0 50px rgba(6,182,212,0.2)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%':      { transform: 'translateY(-8px)' },
        },
        gradientShift: {
          '0%':   { backgroundPosition: '0% 50%' },
          '50%':  { backgroundPosition: '100% 50%' },
          '100%': { backgroundPosition: '0% 50%' },
        },
        shimmer: {
          '0%':   { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition:  '200% 0' },
        },
        fadeInUp: {
          '0%':   { opacity: '0', transform: 'translateY(30px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        orbFloat: {
          '0%, 100%': { transform: 'translate(0, 0) scale(1)' },
          '33%':      { transform: 'translate(30px, -20px) scale(1.05)' },
          '66%':      { transform: 'translate(-20px, 15px) scale(0.95)' },
        },
        orbBreathe: {
          '0%, 100%': { opacity: '0.15', transform: 'scale(1)' },
          '50%':      { opacity: '0.25', transform: 'scale(1.1)' },
        },
        borderGlow: {
          '0%, 100%': { borderColor: 'rgba(225,29,72,0.3)' },
          '50%':      { borderColor: 'rgba(6,182,212,0.5)' },
        },
        /* Floating tech-bubbles animations */
        bubbleDrift1: {
          '0%':   { transform: 'translate(0px, 0px) rotate(0deg)' },
          '25%':  { transform: 'translate(20px, -30px) rotate(6deg)' },
          '50%':  { transform: 'translate(-15px, -60px) rotate(-5deg)' },
          '75%':  { transform: 'translate(25px, -35px) rotate(7deg)' },
          '100%': { transform: 'translate(0px, 0px) rotate(0deg)' },
        },
        bubbleDrift2: {
          '0%':   { transform: 'translate(0px, 0px) rotate(0deg)' },
          '30%':  { transform: 'translate(-25px, 35px) rotate(-6deg)' },
          '60%':  { transform: 'translate(30px, 20px) rotate(8deg)' },
          '100%': { transform: 'translate(0px, 0px) rotate(0deg)' },
        },
        bubbleDrift3: {
          '0%':   { transform: 'translate(0px, 0px) rotate(0deg)' },
          '40%':  { transform: 'translate(35px, -25px) rotate(-8deg)' },
          '70%':  { transform: 'translate(-20px, 40px) rotate(6deg)' },
          '100%': { transform: 'translate(0px, 0px) rotate(0deg)' },
        },
        themeSwitchSpin: {
          '0%':   { transform: 'rotate(0deg) scale(1)' },
          '50%':  { transform: 'rotate(180deg) scale(0.8)' },
          '100%': { transform: 'rotate(360deg) scale(1)' },
        },
      },
      animation: {
        'glow-pulse':         'glowPulse 2.5s ease-in-out infinite',
        'glow-pulse-cyan':    'glowPulseCyan 3s ease-in-out infinite',
        'float':              'float 4s ease-in-out infinite',
        'float-slow':         'float 6s ease-in-out infinite',
        'gradient-shift':     'gradientShift 8s ease infinite',
        'shimmer':            'shimmer 3s linear infinite',
        'fade-in-up':         'fadeInUp 0.8s ease-out forwards',
        'orb-float':          'orbFloat 12s ease-in-out infinite',
        'orb-float-delay':    'orbFloat 15s ease-in-out 3s infinite',
        'orb-breathe':        'orbBreathe 8s ease-in-out infinite',
        'orb-breathe-delay':  'orbBreathe 10s ease-in-out 2s infinite',
        'border-glow':        'borderGlow 4s ease-in-out infinite',
        'bubble-drift-1':     'bubbleDrift1 18s ease-in-out infinite',
        'bubble-drift-2':     'bubbleDrift2 22s ease-in-out infinite',
        'bubble-drift-3':     'bubbleDrift3 16s ease-in-out infinite',
        'theme-spin':         'themeSwitchSpin 0.4s ease-in-out forwards',
      },
      backgroundSize: {
        '300%': '300% 300%',
      },
    },
  },
  plugins: [],
};
