document.addEventListener('DOMContentLoaded', () => {
    const usernameInput = document.querySelector('[data-cy="login-username"]');
    const passwordInput = document.querySelector('[data-cy="login-password"]');
    const submitBtn = document.querySelector('[data-cy="login-submit"]');

    function showError(message) {
        // Simple alert for now; could be replaced with inline error element
        alert(message);
    }

    if (!usernameInput || !passwordInput || !submitBtn) return;

    submitBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        const username = usernameInput.value.trim();
        const password = passwordInput.value;

        if (!username || !password) {
            showError('Kérlek, add meg a felhasználónevedet és jelszavadat.');
            return;
        }

        try {
            const result = await api.postJSON('/api/login', { username, password });
            if (result.ok && result.json && result.json.success) {
                if (result.json.player_id) localStorage.setItem('player_id', result.json.player_id);
                if (result.json.username) localStorage.setItem('player_name', result.json.username);
                window.location.href = '/menu';
            } else {
                const message = (result.json && result.json.error) ? result.json.error : (result.text || 'Bejelentkezés sikertelen.');
                showError(message);
            }
        } catch (err) {
            console.error('Login error', err);
            showError('Hálózati hiba történt a bejelentkezés során.');
        }
    });
});
