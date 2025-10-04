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

    const scores = [
        { game: "Kártyapárosító", score: 120 },
        { game: "Színvadász", score: 95 },
        { game: "Kártyapárosító", score: 80 },
        { game: "Színvadász", score: 70 },
        { game: "Kártyapárosító", score: 65 }
    ];

    const scoreboardBody = document.querySelector('#scoreboard-table tbody');
    if (scoreboardBody) {
        scoreboardBody.innerHTML = '';
        scores.forEach(({ game, score }) => {
            const row = document.createElement('tr');
            const gameCell = document.createElement('td');
            const scoreCell = document.createElement('td');
            gameCell.textContent = game;
            scoreCell.textContent = score;
            row.appendChild(gameCell);
            row.appendChild(scoreCell);
            scoreboardBody.appendChild(row);
        });
    }
});