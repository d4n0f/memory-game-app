document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('avatar-grid');
    const message = document.getElementById('message');

    function showMessage(text, isError = false) {
        message.textContent = text;
        message.style.color = isError ? '#b00020' : '#1b5e20';
    }

    // Initialize thumbnails and selection
    (async function init() {
        let currentAvatar = null;
        try {
            const u = await api.getJSON('/api/current-user');
            if (u.ok && u.json && u.json.user) currentAvatar = u.json.user.profile_picture || null;
        } catch (e) {
            // ignore
        }

        if (grid) {
            grid.querySelectorAll('.avatar-item').forEach(btn => {
                const src = btn.getAttribute('data-src');
                if (src) btn.style.backgroundImage = `url('${src}')`;
                // mark selected if matches current avatar
                if (currentAvatar && src && src === currentAvatar) btn.classList.add('selected');
            });

            grid.addEventListener('click', async (e) => {
                const btn = e.target.closest('.avatar-item');
                if (!btn) return;
                const src = btn.getAttribute('data-src');
                if (!src) return;

                // optimistic UI
                grid.querySelectorAll('.avatar-item').forEach(x => x.classList.remove('selected'));
                btn.classList.add('selected');
                showMessage('Mentés...');
                try {
                    const resp = await fetch('/api/user/update', {
                        method: 'PATCH',
                        credentials: 'same-origin',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ profile_picture: src })
                    });
                    const text = await resp.text();
                    let json = null;
                    try { json = JSON.parse(text); } catch (e) { }
                    if (!resp.ok) {
                        showMessage((json && json.error) || 'Hiba történt', true);
                        return;
                    }
                    showMessage('Profilkép mentve. Átirányítás...');
                    setTimeout(() => window.location.href = '/profile', 800);
                } catch (err) {
                    showMessage('Hálózati hiba', true);
                    console.error(err);
                }
            });
        }
    })();
});
