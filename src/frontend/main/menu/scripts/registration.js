document.addEventListener('DOMContentLoaded', () => {
    const usernameInput = document.querySelector('[data-cy="reg-username"]');
    const emailInput = document.querySelector('[data-cy="reg-email"]');
    const passwordInput = document.querySelector('[data-cy="reg-password"]');
    const password2Input = document.querySelector('[data-cy="reg-password2"]');
    const submitBtn = document.querySelector('[data-cy="reg-submit"]');

    function showError(message) {
        alert(message);
    }

    if (!usernameInput || !emailInput || !passwordInput || !password2Input || !submitBtn) return;

    submitBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        const username = usernameInput.value.trim();
        const email = emailInput.value.trim();
        const password = passwordInput.value;
        const password2 = password2Input.value;

        // Basic client-side validation
        if (!username || !email || !password || !password2) {
            showError('Kérlek, töltsd ki az összes mezőt.');
            return;
        }
        if (password !== password2) {
            showError('A megadott jelszavak nem egyeznek.');
            return;
        }
        if (password.length < 6) {
            showError('A jelszónak legalább 6 karakter hosszúnak kell lennie.');
            return;
        }

        try {
            const resp = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'same-origin',
                body: JSON.stringify({ username, email, password })
            });

            const json = await resp.json();
            if (resp.ok && json.success) {
                if (json.player_id) localStorage.setItem('player_id', json.player_id);
                if (json.username) localStorage.setItem('player_name', json.username);

                // Redirect to main menu or directly log the user in
                window.location.href = '/menu';
            } else {
                const message = json && json.error ? json.error : 'Regisztráció sikertelen.';
                showError(message);
            }
        } catch (err) {
            console.error('Registration error', err);
            showError('Hálózati hiba történt a regisztráció során.');
        }
    });
});
