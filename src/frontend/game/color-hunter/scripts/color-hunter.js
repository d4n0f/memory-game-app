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
const modeSingleBtn = document.getElementById('mode-single');
const modeMultiBtn = document.getElementById('mode-multi');
const modeDesc = document.getElementById('mode-desc');
const startSingleBtn = document.getElementById('start-single');

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

// Mode selection handlers
function setModeSingle() {
    multiplayerMode = false;
    if (modeSingleBtn) modeSingleBtn.classList.add('active');
    if (modeMultiBtn) modeMultiBtn.classList.remove('active');
    if (modeDesc) modeDesc.textContent = 'Gyakorló mód: gyakorolj magadban, játssz több kört egymás után, nincs szobagenerálás.';
    if (modeDesc2) modeDesc2.textContent = '';
    // hide multiplayer controls
    if (generateBtn) generateBtn.classList.add('hidden');
    if (joinInput) joinInput.classList.add('hidden');
    if (codeDisplay) codeDisplay.classList.add('hidden');
    const joinLabel = document.querySelector('label[for="join-code"]');
    if (joinLabel) joinLabel.classList.add('hidden');
    if (joinBtn) joinBtn.classList.add('hidden');
    if (startSingleBtn) startSingleBtn.classList.remove('hidden');
    if (playersRow) playersRow.classList.add('hidden');
}

const modeDesc2 = document.getElementById('mode-desc2');

function setModeMulti() {
    multiplayerMode = true;
    if (modeMultiBtn) modeMultiBtn.classList.add('active');
    if (modeSingleBtn) modeSingleBtn.classList.remove('active');
    if (modeDesc) modeDesc.textContent = 'Párbaj mód: Hozz létre saját játékszobát, vagy add meg a belépési kódot és párbajozz barátaid ellen!';
    if (modeDesc2) modeDesc2.textContent = 'Fontos: Párbaj módban fix 5 mp-ed lesz a kép megtekintésére. Siess és válaszolj gyorsabban, mint barátaid, hogy TE kapd a legtöbb pontot!';
    // show multiplayer controls
    if (generateBtn) generateBtn.classList.remove('hidden');
    if (joinInput) joinInput.classList.remove('hidden');
    if (codeDisplay) codeDisplay.classList.remove('hidden');
    const joinLabel = document.querySelector('label[for="join-code"]');
    if (joinLabel) joinLabel.classList.remove('hidden');
    if (joinBtn) joinBtn.classList.remove('hidden');
    if (startSingleBtn) startSingleBtn.classList.add('hidden');
    // playersRow will be managed by socket events
}

if (modeSingleBtn) modeSingleBtn.addEventListener('click', setModeSingle);
if (modeMultiBtn) modeMultiBtn.addEventListener('click', setModeMulti);

// Initialize mode according to the HTML default (fallback to multiplayer)
if (modeMultiBtn && modeMultiBtn.classList.contains('active')) {
    setModeMulti();
} else if (modeSingleBtn && modeSingleBtn.classList.contains('active')) {
    setModeSingle();
} else {
    // default to multiplayer
    setModeMulti();
}

async function createRoomOnServer() {
    // call backend to create room (requires logged in user/session)
    try {
        const playerId = parseInt(localStorage.getItem('player_id'), 10);
        if (!playerId) {
            alert('Be kell jelentkezned a játékhoz');
            return;
        }
        
        // JAVÍTÁS: player_id küldése a request body-ban
        const res = await api.postJSON('/api/multiplayer/create-room', {
            player_id: playerId
        });
        if (!res.ok) {
            alert(res.json && res.json.error ? res.json.error : 'Szoba létrehozása sikertelen');
            return;
        }
        roomCode = res.json.room_code;
        if (codeDisplay) codeDisplay.textContent = roomCode;
        isHost = true;
        // JAVÍTÁS: host_id tárolása, hogy később ellenőrizni lehessen
        if (res.json.host_id) {
            localStorage.setItem(`room_${roomCode}_host_id`, res.json.host_id.toString());
        }
        // auto-join via websocket
        await joinRoom(roomCode);
    } catch (err) {
        console.error('createRoom error', err);
        alert('Hiba a szoba létrehozásakor');
    }
}

async function joinRoomAPI(room) {
    try {
        const playerId = parseInt(localStorage.getItem('player_id'), 10);
        if (!playerId) {
            alert('Be kell jelentkezned a játékhoz');
            return false;
        }
        
        // JAVÍTÁS: player_id küldése a request body-ban
        const res = await api.postJSON(`/api/multiplayer/join-room/${room}`, {
            player_id: playerId
        });
        if (!res.ok) {
            alert(res.json && res.json.error ? res.json.error : 'Szobához csatlakozás sikertelen');
            return false;
        }
        isHost = !!res.json.is_host;
        // JAVÍTÁS: host_id tárolása
        if (res.json.host_id) {
            localStorage.setItem(`room_${room}_host_id`, res.json.host_id.toString());
        }
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
        isHost = !!data.is_host; // FRISSÍTÉS!
        // JAVÍTÁS: host_id tárolása, ha van
        if (data.host_id && roomCode) {
            localStorage.setItem(`room_${roomCode}_host_id`, data.host_id.toString());
        }
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
        // JAVÍTÁS: currentRoundNumber frissítése a szerver által küldött round_number alapján
        if (data.round_number !== undefined) {
            currentRoundNumber = data.round_number;
        }
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
        // JAVÍTÁS: currentRoundNumber frissítése a szerver által küldött round_number alapján
        if (data.round_number !== undefined) {
            currentRoundNumber = data.round_number;
        }
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
        // JAVÍTÁS: currentRoundNumber frissítése a szerver által küldött round_number alapján
        if (data.round_number !== undefined) {
            currentRoundNumber = data.round_number;
        }
        let msg = 'Játék vége\nRanglista:\n' + lb.map((p, i) => `${i+1}. ${p.name} (${p.score})`).join('\n');
        resultMessage.textContent = msg;
        resultScreen.classList.remove('hidden');
        
        // JAVÍTÁS: Végső eredmény mentése a scores táblába
        const playerId = parseInt(localStorage.getItem('player_id'), 10);
        console.log('game_end - playerId:', playerId, 'leaderboard:', lb, 'currentRoundNumber:', currentRoundNumber, 'data.round_number:', data.round_number);
        
        if (playerId) {
            // Keresd meg a játékos pozícióját és pontszámát a ranglistán
            // JAVÍTÁS: Típus-egyeztetés biztosítása (mindkét oldalt számként kezeljük)
            const myPlayer = lb.find(p => {
                const pid = parseInt(p.player_id || p.playerId || 0, 10);
                return pid === playerId;
            });
            
            console.log('game_end - myPlayer found:', myPlayer);
            
            if (myPlayer) {
                // JAVÍTÁS: Mentsük az eredményt akkor is, ha a score 0 (a játékos részt vett)
                const scoreToSave = myPlayer.score || 0;
                const roundsToSave = currentRoundNumber || 1;
                
                console.log('game_end - Saving score:', {
                    player_id: playerId,
                    score: scoreToSave,
                    game_mode: 'color-hunter-multiplayer',
                    rounds_played: roundsToSave,
                    difficulty: 'multiplayer'
                });
                
                (async () => {
                    try {
                        const res = await api.postJSON('/api/save', {
                            player_id: playerId,
                            score: scoreToSave,
                            game_mode: 'color-hunter-multiplayer',
                            rounds_played: roundsToSave,
                            difficulty: 'multiplayer'
                        });
                        if (!res.ok) {
                            console.error('Score mentés sikertelen:', res.json?.error || res.text);
                            console.error('Response status:', res.status);
                        } else {
                            console.log('Score sikeresen mentve:', scoreToSave, 'rounds:', roundsToSave);
                        }
                    } catch (err) {
                        console.error('Save score error', err);
                    }
                })();
            } else {
                console.warn('game_end - Játékos nem található a leaderboardban. playerId:', playerId, 'leaderboard player_ids:', lb.map(p => p.player_id || p.playerId));
            }
        } else {
            console.warn('game_end - Nincs player_id a localStorage-ban');
        }
    });

    socket.on('error', (err) => {
        console.error('socket error', err);
        const message = err.message || err.error || 'Ismeretlen hiba történt';
        alert(message);
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
    const playerId = parseInt(localStorage.getItem('player_id'), 10);
    if (!playerId) { alert('Be kell jelentkezned'); return; }
    if (!socket) { alert('Nincs socket kapcsolat'); return; }
    if (!roomCode) { alert('Nincs szoba kód'); return; }
    
    // JAVÍTÁS: Ellenőrizzük, hogy a jelenlegi player_id megegyezik-e a host_id-val
    const storedHostId = localStorage.getItem(`room_${roomCode}_host_id`);
    if (storedHostId && parseInt(storedHostId, 10) !== playerId) {
        alert('Csak a host indíthatja a játékot!');
        console.warn(`Player ID mismatch: current=${playerId}, host=${storedHostId}`);
        return;
    }
    
    socket.emit('start_game', { room_code: roomCode, player_id: playerId });
});

// Start singleplayer: start local rounds repeatedly
if (startSingleBtn) startSingleBtn.addEventListener('click', () => {
    // ensure singleplayer mode
    setModeSingle();
    // hide lobby and show game board
    try { hideLobby(); } catch (e) {}
    if (gameBoard) gameBoard.classList.remove('hidden');
    // initialize score and round counter
    score = 0;
    currentRoundNumber = 0;
    // start first round
    startRound();
});

showLobby();

function startRound() {
    document.getElementById("target-container").classList.remove("hidden");
    choicesContainer.classList.add("hidden");
    resultScreen.classList.add("hidden");

    currentRoundNumber = (currentRoundNumber || 0) + 1;
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
    // Build choices ensuring uniqueness: include currentTarget plus 3 distinct other images
    const others = images.filter(img => img !== currentTarget);
    // Shuffle others
    for (let i = others.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [others[i], others[j]] = [others[j], others[i]];
    }
    const take = Math.min(3, others.length);
    const options = [currentTarget, ...others.slice(0, take)];

    // If not enough distinct images available (edge case), fill with currentTarget only once
    // and avoid duplicates in options
    const uniqueOptions = [];
    const seen = new Set();
    for (const o of options) {
        if (!seen.has(o)) {
            uniqueOptions.push(o);
            seen.add(o);
        }
    }

    // Shuffle final options
    for (let i = uniqueOptions.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [uniqueOptions[i], uniqueOptions[j]] = [uniqueOptions[j], uniqueOptions[i]];
    }

    choicesGrid.innerHTML = "";
    uniqueOptions.forEach(img => {
        const el = document.createElement("img");
        el.src = img;
        el.addEventListener("click", () => checkChoice(img));
        choicesGrid.appendChild(el);
    });
}

function checkChoice(choice) {
    choicesContainer.classList.add("hidden");
    resultScreen.classList.remove("hidden");

    const correct = (choice === currentTarget);

    if (multiplayerMode) {
        // multiplayer: let server handle results (existing behavior)
        if (correct) {
            score++;
            window.location.href = '/color-hunter/correct-answer';
            return;
        } else {
            window.location.href = '/color-hunter/wrong-answer';
            return;
        }
    }

    // Singleplayer: show in-page result and allow next rounds
    if (correct) {
        score++;
        resultMessage.textContent = `Helyes! Pontszám: ${score}`;
    } else {
        resultMessage.textContent = `Helytelen. Pontszám: ${score}`;
    }

    // Optionally save score for singleplayer
    const playerId = localStorage.getItem('player_id');
    const difficulty = localStorage.getItem('difficulty') || 'easy';
    if (playerId) {
        (async () => {
            try {
                await api.postJSON('/api/save', {
                    player_id: parseInt(playerId, 10),
                    score: score,
                    game_mode: 'color-hunter',
                    rounds_played: currentRoundNumber,
                    difficulty: difficulty
                });
            } catch (err) {
                console.error('Save score error', err);
            }
        })();
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