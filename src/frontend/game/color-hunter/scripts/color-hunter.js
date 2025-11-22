const images = [
    "../../assets/images/color-hunter/kep1.jpg",
    "../../assets/images/color-hunter/kep2.jpg",
    "../../assets/images/color-hunter/kep3.jpg",
    "../../assets/images/color-hunter/kep4.jpg",
    "../../assets/images/color-hunter/kep5.jpg",
    "../../assets/images/color-hunter/kep6.jpg",
    "../../assets/images/color-hunter/kep7.jpg",
    "../../assets/images/color-hunter/kep8.jpg",
    "../../assets/images/color-hunter/kep9.jpg",
    "../../assets/images/color-hunter/kep10.jpg",
    "../../assets/images/color-hunter/kep11.jpg",
    "../../assets/images/color-hunter/kep12.jpg",
    "../../assets/images/color-hunter/kep13.jpg",
    "../../assets/images/color-hunter/kep14.jpg"
];

const gameBoard = document.getElementById("game-board");
const targetImage = document.getElementById("target-image");
const timerElement = document.getElementById("timer");
const choicesContainer = document.getElementById("choices-container");
const choicesGrid = document.getElementById("choices-grid");
const resultScreen = document.getElementById("result-screen");
const resultMessage = document.getElementById("result-message");
const nextRoundBtn = document.getElementById("next-round");
const menuBtn = document.getElementById("menu-btn");

let timer;
let score = 0;
let currentTarget = "";

function getDifficulty() {
    // Alapértelmezett nehézség: könnyű
    return localStorage.getItem('difficulty') || 'easy';
}

// Show lobby first; wait for user to create or enter a room code
const lobby = document.getElementById('lobby');
const generateBtn = document.getElementById('generate-code');
const codeDisplay = document.getElementById('code-display');
const joinInput = document.getElementById('join-code');
const joinBtn = document.getElementById('join-btn');

let roomCode = '';
let socket = null;
let isHost = false;
let players = [];
let multiplayerMode = false;
let optionsForRound = [];
let currentRoundNumber = 0;
const playersRow = document.getElementById('players-row');
const playersListEl = document.getElementById('players-list');
const startGameBtn = document.getElementById('start-game');

function showLobby() {
    if (lobby) lobby.classList.remove('hidden');
    if (choicesContainer) choicesContainer.classList.add('hidden');
    if (resultScreen) resultScreen.classList.add('hidden');
    if (gameBoard) gameBoard.classList.add('hidden');
}

function hideLobby() {
    if (lobby) lobby.classList.add('hidden');
    if (gameBoard) gameBoard.classList.remove('hidden');
}

function generateCode() {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    let s = '';
    for (let i = 0; i < 5; i++) s += chars.charAt(Math.floor(Math.random() * chars.length));
    roomCode = s;
    if (codeDisplay) codeDisplay.textContent = roomCode;
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(roomCode).catch(() => {});
    }
}

if (generateBtn) generateBtn.addEventListener('click', generateCode);

async function createRoomOnServer() {
    // call backend to create room (requires logged in user/session)
    try {
        const res = await api.postJSON('/api/multiplayer/create-room', {});
        if (!res.ok) {
            alert(res.json && res.json.error ? res.json.error : 'Szoba létrehozása sikertelen');
            return;
        }
        roomCode = res.json.room_code;
        if (codeDisplay) codeDisplay.textContent = roomCode;
        isHost = true;
        // auto-join via websocket
        await joinRoom(roomCode);
    } catch (err) {
        console.error('createRoom error', err);
        alert('Hiba a szoba létrehozásakor');
    }
}

async function joinRoomAPI(room) {
    try {
        const res = await api.postJSON(`/api/multiplayer/join-room/${room}`, {});
        if (!res.ok) {
            alert(res.json && res.json.error ? res.json.error : 'Szobához csatlakozás sikertelen');
            return false;
        }
        isHost = !!res.json.is_host;
        return true;
    } catch (err) {
        console.error('joinRoomAPI error', err);
        alert('Hiba a szobához való csatlakozáskor');
        return false;
    }
}

function connectSocketIfNeeded() {
    if (socket) return socket;
    if (typeof io === 'undefined') {
        console.warn('Socket.IO client not available');
        return null;
    }
    socket = io();

    socket.on('connect', () => {
        console.log('connected to socket', socket.id);
    });

    socket.on('room_joined', (data) => {
        console.log('room_joined', data);
        players = data.players || [];
        currentRoundNumber = data.current_round || 0;
        updatePlayersUI();
        if (playersRow) playersRow.classList.remove('hidden');
        if (isHost && startGameBtn) startGameBtn.classList.remove('hidden');
    });

    socket.on('player_joined', (data) => {
        console.log('player_joined', data);
        players = data.players || players;
        updatePlayersUI();
    });

    socket.on('player_left', (data) => {
        console.log('player_left', data);
        // refresh room info from server could be implemented; for now update list
        if (data && data.player_id) {
            players = players.filter(p => p.player_id !== data.player_id);
            updatePlayersUI();
        }
    });

    socket.on('round_start', (data) => {
        console.log('round_start', data);
        multiplayerMode = true;
        currentTarget = data.target_image;
        optionsForRound = data.options || [];
        // Hide the lobby and ensure the game board is visible so images render
        try { hideLobby(); } catch (e) { /* ignore */ }
        if (gameBoard) gameBoard.classList.remove('hidden');
        document.getElementById('target-container').classList.remove('hidden');
        choicesContainer.classList.add('hidden');
        resultScreen.classList.add('hidden');

        // display timer countdown
        let viewTime = data.view_time || 5;
        timerElement.textContent = `Hátralévő idő: ${viewTime} mp`;
        clearInterval(timer);
        timer = setInterval(() => {
            viewTime--;
            timerElement.textContent = `Hátralévő idő: ${viewTime} mp`;
            if (viewTime <= 0) {
                clearInterval(timer);
            }
        }, 1000);

        if (targetImage) targetImage.src = currentTarget;
    });

    socket.on('show_choices', (data) => {
        console.log('show_choices', data);
        // show the choices prepared in round_start
        document.getElementById('target-container').classList.add('hidden');
        choicesContainer.classList.remove('hidden');
        choicesGrid.innerHTML = '';
        optionsForRound.forEach(img => {
            const el = document.createElement('img');
            el.src = img;
            el.addEventListener('click', () => {
                // emit answer
                const playerId = localStorage.getItem('player_id');
                if (!playerId) { alert('Be kell jelentkezned a játékhoz'); return; }
                socket.emit('player_answer', { room_code: roomCode, player_id: playerId, choice: img });
                // hide choices while waiting
                choicesContainer.classList.add('hidden');
            });
            choicesGrid.appendChild(el);
        });
    });

    socket.on('round_end', (data) => {
        console.log('round_end', data);
        // If server sent round_responses, redirect current player to correct/wrong page
        const responses = data.round_responses || null;
        const playerId = (sessionStorage && sessionStorage.getItem('player_id')) || localStorage.getItem('player_id');
        // Prepare a players array to render on the result pages: use leaderboard if available
        const leaderboard = data.leaderboard || [];
        const playersForStorage = leaderboard.map(p => {
            const pid = p.player_id || p.playerId || p.id || p.player_id;
            const resp = responses && responses[pid] ? responses[pid] : null;
            return {
                player_id: pid,
                name: p.name || p.username || p.player_name || 'Név',
                score: p.score || 0,
                correct: resp ? !!resp.correct : null
            };
        });
        try {
            sessionStorage.setItem('color_hunter_last_players', JSON.stringify(playersForStorage));
        } catch (e) { console.warn('Could not save players to sessionStorage', e); }

        if (responses && playerId) {
            const myResp = responses[playerId];
            if (myResp && myResp.correct) {
                window.location.href = '/color-hunter/correct-answer';
                return;
            } else {
                window.location.href = '/color-hunter/wrong-answer';
                return;
            }
        }

        // Fallback: show in-page result if no response info available
        const results = data.results || [];
        let msg = 'Kör vége\n';
        if (results.length) {
            msg += results.map(r => `${r.position}. ${r.player_name} (+${r.points})`).join('\n');
        }
        resultMessage.textContent = msg;
        resultScreen.classList.remove('hidden');
    });

    socket.on('game_end', (data) => {
        console.log('game_end', data);
        const lb = data.leaderboard || [];
        let msg = 'Játék vége\nRanglista:\n' + lb.map((p, i) => `${i+1}. ${p.name} (${p.score})`).join('\n');
        resultMessage.textContent = msg;
        resultScreen.classList.remove('hidden');
    });

    socket.on('error', (err) => {
        console.error('socket error', err);
    });

    return socket;
}

function updatePlayersUI() {
    if (!playersListEl) return;
    playersListEl.innerHTML = '';
    players.forEach(p => {
        const el = document.createElement('div');
        el.className = 'player-item';
        el.textContent = p.name + (p.is_host ? ' (Host)' : '');
        playersListEl.appendChild(el);
    });
}

async function joinRoom(room) {
    const ok = await joinRoomAPI(room);
    if (!ok) return;
    // connect socket and emit join_room
    const s = connectSocketIfNeeded();
    if (!s) return;
    const playerId = localStorage.getItem('player_id');
    if (!playerId) { alert('Be kell jelentkezned a játékhoz'); return; }
    roomCode = room;
    s.emit('join_room', { room_code: roomCode, player_id: playerId });
    // Do NOT hide the whole lobby (players list lives inside it).
    // Instead hide the join/create controls and reveal the players section.
    try {
        // Hide the create/join controls but KEEP the code display visible
        if (generateBtn) generateBtn.classList.add('hidden');
        if (joinInput) joinInput.classList.add('hidden');
        const joinLabel = document.querySelector('label[for="join-code"]');
        if (joinLabel) joinLabel.classList.add('hidden');
        if (joinBtn) joinBtn.classList.add('hidden');
        // Ensure the generated code remains visible for the host
        if (codeDisplay) codeDisplay.classList.remove('hidden');
    } catch (e) {
        console.warn('Could not hide join controls', e);
    }
    if (lobby) lobby.classList.remove('hidden');
    if (playersRow) playersRow.classList.remove('hidden');
}

// event listeners for create/join/start
if (generateBtn) generateBtn.addEventListener('click', createRoomOnServer);
if (joinBtn) joinBtn.addEventListener('click', async () => {
    const val = (joinInput && joinInput.value.trim()) || (codeDisplay && codeDisplay.textContent.trim());
    if (!val) { alert('Adj meg egy kódot.'); return; }
    await joinRoom(val);
});

if (startGameBtn) startGameBtn.addEventListener('click', () => {
    const playerId = localStorage.getItem('player_id');
    if (!playerId) { alert('Be kell jelentkezned'); return; }
    if (!socket) { alert('Nincs socket kapcsolat'); return; }
    socket.emit('start_game', { room_code: roomCode, player_id: playerId });
});

showLobby();

function startRound() {
    document.getElementById("target-container").classList.remove("hidden");
    choicesContainer.classList.add("hidden");
    resultScreen.classList.add("hidden");

    currentTarget = images[Math.floor(Math.random() * images.length)];
    targetImage.src = currentTarget;

    let difficulty = getDifficulty();
    let timeLeft = 5;
    if (difficulty === 'easy') {
        timeLeft = 10;
    } else if (difficulty === 'medium') {
        timeLeft = 5;
    } else if (difficulty === 'hard') {
        timeLeft = 3;
    }
    timerElement.textContent = `Hátralévő idő: ${timeLeft} mp`;

    clearInterval(timer);
    timer = setInterval(() => {
        timeLeft--;
        timerElement.textContent = `Hátralévő idő: ${timeLeft} mp`;

        if (timeLeft <= 0) {
            clearInterval(timer);
            showChoices();
        }
    }, 1000);
}

function showChoices() {
    document.getElementById("target-container").classList.add("hidden");
    choicesContainer.classList.remove("hidden");

    const shuffled = [...images].sort(() => 0.5 - Math.random());
    const options = [currentTarget, ...shuffled.slice(0, 3)];
    const finalOptions = options.sort(() => 0.5 - Math.random());

    choicesGrid.innerHTML = "";
    finalOptions.forEach(img => {
        const el = document.createElement("img");
        el.src = img;
        el.addEventListener("click", () => checkChoice(img));
        choicesGrid.appendChild(el);
    });
}

function checkChoice(choice) {
    choicesContainer.classList.add("hidden");
    resultScreen.classList.remove("hidden");

    let correct = false;
    if (choice === currentTarget) {
        score++;
        correct = true;
        // redirect to server route for correct answer
        window.location.href = '/color-hunter/correct-answer';
        return;
    } else {
        // redirect to server route for wrong answer
        window.location.href = '/color-hunter/wrong-answer';
        return;
    }

    if (correct) {
        const playerId = localStorage.getItem('player_id');
        const difficulty = localStorage.getItem('difficulty') || 'easy';
        if (playerId) {
                (async () => {
                    try {
                        const res = await api.postJSON('/api/save', {
                            player_id: playerId,
                            score: score,
                            game_mode: 'color-hunter',
                            rounds_played: 1,
                            difficulty: difficulty
                        });
                        // optional: check res.ok/res.json for errors
                    } catch (err) {
                        console.error('Save score error', err);
                    }
                })();
        }
    }
}

nextRoundBtn.addEventListener("click", () => {
    resultScreen.classList.add("hidden");
    document.getElementById("target-container").classList.remove("hidden");
    startRound();
});

if (menuBtn) {
    menuBtn.addEventListener("click", () => {
        window.location.href = "/menu";
    });
}