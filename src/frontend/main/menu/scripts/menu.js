document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("player-form");
    const playerSetup = document.getElementById("player-setup");
    const modeSelector = document.getElementById("mode-selector");

    form.addEventListener("submit", (event) => {
        event.preventDefault();
        const playerName = document.getElementById("player-name").value.trim();

        if (playerName) {
            playerSetup.classList.add("hidden");
            modeSelector.classList.remove("hidden");
        } else {
            alert("Kérlek, add meg a neved!");
        }
    });

    const modeButtons = document.querySelectorAll(".mode-btn");
    modeButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const mode = btn.dataset.mode;
            if (mode === "color-hunter") {
                window.location.href = "../../game/color-hunter/color-hunter.html";
            } else if (mode === "card-match") {
                window.location.href = "../../game/card-match/card-match.html";
            }
        });
    });
});