document.addEventListener("DOMContentLoaded", () => {
    const allCardFrontImages = [
        "../../assets/images/color-match/elulso-kep1.jpg",
        "../../assets/images/color-match/elulso-kep2.jpg",
        "../../assets/images/color-match/elulso-kep3.jpg",
        "../../assets/images/color-match/elulso-kep4.jpg",
        "../../assets/images/color-match/elulso-kep5.jpg",
        "../../assets/images/color-match/elulso-kep6.jpg",
        "../../assets/images/color-match/elulso-kep7.jpg",
        "../../assets/images/color-match/elulso-kep8.jpg"
    ];
    const cardBackImage = "../../assets/images/color-match/hatso-kep.jpg";

    const board = document.getElementById("game-board");
    const scoreEl = document.getElementById("score");
    const movesEl = document.getElementById("moves");
    const resultScreen = document.getElementById("result-screen");
    const resultMessage = document.getElementById("result-message");
    const finalScoreEl = document.getElementById("final-score");
    const nextRoundBtn = document.getElementById("next-round");
    const menuBtn = document.getElementById("menu-btn");

    let firstCard = null;
    let secondCard = null;
    let lockBoard = false;
    let score = 0;
    let moves = 0;

    function getDifficulty() {
        return localStorage.getItem('difficulty') || 'easy';
    }

    let totalPairs = 0;

    initGame();

    function initGame() {
        // reset
        board.innerHTML = "";
        firstCard = null;
        secondCard = null;
        lockBoard = false;
        score = 0;
        moves = 0;
        updateUI();
        resultScreen.classList.add("hidden");

        // Nehézség alapján tábla méret és képek meghatározása
        let difficulty = getDifficulty();
        let pairs = 0;
        let selectedImages = [];
        if (difficulty === 'easy') {
            pairs = 3; // 2x3
            selectedImages = allCardFrontImages.slice(0, 3);
            board.style.gridTemplateColumns = 'repeat(3, 1fr)';
            board.style.gridTemplateRows = 'repeat(2, 1fr)';
        } else if (difficulty === 'medium') {
            pairs = 4; // 2x4
            selectedImages = allCardFrontImages.slice(0, 4);
            board.style.gridTemplateColumns = 'repeat(4, 1fr)';
            board.style.gridTemplateRows = 'repeat(2, 1fr)';
        } else if (difficulty === 'hard') {
            pairs = 6; // 3x4
            selectedImages = allCardFrontImages.slice(0, 6);
            board.style.gridTemplateColumns = 'repeat(4, 1fr)';
            board.style.gridTemplateRows = 'repeat(3, 1fr)';
        } else {
            // alapértelmezett
            pairs = 3;
            selectedImages = allCardFrontImages.slice(0, 3);
            board.style.gridTemplateColumns = 'repeat(3, 1fr)';
            board.style.gridTemplateRows = 'repeat(2, 1fr)';
        }
        totalPairs = pairs;

        // párok előállítása: vagy statikus képekből, vagy fraktál-módban generált képek
        if (isFractalMode()) {
            // generate fractal pairs (each pair has same id but slightly different visualizations)
            const size = getCardImageSize();
            // generatePairs returns an array of {src, id} entries (2 per pair)
            const fractalEntries = generateFractalPairs(pairs, size.width, size.height);
            const deck = shuffle(fractalEntries);
            deck.forEach((entry, idx) => {
                const card = createCard(entry.src, entry.id);
                board.appendChild(card);
            });
        } else {
            // párok duplikálása, keverés
            const deck = shuffle([...selectedImages, ...selectedImages]);

            deck.forEach((src, idx) => {
                const card = createCard(src, idx);
                board.appendChild(card);
            });
        }
    }


    function flipCard(card) {
        if (lockBoard) return;
        if (card === firstCard) return;
        if (card.classList.contains("matched")) return;

        card.classList.add("flipped");

        if (!firstCard) {
            firstCard = card;
            return;
        }

        secondCard = card;
        moves++;
        updateUI();

        lockBoard = true;
        setTimeout(checkForMatch, 700); // animáció miatt kis késleltetés
    }

    function checkForMatch() {
        const isMatch = firstCard.dataset.image === secondCard.dataset.image;

        if (isMatch) {
            firstCard.classList.add("matched");
            secondCard.classList.add("matched");
            score++;
            updateUI();
            resetSelection();
            lockBoard = false;
            if (score === totalPairs) {
                endGame();
            }
        } else {
            setTimeout(() => {
                firstCard.classList.remove("flipped");
                secondCard.classList.remove("flipped");
                resetSelection();
                lockBoard = false;
            }, 800);
        }
    }

    function resetSelection() {
        firstCard = null;
        secondCard = null;
    }

    function updateUI() {
        scoreEl.textContent = score;
        movesEl.textContent = moves;
    }

    function endGame() {
        finalScoreEl.textContent = score;
        resultMessage.textContent = `Megtaláltad az összes párt ${moves} lépésből!`;
        resultScreen.classList.remove("hidden");

        // Eredmény mentése backendre
        const playerId = localStorage.getItem('player_id');
        const difficulty = localStorage.getItem('difficulty') || 'easy';
        if (playerId) {
            (async () => {
                try {
                    const res = await api.postJSON('/api/save', {
                        player_id: playerId,
                        score: score,
                        game_mode: 'card-match',
                        //game_time: 0,
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


    nextRoundBtn.addEventListener("click", () => initGame());

    // Menü gomb esemény: vissza a főmenübe
    if (menuBtn) {
        menuBtn.addEventListener("click", () => {
            window.location.href = "/menu";
        });
    }

    function shuffle(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }

    function createCard(imageSrc, idxOrId) {
        const card = document.createElement("div");
        card.classList.add("card");

        const inner = document.createElement("div");
        inner.classList.add("card-inner");

        // Hátlap
        const back = document.createElement("div");
        back.classList.add("card-back");
        const backImg = document.createElement("img");
        backImg.src = cardBackImage;
        back.appendChild(backImg);

        // Előlap 
        const front = document.createElement("div");
        front.classList.add("card-front");
    const frontImg = document.createElement("img");
    frontImg.src = imageSrc;
    front.appendChild(frontImg);

        // sorrend: először hátlap, aztán előlap
        inner.appendChild(back);
        inner.appendChild(front);
        card.appendChild(inner);

    // For matching, store an id for the pair. If idxOrId is a number (old behavior), use the imageSrc
    // Otherwise use the provided id (string) so pairs can be similar but still match by id.
    card.dataset.image = (typeof idxOrId === 'number') ? imageSrc : String(idxOrId);

        card.addEventListener("click", () => flipCard(card));

        return card;
    }

    function getCardImageSize() {
        // choose a reasonable canvas size based on difficulty/grid
        // small canvases are fine for mobile and speed
        const diff = getDifficulty();
        if (diff === 'hard') return { width: 220, height: 160 };
        if (diff === 'medium') return { width: 200, height: 140 };
        return { width: 180, height: 120 };
    }

    function isFractalMode() {
        // check URL query or localStorage for selected game_mode
        try {
            const params = new URLSearchParams(window.location.search);
            if (params.get('mode') === 'fractal') return true;
        } catch (e) {}
        return localStorage.getItem('game_mode') === 'fractal';
    }

    // Generate N pairs of visually similar fractal images.
    // Returns array of length 2*pairs: [{src, id}, ...]
    function generateFractalPairs(pairsCount, width, height) {
        const entries = [];
        // we'll use a simple Julia set renderer with different parameters per pair
        for (let i = 0; i < pairsCount; i++) {
            const pairId = `fractal-${Date.now()}-${i}-${Math.floor(Math.random()*10000)}`;
            // base complex parameter for this pair
            const cre = (Math.random() * 2 - 1) * 0.8; // -0.8..0.8
            const cim = (Math.random() * 2 - 1) * 0.8;
            const base = { cre, cim };
            // create two similar but not identical variants by varying color offset / zoom
            const variantA = generateJuliaDataURL(base.cre, base.cim, width, height, { colorOffset: Math.random()*360, zoom: 1 + Math.random()*0.6 });
            const variantB = generateJuliaDataURL(base.cre + (Math.random()-0.5)*0.02, base.cim + (Math.random()-0.5)*0.02, width, height, { colorOffset: Math.random()*360, zoom: 1 + Math.random()*0.6 });
            entries.push({ src: variantA, id: pairId });
            entries.push({ src: variantB, id: pairId });
        }
        return entries;
    }

    // Simple Julia set renderer to a data URL. Fast and small resolution.
    function generateJuliaDataURL(cre, cim, width, height, opts = {}) {
        const maxIter = opts.maxIter || 80;
        const zoom = opts.zoom || 1.0;
        const colorOffset = opts.colorOffset || 0;

        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        const img = ctx.createImageData(width, height);
        // bounds in complex plane
        const xmin = -1.5/zoom;
        const xmax = 1.5/zoom;
        const ymin = -1.0/zoom;
        const ymax = 1.0/zoom;

        let p = 0;
        for (let y = 0; y < height; y++) {
            const zy0 = ymin + (y / (height - 1)) * (ymax - ymin);
            for (let x = 0; x < width; x++) {
                const zx0 = xmin + (x / (width - 1)) * (xmax - xmin);
                let zx = zx0;
                let zy = zy0;
                let iter = 0;
                while (zx*zx + zy*zy < 4 && iter < maxIter) {
                    const xt = zx*zx - zy*zy + cre;
                    zy = 2*zx*zy + cim;
                    zx = xt;
                    iter++;
                }
                // color mapping
                const t = iter / maxIter;
                const hue = (colorOffset + t * 360) % 360;
                const [r,g,b] = hslToRgb(hue/360, 0.6, 0.5 + 0.2 * (1 - t));
                img.data[p++] = Math.floor(r*255);
                img.data[p++] = Math.floor(g*255);
                img.data[p++] = Math.floor(b*255);
                img.data[p++] = 255;
            }
        }
        ctx.putImageData(img, 0, 0);
        return canvas.toDataURL('image/png');
    }

    // HSL to RGB helper (h in [0,1], s,l in [0,1]) -> [r,g,b] 0..1
    function hslToRgb(h, s, l){
        let r, g, b;
        if (s === 0) {
            r = g = b = l; // achromatic
        } else {
            const hue2rgb = function(p, q, t){
                if(t < 0) t += 1;
                if(t > 1) t -= 1;
                if(t < 1/6) return p + (q - p) * 6 * t;
                if(t < 1/2) return q;
                if(t < 2/3) return p + (q - p) * (2/3 - t) * 6;
                return p;
            };
            const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
            const p = 2 * l - q;
            r = hue2rgb(p, q, h + 1/3);
            g = hue2rgb(p, q, h);
            b = hue2rgb(p, q, h - 1/3);
        }
        return [r,g,b];
    }



});
