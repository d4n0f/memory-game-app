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
            const resp = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'same-origin',
                body: JSON.stringify({ username, password })
            });

            const json = await resp.json();
            if (resp.ok && json.success) {
                // Save useful info locally for frontend usage
                if (json.player_id) localStorage.setItem('player_id', json.player_id);
                if (json.username) localStorage.setItem('player_name', json.username);

                // Redirect to menu (or other desired page)
                window.location.href = '/menu';
            } else {
                const message = json && json.error ? json.error : 'Bejelentkezés sikertelen.';
                showError(message);
            }
        } catch (err) {
            console.error('Login error', err);
            showError('Hálózati hiba történt a bejelentkezés során.');
        }
    });
});
