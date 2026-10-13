/**
 * Browser History Manager - Frontend JavaScript
 * Connects UI interactions to the Python Flask REST API.
 * Preserves Python DSA Stack Data Structure execution on the backend.
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Element References
    const urlForm = document.getElementById('urlForm');
    const urlInput = document.getElementById('urlInput');
    const visitBtn = document.getElementById('visitBtn');
    const backBtn = document.getElementById('backBtn');
    const forwardBtn = document.getElementById('forwardBtn');
    const clearBtn = document.getElementById('clearBtn');

    const currentPageDisplay = document.getElementById('currentPageDisplay');
    const currentStatusBadge = document.getElementById('currentStatusBadge');
    const openLinkBtn = document.getElementById('openLinkBtn');

    const backStackCount = document.getElementById('backStackCount');
    const backStackContainer = document.getElementById('backStackContainer');

    const forwardStackCount = document.getElementById('forwardStackCount');
    const forwardStackContainer = document.getElementById('forwardStackContainer');

    const prevVisitedList = document.getElementById('prevVisitedList');
    const historyCurrentPageCard = document.getElementById('historyCurrentPageCard');
    const forwardHistoryList = document.getElementById('forwardHistoryList');
    const toastContainer = document.getElementById('toastContainer');

    // Quick Test Chips
    const chips = document.querySelectorAll('.chip');
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            const sampleUrl = chip.getAttribute('data-url');
            if (sampleUrl) {
                urlInput.value = sampleUrl;
                urlInput.focus();
            }
        });
    });

    /**
     * Display a modern toast notification for user feedback
     */
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        const icon = type === 'success' ? '✓' : type === 'error' ? '✗' : 'ℹ';
        toast.innerHTML = `
            <span class="toast-icon">${icon}</span>
            <span class="toast-message">${escapeHtml(message)}</span>
        `;

        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(-10px)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3200);
    }

    /**
     * Escape HTML string helper to prevent injection
     */
    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    /**
     * Render a Stack Panel (Back Stack or Forward Stack)
     * In Python, stack = [...] where the LAST element is the TOP of the stack.
     * In this UI, we render items vertically with TOP clearly indicated at the top of the container.
     */
    function renderStack(container, stackList, isBack) {
        if (!stackList || stackList.length === 0) {
            container.innerHTML = `
                <div class="empty-stack-placeholder">
                    <span class="empty-icon">📭</span>
                    <p>${isBack ? 'Back stack is empty' : 'Forward stack is empty'}</p>
                    <span class="empty-sub">${isBack ? 'No previous pages to pop' : 'No forward pages to pop'}</span>
                </div>
            `;
            return;
        }

        container.innerHTML = '';
        const total = stackList.length;

        // Iterate from top of stack (last index) down to bottom (index 0)
        for (let i = total - 1; i >= 0; i--) {
            const url = stackList[i];
            const isTop = (i === total - 1);
            const isBottom = (i === 0);

            const item = document.createElement('div');
            item.className = `stack-item ${isTop ? 'is-top' : ''}`;

            let markers = '';
            if (isTop && isBottom) {
                markers = '<span class="stack-marker marker-top">▲ TOP &amp; BOTTOM</span>';
            } else if (isTop) {
                markers = '<span class="stack-marker marker-top">▲ TOP (Next Pop)</span>';
            } else if (isBottom) {
                markers = '<span class="stack-marker marker-bottom">▼ BOTTOM</span>';
            }

            item.innerHTML = `
                <div class="stack-item-header">
                    <span class="stack-item-index">Index [${i}]</span>
                    ${markers}
                </div>
                <div class="stack-item-url" title="${escapeHtml(url)}">${escapeHtml(url)}</div>
            `;

            container.appendChild(item);
        }
    }

    /**
     * Update Current Page Section
     */
    function updateCurrentPage(currentPage) {
        if (currentPage) {
            currentPageDisplay.textContent = currentPage;
            currentPageDisplay.classList.remove('empty');
            currentStatusBadge.textContent = 'Active Page';
            currentStatusBadge.className = 'badge badge-success';

            openLinkBtn.href = currentPage;
            openLinkBtn.classList.remove('disabled');
            openLinkBtn.title = `Open ${currentPage} in new tab`;
        } else {
            currentPageDisplay.textContent = 'No page is currently open.';
            currentPageDisplay.classList.add('empty');
            currentStatusBadge.textContent = 'No Page';
            currentStatusBadge.className = 'badge badge-muted';

            openLinkBtn.href = '#';
            openLinkBtn.classList.add('disabled');
            openLinkBtn.title = 'No active page to open';
        }
    }

    /**
     * Update Complete Browsing History Section (Operation 5)
     */
    function updateHistorySection(historyData) {
        // 1. Previously Visited
        const prevVisited = historyData.previously_visited || [];
        if (prevVisited.length === 0) {
            prevVisitedList.innerHTML = '<li class="empty-item">No previous pages.</li>';
        } else {
            prevVisitedList.innerHTML = prevVisited
                .map(page => `<li>${escapeHtml(page)}</li>`)
                .join('');
        }

        // 2. Current Page in History Section
        const current = historyData.current_page;
        if (current) {
            historyCurrentPageCard.innerHTML = `
                <div class="current-highlight-box">
                    <span class="current-highlight-title">Active Browser Page</span>
                    <span class="current-highlight-url">${escapeHtml(current)}</span>
                </div>
            `;
        } else {
            historyCurrentPageCard.innerHTML = '<span class="empty-item">No page is currently open.</span>';
        }

        // 3. Forward History
        const forwardHistory = historyData.forward_history || [];
        if (forwardHistory.length === 0) {
            forwardHistoryList.innerHTML = '<li class="empty-item">No forward pages.</li>';
        } else {
            forwardHistoryList.innerHTML = forwardHistory
                .map(page => `<li>${escapeHtml(page)}</li>`)
                .join('');
        }
    }

    /**
     * Fetch complete state and history from Flask REST API
     */
    async function refreshAppState() {
        try {
            // 1. Fetch current state (GET /api/state)
            const stateRes = await fetch('/api/state');
            const state = await stateRes.json();

            if (state.success) {
                // Update navigation buttons enabled/disabled state
                backBtn.disabled = !state.can_go_back;
                forwardBtn.disabled = !state.can_go_forward;

                // Update current page display
                updateCurrentPage(state.current_page);

                // Update stack counts if elements exist
                if (backStackCount) {
                    backStackCount.textContent = `${state.back_count} ${state.back_count === 1 ? 'item' : 'items'}`;
                }
                if (forwardStackCount) {
                    forwardStackCount.textContent = `${state.forward_count} ${state.forward_count === 1 ? 'item' : 'items'}`;
                }

                // Render stack visualizations if containers exist
                if (backStackContainer) {
                    renderStack(backStackContainer, state.back_stack, true);
                }
                if (forwardStackContainer) {
                    renderStack(forwardStackContainer, state.forward_stack, false);
                }
            }

            // 2. Fetch history (GET /api/history)
            const historyRes = await fetch('/api/history');
            const historyData = await historyRes.json();
            if (historyData.success) {
                updateHistorySection(historyData);
            }
        } catch (err) {
            console.error('Error refreshing app state:', err);
            showToast('Unable to communicate with Flask server.', 'error');
        }
    }

    /**
     * Operation 1: Visit Website (POST /api/visit)
     */
    async function handleVisitWebsite(url) {
        if (!url || !url.trim()) {
            showToast('URL cannot be empty.', 'error');
            urlInput.focus();
            return;
        }

        try {
            visitBtn.disabled = true;
            const res = await fetch('/api/visit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: url.trim() })
            });

            const data = await res.json();
            if (data.success) {
                showToast(data.message || `Visited: ${url}`, 'success');
                urlInput.value = '';
            } else {
                showToast(data.message || 'Failed to visit website.', 'error');
            }
        } catch (err) {
            console.error('Error during visit operation:', err);
            showToast('Server connection failed.', 'error');
        } finally {
            visitBtn.disabled = false;
            await refreshAppState();
        }
    }

    /**
     * Operation 2: Go Back (POST /api/back)
     */
    async function handleGoBack() {
        try {
            backBtn.disabled = true;
            const res = await fetch('/api/back', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            const data = await res.json();
            if (data.success) {
                showToast(data.message || 'Navigated back.', 'info');
            } else {
                showToast(data.message || 'No previous page available.', 'error');
            }
        } catch (err) {
            console.error('Error during back operation:', err);
            showToast('Server connection failed.', 'error');
        } finally {
            await refreshAppState();
        }
    }

    /**
     * Operation 3: Go Forward (POST /api/forward)
     */
    async function handleGoForward() {
        try {
            forwardBtn.disabled = true;
            const res = await fetch('/api/forward', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            const data = await res.json();
            if (data.success) {
                showToast(data.message || 'Navigated forward.', 'info');
            } else {
                showToast(data.message || 'No forward page available.', 'error');
            }
        } catch (err) {
            console.error('Error during forward operation:', err);
            showToast('Server connection failed.', 'error');
        } finally {
            await refreshAppState();
        }
    }

    /**
     * Operation 6: Clear History (DELETE /api/history)
     */
    async function handleClearHistory() {
        try {
            clearBtn.disabled = true;
            const res = await fetch('/api/history', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' }
            });

            const data = await res.json();
            if (data.success) {
                showToast(data.message || 'Browser history cleared.', 'success');
            } else {
                showToast(data.message || 'Failed to clear history.', 'error');
            }
        } catch (err) {
            console.error('Error during clear history operation:', err);
            showToast('Server connection failed.', 'error');
        } finally {
            clearBtn.disabled = false;
            await refreshAppState();
        }
    }

    // Event Listeners
    urlForm.addEventListener('submit', (e) => {
        e.preventDefault();
        handleVisitWebsite(urlInput.value);
    });

    visitBtn.addEventListener('click', (e) => {
        e.preventDefault();
        handleVisitWebsite(urlInput.value);
    });

    backBtn.addEventListener('click', handleGoBack);
    forwardBtn.addEventListener('click', handleGoForward);
    clearBtn.addEventListener('click', handleClearHistory);

    // Initial State Fetch upon page load
    refreshAppState();
});
