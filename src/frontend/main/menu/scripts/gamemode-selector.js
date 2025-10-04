document.addEventListener("DOMContentLoaded", () => {
    let selectedDifficulty = null;
    let selectedMode = null;

    const difficultyButtons = document.querySelectorAll(".difficulty-btn");
    const modeButtons = document.querySelectorAll(".mode-btn");
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

    modeButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            modeButtons.forEach(b => b.classList.remove("selected"));
            btn.classList.add("selected");
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
            fetch('/api/game', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: playerName })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success && data.player_id) {
                    localStorage.setItem('player_id', data.player_id);
                    // Továbbirányítás a választott játékra
                    if (selectedMode === "color-hunter") {
                        window.location.href = "/color-hunter";
                    } else if (selectedMode === "card-match") {
                        window.location.href = "/card-match";
                    }
                } else {
                    alert('Nem sikerült elindítani a játékot: ' + (data.error || 'Ismeretlen hiba'));
                }
            })
            .catch(() => {
                alert('Nem sikerült csatlakozni a szerverhez.');
            });
        });
    }
});