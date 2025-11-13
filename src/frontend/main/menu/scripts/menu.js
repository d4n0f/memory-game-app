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
    const scoreboardBody = document.querySelector('#scoreboard-table tbody');
    if (scoreboardBody) {
        (async () => {
            try {
                const result = await api.getJSON('/api/scores?limit=5');
                scoreboardBody.innerHTML = '';
                const data = result.json;
                if (result.ok && data && Array.isArray(data.scores)) {
                    data.scores.forEach(score => {
                        const row = document.createElement('tr');
                        const nameCell = document.createElement('td');
                        const gameCell = document.createElement('td');
                        const scoreCell = document.createElement('td');
                        nameCell.textContent = score.display_name || score.name || '';
                        gameCell.textContent = score.game_mode === 'card-match' ? 'Kártyapárosító' : 'Színvadász';
                        scoreCell.textContent = score.score_val || score.score || score.scoreVal || '';
                        row.appendChild(nameCell);
                        row.appendChild(gameCell);
                        row.appendChild(scoreCell);
                        scoreboardBody.appendChild(row);
                    });
                } else {
                    const row = document.createElement('tr');
                    const cell = document.createElement('td');
                    cell.colSpan = 3;
                    cell.textContent = 'Nincs elérhető eredmény.';
                    row.appendChild(cell);
                    scoreboardBody.appendChild(row);
                }
            } catch (err) {
                scoreboardBody.innerHTML = '';
                const row = document.createElement('tr');
                const cell = document.createElement('td');
                cell.colSpan = 3;
                cell.textContent = 'Nem sikerült betölteni az eredményeket.';
                row.appendChild(cell);
                scoreboardBody.appendChild(row);
            }
        })();
    }
});