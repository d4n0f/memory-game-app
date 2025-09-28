document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("player-form");
    const playerSetup = document.getElementById("player-setup");
    const modeSelector = document.getElementById("mode-selector");

    form.addEventListener("submit", (event) => {
        event.preventDefault();
        const playerName = document.getElementById("player-name").value.trim();

        if (playerName) {
            localStorage.setItem('player_name', playerName);
            window.location.href = "gamemode-selector.html";
        } else {
            alert("Kérlek, add meg a neved!");
        }
    });
});