/**
 * admin.js — Admin Dashboard logic
 * - Fetches stats, chart data, and user list from API
 * - Renders Chart.js line chart for registrations
 * - Searchable users table with debouncing
 * - Admin actions: Delete user, Mark as paid, Change ticket type
 */

/** Cached ticket types for the dropdown */
let ticketTypes = [];

document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadChart();
    loadTicketTypes().then(() => loadUsers());

    // Search with debounce
    const searchInput = document.getElementById('user-search');
    let debounceTimer;
    searchInput?.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            loadUsers(searchInput.value.trim());
        }, 300);
    });
});


// ═══════════════════════════════════════════════════════════════════════
// 1. Top Metrics
// ═══════════════════════════════════════════════════════════════════════

async function loadStats() {
    try {
        const res = await fetch(window.ADMIN_URLS.stats);
        const data = await res.json();

        document.getElementById('metric-users').textContent = data.total_users;
        document.getElementById('metric-orders').textContent = data.total_orders;
        document.getElementById('metric-revenue').textContent = data.total_revenue.toLocaleString() + ' EGP';
    } catch (err) {
        console.error('Failed to load stats:', err);
    }
}


// ═══════════════════════════════════════════════════════════════════════
// 2. Registrations Line Chart (Chart.js)
// ═══════════════════════════════════════════════════════════════════════

async function loadChart() {
    try {
        const res = await fetch(window.ADMIN_URLS.chart);
        const data = await res.json();

        const ctx = document.getElementById('registrations-chart')?.getContext('2d');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels.map(d => {
                    const date = new Date(d);
                    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                }),
                datasets: [{
                    label: 'New Users',
                    data: data.data,
                    borderColor: '#e6003a',
                    backgroundColor: 'rgba(230, 0, 58, 0.1)',
                    borderWidth: 2,
                    pointBackgroundColor: '#e6003a',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    tension: 0.3,
                    fill: true,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false,
                    },
                    tooltip: {
                        backgroundColor: '#0d1536',
                        borderColor: 'rgba(255,255,255,0.1)',
                        borderWidth: 1,
                        titleColor: '#fff',
                        bodyColor: '#8b95b5',
                        padding: 12,
                    },
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#8b95b5', font: { size: 11 } },
                    },
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: {
                            color: '#8b95b5',
                            font: { size: 11 },
                            stepSize: 1,
                        },
                    },
                },
            },
        });
    } catch (err) {
        console.error('Failed to load chart:', err);
    }
}


// ═══════════════════════════════════════════════════════════════════════
// 3. Load Ticket Types (for dropdown)
// ═══════════════════════════════════════════════════════════════════════

async function loadTicketTypes() {
    try {
        const res = await fetch(window.ADMIN_URLS.ticketTypes);
        const data = await res.json();
        ticketTypes = data.ticket_types || [];
    } catch (err) {
        console.error('Failed to load ticket types:', err);
    }
}


// ═══════════════════════════════════════════════════════════════════════
// 4. Users Table with Search & Actions
// ═══════════════════════════════════════════════════════════════════════

async function loadUsers(query = '') {
    const tbody = document.getElementById('users-table-body');
    const countEl = document.getElementById('users-count');

    if (!tbody) return;

    try {
        const url = query
            ? `${window.ADMIN_URLS.users}?q=${encodeURIComponent(query)}`
            : window.ADMIN_URLS.users;

        const res = await fetch(url);
        const data = await res.json();

        if (data.users.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="py-8 text-center text-textMuted">No users found.</td></tr>`;
            countEl.textContent = '0 users';
            return;
        }

        tbody.innerHTML = data.users.map(user => {
            // Status badge
            const isPaid = user.order_status === 'completed';
            const statusBadge = user.order_status === 'none'
                ? `<span class="text-[10px] font-bold px-2 py-0.5 rounded bg-white/5 text-textMuted uppercase">No order</span>`
                : isPaid
                    ? `<span class="text-[10px] font-bold px-2 py-0.5 rounded bg-green-500/15 text-green-400 uppercase">Paid</span>`
                    : `<span class="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-500/15 text-amber-400 uppercase">Unpaid</span>`;

            // Ticket type badge
            const ticketBadge = `<span class="text-xs font-bold px-2 py-1 rounded
                ${user.ticket_type.includes('VIP') ? 'bg-brand/20 text-brand' :
                  user.ticket_type.includes('Coaching') ? 'bg-purple-500/20 text-purple-400' :
                  user.ticket_type.includes('No ticket') ? 'bg-white/5 text-textMuted' :
                  'bg-white/10 text-white'}">
                ${escapeHtml(user.ticket_type)}
            </span>`;

            // Ticket type dropdown options
            const ticketOptions = ticketTypes.map(t =>
                `<option value="${t.id}" ${t.id === user.ticket_type_id ? 'selected' : ''}>${escapeHtml(t.name)}</option>`
            ).join('');

            // Build toggle payment button
            const togglePaymentBtn = isPaid
                ? `<button onclick="togglePayment(${user.id})" title="Undo Payment (Mark Unpaid)"
                     class="inline-flex items-center gap-1 px-2 py-1 rounded text-[10px] font-bold uppercase
                            bg-amber-500/10 text-amber-400 border border-amber-500/20
                            hover:bg-amber-500/20 transition-all">
                     <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                     Unpaid
                   </button>`
                : `<button onclick="togglePayment(${user.id})" title="Mark as Paid"
                     class="inline-flex items-center gap-1 px-2 py-1 rounded text-[10px] font-bold uppercase
                            bg-green-500/10 text-green-400 border border-green-500/20
                            hover:bg-green-500/20 transition-all">
                     <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                     Paid
                   </button>`;

            const deleteBtn = `<button onclick="deleteUser(${user.id}, '${escapeHtml(user.name).replace(/'/g, "\\'")}')" title="Delete User"
                 class="inline-flex items-center gap-1 px-2 py-1 rounded text-[10px] font-bold uppercase
                        bg-red-500/10 text-red-400 border border-red-500/20
                        hover:bg-red-500/20 transition-all">
                 <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                 Del
               </button>`;

            return `
            <tr class="border-b border-white/5 hover:bg-white/[0.02] transition" id="user-row-${user.id}">
                <td class="py-3 pr-4 font-medium text-white">${escapeHtml(user.name)}</td>
                <td class="py-3 pr-4 text-textMuted text-xs">${escapeHtml(user.email)}</td>
                <td class="py-3 pr-4 text-textMuted text-xs">${escapeHtml(user.phone)}</td>
                <td class="py-3 pr-4">
                    <select onchange="changeTicket(${user.id}, this.value)"
                            class="bg-darkBg border border-white/10 text-white text-xs rounded px-2 py-1 focus:border-brand focus:outline-none cursor-pointer">
                        <option value="" ${!user.ticket_type_id ? 'selected' : ''} disabled>No ticket</option>
                        ${ticketOptions}
                    </select>
                </td>
                <td class="py-3 pr-4">${statusBadge}</td>
                <td class="py-3 pr-4 text-textMuted text-xs">${escapeHtml(user.registered)}</td>
                <td class="py-3">
                    <div class="flex items-center gap-1.5 flex-wrap">
                        ${togglePaymentBtn}
                        ${deleteBtn}
                    </div>
                </td>
            </tr>
        `;
        }).join('');

        countEl.textContent = `${data.total} user${data.total !== 1 ? 's' : ''} found`;
    } catch (err) {
        console.error('Failed to load users:', err);
        tbody.innerHTML = `<tr><td colspan="7" class="py-8 text-center text-red-400">Failed to load users.</td></tr>`;
    }
}


// ═══════════════════════════════════════════════════════════════════════
// 5. Admin Actions (AJAX)
// ═══════════════════════════════════════════════════════════════════════

/**
 * Delete a user and their orders.
 */
async function deleteUser(userId, userName) {
    if (!confirm(`Are you sure you want to delete "${userName}"? This will remove all their data permanently.`)) {
        return;
    }

    try {
        const res = await fetch(`/admin/api/users/${userId}`, { method: 'DELETE' });
        const data = await res.json();

        if (data.success) {
            // Animate row removal
            const row = document.getElementById(`user-row-${userId}`);
            if (row) {
                row.style.transition = 'opacity 0.3s, transform 0.3s';
                row.style.opacity = '0';
                row.style.transform = 'translateX(20px)';
                setTimeout(() => row.remove(), 300);
            }
            showToast(data.message, 'success');
            // Refresh stats
            loadStats();
        } else {
            showToast(data.error || 'Failed to delete user.', 'error');
        }
    } catch (err) {
        console.error('Delete user failed:', err);
        showToast('Network error. Please try again.', 'error');
    }
}

/**
 * Toggle a user's payment status between paid (completed) and unpaid (pending).
 */
async function togglePayment(userId) {
    try {
        const res = await fetch(`/admin/api/users/${userId}/toggle-payment`, { method: 'PATCH' });
        const data = await res.json();

        if (data.success) {
            showToast(data.message, 'success');
            // Refresh the table to reflect updated status
            const searchVal = document.getElementById('user-search')?.value?.trim() || '';
            loadUsers(searchVal);
            loadStats();
        } else {
            showToast(data.error || 'Failed to toggle payment.', 'error');
        }
    } catch (err) {
        console.error('Toggle payment failed:', err);
        showToast('Network error. Please try again.', 'error');
    }
}

/**
 * Change a user's ticket type.
 */
async function changeTicket(userId, ticketTypeId) {
    if (!ticketTypeId) return;

    try {
        const res = await fetch(`/admin/api/users/${userId}/ticket`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticket_type_id: parseInt(ticketTypeId) }),
        });
        const data = await res.json();

        if (data.success) {
            showToast(data.message, 'success');
        } else {
            showToast(data.error || 'Failed to change ticket.', 'error');
            // Reload to revert dropdown
            const searchVal = document.getElementById('user-search')?.value?.trim() || '';
            loadUsers(searchVal);
        }
    } catch (err) {
        console.error('Change ticket failed:', err);
        showToast('Network error. Please try again.', 'error');
    }
}


// ═══════════════════════════════════════════════════════════════════════
// 6. Toast Notifications
// ═══════════════════════════════════════════════════════════════════════

/**
 * Show a toast notification at the top-right of the screen.
 * @param {string} message - The message to display
 * @param {'success'|'error'|'info'} type - The toast type
 */
function showToast(message, type = 'info') {
    // Create or find the toast container
    let container = document.getElementById('admin-toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'admin-toast-container';
        container.className = 'fixed top-24 right-6 z-[60] space-y-3 max-w-sm';
        document.body.appendChild(container);
    }

    const colors = {
        success: 'bg-green-900/80 border-green-500/40 text-green-200',
        error: 'bg-red-900/80 border-red-500/40 text-red-200',
        info: 'bg-blue-900/80 border-blue-500/40 text-blue-200',
    };

    const toast = document.createElement('div');
    toast.className = `flex items-center gap-3 px-5 py-3 rounded-lg border backdrop-blur-sm shadow-xl ${colors[type] || colors.info}`;
    toast.style.animation = 'fadeIn 0.4s ease-out';
    toast.innerHTML = `
        <span class="text-sm font-medium">${escapeHtml(message)}</span>
        <button onclick="this.parentElement.remove()" class="ml-auto text-white/60 hover:text-white text-lg">&times;</button>
    `;

    container.appendChild(toast);

    // Auto-dismiss after 4 seconds
    setTimeout(() => {
        toast.style.transition = 'opacity 0.4s';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}


// ═══════════════════════════════════════════════════════════════════════
// Utilities
// ═══════════════════════════════════════════════════════════════════════

/**
 * Escape HTML to prevent XSS in dynamically rendered content.
 */
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
