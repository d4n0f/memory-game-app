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
            const payload = { username, email, password };
            console.log('Register payload:', payload);

            const result = await api.postJSON('/api/register', payload);
            console.log('Register response status:', result.status);
            console.log('Register response body:', result.text);

            if (result.ok && result.json && result.json.success) {
                if (result.json.player_id) localStorage.setItem('player_id', result.json.player_id);
                if (result.json.username) localStorage.setItem('player_name', result.json.username);
                window.location.href = '/menu';
            } else {
                const message = (result.json && result.json.error) ? result.json.error : result.text || 'Regisztráció sikertelen.';
                showError(message);
            }
        } catch (err) {
            console.error('Registration error', err);
            showError('Hálózati hiba történt a regisztráció során.');
        }
    });
});
