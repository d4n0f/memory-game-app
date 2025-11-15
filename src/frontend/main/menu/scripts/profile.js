document.addEventListener('DOMContentLoaded', () => {
    const usernameInput = document.getElementById('username');
    const currentPasswordInput = document.getElementById('current-password');
    const newPasswordInput = document.getElementById('new-password');
    const saveBtn = document.getElementById('save-btn');
    const logoutBtn = document.getElementById('logout-btn');
    const messageEl = document.getElementById('message');
    const avatarInput = document.getElementById('avatar-input');
    const avatarPreview = document.getElementById('avatar-preview');
    const avatarChangeBtn = document.getElementById('avatar-change');

    function showMessage(txt, isError=false){
        messageEl.textContent = txt;
        messageEl.style.color = isError ? '#b22222' : '#2a7a3a';
    }

    async function loadCurrentUser(){
        try{
            const res = await api.getJSON('/api/current-user');
            if(res.ok && res.json && res.json.user){
                usernameInput.value = res.json.user.username || '';
            } else {
                showMessage('Nincs bejelentkezve', true);
            }
        } catch(err){
            console.error(err);
            showMessage('Hiba a felhasználó betöltésekor', true);
        }
    }

    // Save handler
    document.getElementById('profile-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        saveBtn.disabled = true;
        showMessage('Mentés...');
        const payload = {};
        const newUsername = usernameInput.value.trim();
        const currentPassword = currentPasswordInput.value;
        const newPassword = newPasswordInput.value;
        if(newUsername) payload.username = newUsername;
        if(newPassword) payload.new_password = newPassword;
        if(newPassword && !currentPassword){
            showMessage('A jelenlegi jelszó megadása kötelező új jelszó megadásakor', true);
            saveBtn.disabled = false;
            return;
        }
        if(currentPassword) payload.current_password = currentPassword;

        try{
            const res = await api.postJSON('/api/user/update', payload); // POST helper supports JSON; backend expects PATCH but accepts JSON body
            // Note: api.postJSON uses fetch with method POST. The backend expects PATCH on /api/user/update.
            // Use fetch directly for PATCH to be correct.
            if(!res.ok){
                showMessage(res.json && res.json.error ? res.json.error : 'Hiba a mentés során', true);
            } else {
                showMessage((res.json && res.json.message) || 'Sikeres mentés');
                // clear password fields
                currentPasswordInput.value = '';
                newPasswordInput.value = '';
            }
        } catch(err){
            console.error(err);
            showMessage('Szerver hiba a mentés során', true);
        } finally{
            saveBtn.disabled = false;
        }
    });

    // Use proper PATCH request for update
    async function patchUpdate(payload){
        const r = await fetch('/api/user/update', {
            method: 'PATCH',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const text = await r.text();
        let json = null;
        try{ json = JSON.parse(text); } catch(e){}
        return { ok: r.ok, status: r.status, json, text };
    }

    // Replace earlier handler to use PATCH correctly
    document.getElementById('profile-form').addEventListener('submit', async (e) => {} , { once: true });
    // Remove the earlier handler and rebind properly
    document.getElementById('profile-form').removeEventListener('submit', null);
    document.getElementById('profile-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        saveBtn.disabled = true;
        showMessage('Mentés...');
        const payload = {};
        const newUsername = usernameInput.value.trim();
        const currentPassword = currentPasswordInput.value;
        const newPassword = newPasswordInput.value;
        if(newUsername) payload.username = newUsername;
        if(newPassword) payload.new_password = newPassword;
        if(newPassword && !currentPassword){
            showMessage('A jelenlegi jelszó megadása kötelező új jelszó megadásakor', true);
            saveBtn.disabled = false;
            return;
        }
        if(currentPassword) payload.current_password = currentPassword;

        try{
            const res = await patchUpdate(payload);
            if(!res.ok){
                showMessage(res.json && res.json.error ? res.json.error : 'Hiba a mentés során', true);
            } else {
                showMessage((res.json && res.json.message) || 'Sikeres mentés');
                currentPasswordInput.value = '';
                newPasswordInput.value = '';
            }
        } catch(err){
            console.error(err);
            showMessage('Szerver hiba a mentés során', true);
        } finally{
            saveBtn.disabled = false;
        }
    });

    // Logout
    logoutBtn.addEventListener('click', async () => {
        try{
            const r = await fetch('/api/logout', { method: 'POST', credentials: 'include' });
            if(r.ok){
                window.location.href = '/';
            } else {
                showMessage('Kijelentkezés sikertelen', true);
            }
        } catch(err){
            console.error(err);
            showMessage('Hiba a kijelentkezés során', true);
        }
    });

    // Initialize
    loadCurrentUser();
});
