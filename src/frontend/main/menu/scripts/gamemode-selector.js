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
            if (selectedMode === "color-hunter") {
                window.location.href = `../../game/color-hunter/color-hunter.html?difficulty=${selectedDifficulty}`;
            } else if (selectedMode === "card-match") {
                window.location.href = `../../game/card-match/card-match.html?difficulty=${selectedDifficulty}`;
            }
        });
    }
});