/**
 * checkout.js — Payment form handling
 * - Card number formatting (spaces every 4 digits)
 * - Expiry date formatting (MM/YY)
 * - Submits payment via fetch() to server-side validation
 * - Shows server errors or success modal
 */

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('payment-form');
    const cardNumberInput = document.getElementById('card-number');
    const cardExpiryInput = document.getElementById('card-expiry');
    const errorsContainer = document.getElementById('payment-errors');
    const errorsList = errorsContainer?.querySelector('ul');
    const payBtn = document.getElementById('pay-btn');
    const successModal = document.getElementById('success-modal');

    // ── Card Number Formatting ──────────────────────────────────────
    cardNumberInput?.addEventListener('input', (e) => {
        let value = e.target.value.replace(/\D/g, '');       // Strip non-digits
        value = value.replace(/(.{4})/g, '$1 ').trim();      // Add space every 4
        e.target.value = value;
    });

    // ── Expiry Date Formatting ──────────────────────────────────────
    cardExpiryInput?.addEventListener('input', (e) => {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length >= 2) {
            value = value.substring(0, 2) + '/' + value.substring(2, 4);
        }
        e.target.value = value;
    });

    // ── Form Submission — sends to server-side validation ───────────
    form?.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Clear previous errors
        errorsContainer.classList.add('hidden');
        errorsList.innerHTML = '';

        const cardName = document.getElementById('card-name').value.trim();
        const cardNumber = cardNumberInput.value.trim();
        const cardExpiry = cardExpiryInput.value.trim();
        const cardCvv = document.getElementById('card-cvv').value.trim();

        // Show loading state
        const originalBtnHTML = payBtn.innerHTML;
        payBtn.innerHTML = `
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Processing...`;
        payBtn.disabled = true;
        payBtn.classList.add('opacity-75', 'cursor-not-allowed');

        try {
            const response = await fetch(window.CHECKOUT_CONFIG.processUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ticket_id: window.CHECKOUT_CONFIG.ticketId,
                    card_name: cardName,
                    card_number: cardNumber,
                    card_expiry: cardExpiry,
                    card_cvv: cardCvv,
                }),
            });

            const data = await response.json();

            if (data.success) {
                // Show success modal
                successModal.classList.remove('hidden');
                successModal.classList.add('flex');
            } else {
                // Show server-side validation errors
                data.errors.forEach(err => {
                    const li = document.createElement('li');
                    li.textContent = err;
                    errorsList.appendChild(li);
                });
                errorsContainer.classList.remove('hidden');

                // Reset button
                payBtn.innerHTML = originalBtnHTML;
                payBtn.disabled = false;
                payBtn.classList.remove('opacity-75', 'cursor-not-allowed');
            }
        } catch (err) {
            errorsList.innerHTML = '<li>Network error. Please try again.</li>';
            errorsContainer.classList.remove('hidden');
            payBtn.innerHTML = originalBtnHTML;
            payBtn.disabled = false;
            payBtn.classList.remove('opacity-75', 'cursor-not-allowed');
        }
    });
});
