document.addEventListener('DOMContentLoaded', () => {
    const usernameInput = document.getElementById('username');
    const currentPasswordInput = document.getElementById('current-password');
    const newPasswordInput = document.getElementById('new-password');
    const saveBtn = document.getElementById('save-btn');
    const logoutBtn = document.getElementById('logout-btn');
    const cancelBtn = document.getElementById('cancel-btn');
    const messageEl = document.getElementById('message');
    const avatarPreview = document.getElementById('avatar-preview');
    const avatarChangeBtn = document.getElementById('avatar-change');
    const avatarChooser = document.getElementById('avatar-chooser');
    const avatarGrid = document.getElementById('avatar-grid');

    let selectedAvatar = null; // path string

    function showMessage(txt, isError=false){
        messageEl.textContent = txt;
        messageEl.style.color = isError ? '#b22222' : '#2a7a3a';
    }

    async function loadCurrentUser(){
        try{
            const res = await api.getJSON('/api/current-user');
            if(res.ok && res.json && res.json.user){
                usernameInput.value = res.json.user.username || '';
                // backend may return profile_picture in some responses; if present, show it
                if(res.json.user.profile_picture){
                    selectedAvatar = res.json.user.profile_picture;
                    avatarPreview.style.backgroundImage = `url('${selectedAvatar}')`;
                }
            } else {
                showMessage('Nincs bejelentkezve', true);
            }
        } catch(err){
            console.error(err);
            showMessage('Hiba a felhasználó betöltésekor', true);
        }
    }

    // PATCH helper
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

    // Avatar chooser
    avatarChangeBtn.addEventListener('click', () => {
        const visible = avatarChooser.getAttribute('aria-hidden') === 'false';
        avatarChooser.setAttribute('aria-hidden', String(!visible));
        avatarChooser.style.display = visible ? 'none' : 'block';
    });

    if(avatarGrid){
        avatarGrid.querySelectorAll('.avatar-item').forEach(btn => {
            const src = btn.dataset.src;
            // set placeholder background so the empty image path still shows a blank area
            btn.style.backgroundImage = `url('${src}')`;
            btn.addEventListener('click', () => {
                avatarGrid.querySelectorAll('.avatar-item').forEach(x => x.classList.remove('selected'));
                btn.classList.add('selected');
                selectedAvatar = src;
                avatarPreview.style.backgroundImage = `url('${src}')`;
                avatarChooser.setAttribute('aria-hidden', 'true');
                avatarChooser.style.display = 'none';
            });
        });
    }

    // Save handler (single binding)
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
        if(selectedAvatar) payload.profile_picture = selectedAvatar;

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

    // Cancel button just reloads /profile to discard unsaved edits
    if(cancelBtn){
        cancelBtn.addEventListener('click', () => {
            window.location.href = '/profile';
        });
    }

    // Logout
    logoutBtn.addEventListener('click', async () => {
        try{
            const r = await fetch('/api/logout', { method: 'POST', credentials: 'include' });
            if(r.ok){
                window.location.href = '/login';
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
