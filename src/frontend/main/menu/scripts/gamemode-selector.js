document.addEventListener("DOMContentLoaded", () => {
    let selectedDifficulty = null;
    let selectedMode = null;

    const difficultyButtons = document.querySelectorAll(".difficulty-btn");

    const modeRow = document.querySelector('.mode-row');
    let modeButtons = document.querySelectorAll(".mode-btn");
    const startGameBtn = document.querySelector(".start-game-btn");

    function updateStartButtonState() {
        if (selectedDifficulty && selectedMode) {
            startGameBtn.disabled = false;
            startGameBtn.classList.remove("disabled");
        } else {
            startGameBtn.disabled = true;
            startGameBtn.classList.add("disabled");
        }
    }

    difficultyButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            difficultyButtons.forEach(b => b.classList.remove("selected"));
            btn.classList.add("selected");
            selectedDifficulty = btn.dataset.difficulty;
            updateStartButtonState();
        });
    });

    // If mode buttons are not present in the DOM, generate them here.
    const availableModes = [
        { id: 'color-hunter', label: 'Színvadász', img: '../../assets/images/nyuszi.png' },
        { id: 'card-match', label: 'Kártyapárosító', img: '../../assets/images/kartyak.png' }
    ];

    if (modeRow && modeRow.children.length === 0) {
        availableModes.forEach(m => {
            const btn = document.createElement('button');
            btn.className = 'mode-btn';
            btn.dataset.mode = m.id;
            btn.setAttribute('data-cy', 'mode-item');
            btn.setAttribute('type', 'button');

            const img = document.createElement('img');
            img.src = m.img;
            img.alt = m.label;
            btn.appendChild(img);

            const span = document.createElement('span');
            span.className = 'mode-label';
            span.textContent = m.label;
            btn.appendChild(span);

            modeRow.appendChild(btn);
        });
        // refresh modeButtons NodeList after generation
        modeButtons = document.querySelectorAll('.mode-btn');
    }

    modeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            modeButtons.forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            selectedMode = btn.dataset.mode;
            updateStartButtonState();
        });
    });

    if (startGameBtn) {
        startGameBtn.disabled = true;
        startGameBtn.classList.add("disabled");
        startGameBtn.addEventListener("click", () => {
            if (selectedDifficulty) {
                localStorage.setItem('difficulty', selectedDifficulty);
            }
            // Játékos név lekérése a localStorage-ből (amit a főmenüben ad meg)
            const playerName = localStorage.getItem('player_name') || '';
            if (!playerName) {
                alert('Név nincs megadva!');
                return;
            }
            // Játék indítása a backenddel
            (async () => {
                try {
                    const result = await api.postJSON('/api/game', { name: playerName });
                    if (result.ok && result.json && result.json.player_id) {
                        localStorage.setItem('player_id', result.json.player_id);
                        if (selectedMode === "color-hunter") {
                            window.location.href = "/color-hunter";
                        } else if (selectedMode === "card-match") {
                            window.location.href = "/card-match";
                        }
                    } else {
                        const msg = (result.json && result.json.error) ? result.json.error : (result.text || 'Ismeretlen hiba');
                        alert('Nem sikerült elindítani a játékot: ' + msg);
                    }
                } catch (err) {
                    console.error('Start game error', err);
                    alert('Nem sikerült csatlakozni a szerverhez.');
                }
            })();
        });
    }
});