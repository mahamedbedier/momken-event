/**
 * auth.js — Login/Signup tab switching and client-side password match validation
 */

function switchTab(tab) {
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const btnLogin = document.getElementById('btn-login');
    const btnSignup = document.getElementById('btn-signup');

    if (tab === 'login') {
        loginForm.classList.remove('hidden');
        signupForm.classList.add('hidden');
        btnLogin.className = 'flex-1 py-3 text-brand border-b-2 border-brand font-bold uppercase tracking-wider text-sm transition';
        btnSignup.className = 'flex-1 py-3 text-textMuted border-b-2 border-transparent font-bold uppercase tracking-wider text-sm hover:text-white transition';
    } else {
        signupForm.classList.remove('hidden');
        loginForm.classList.add('hidden');
        btnSignup.className = 'flex-1 py-3 text-brand border-b-2 border-brand font-bold uppercase tracking-wider text-sm transition';
        btnLogin.className = 'flex-1 py-3 text-textMuted border-b-2 border-transparent font-bold uppercase tracking-wider text-sm hover:text-white transition';
    }
}

// Client-side password match check before form submission
document.addEventListener('DOMContentLoaded', () => {
    const signupForm = document.getElementById('signup-form');
    if (!signupForm) return;

    signupForm.addEventListener('submit', (e) => {
        const pass = document.getElementById('reg-pass').value;
        const confirm = document.getElementById('reg-confirm').value;
        const errorMsg = document.getElementById('pass-error');

        if (pass !== confirm) {
            e.preventDefault();
            errorMsg.classList.remove('hidden');
            return;
        }
        errorMsg.classList.add('hidden');
    });
});
