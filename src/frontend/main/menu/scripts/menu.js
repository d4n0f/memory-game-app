document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("player-form");

    form.addEventListener("submit", (event) => {
        event.preventDefault();
        const playerName = document.getElementById("player-name").value.trim();

        if (playerName) {
            localStorage.setItem('player_name', playerName);
            window.location.href = "/menu";
        } else {
            alert("Kérlek, add meg a neved!");
        }
    });
});