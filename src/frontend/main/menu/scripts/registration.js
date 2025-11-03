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

            const resp = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'same-origin',
                body: JSON.stringify(payload)
            });

            const text = await resp.text(); // read raw body for better debugging
            let json;
            try { json = JSON.parse(text); } catch(e) { json = null; }

            console.log('Register response status:', resp.status);
            console.log('Register response body:', text);

            if (resp.ok && json && json.success) {
                if (json.player_id) localStorage.setItem('player_id', json.player_id);
                if (json.username) localStorage.setItem('player_name', json.username);
                window.location.href = '/menu';
            } else {
                const message = (json && json.error) ? json.error : text || 'Regisztráció sikertelen.';
                showError(message);
            }
        } catch (err) {
            console.error('Registration error', err);
            showError('Hálózati hiba történt a regisztráció során.');
        }
    });
});
