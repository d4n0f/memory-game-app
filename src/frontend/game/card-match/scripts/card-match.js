document.addEventListener("DOMContentLoaded", () => {
    // Color-match képek: előlapok és hátlap
    const cardFrontImages = [
        "../../assets/images/color-match/elulso-kep1.jpg",
        "../../assets/images/color-match/elulso-kep2.jpg",
        "../../assets/images/color-match/elulso-kep3.jpg",
        "../../assets/images/color-match/elulso-kep4.jpg",
        "../../assets/images/color-match/elulso-kep5.jpg",
        "../../assets/images/color-match/elulso-kep6.jpg"
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
    const totalPairs = cardFrontImages.length;

    initGame();

    function initGame() {
        // reset state
        board.innerHTML = "";
        firstCard = null;
        secondCard = null;
        lockBoard = false;
        score = 0;
        moves = 0;
        updateUI();
        resultScreen.classList.add("hidden");

        // párok duplikálása, keverés
        const deck = shuffle([...cardFrontImages, ...cardFrontImages]);

        deck.forEach((src, idx) => {
            const card = createCard(src, idx);
            board.appendChild(card);
        });
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
    }


    nextRoundBtn.addEventListener("click", () => initGame());

    // Menü gomb esemény: vissza a főmenübe
    if (menuBtn) {
        menuBtn.addEventListener("click", () => {
            window.location.href = "../../main/menu/index.html";
        });
    }

    // Fisher–Yates shuffle
    function shuffle(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }

    function createCard(imageSrc, idx) {
        const card = document.createElement("div");
        card.classList.add("card");

        const inner = document.createElement("div");
        inner.classList.add("card-inner");

        // --- Hátlap (mindenkinek ugyanaz, alapból látszik) ---
        const back = document.createElement("div");
        back.classList.add("card-back");
        const backImg = document.createElement("img");
        backImg.src = cardBackImage;
        back.appendChild(backImg);

        // --- Előlap (változó kép, kattintás után látszik) ---
        const front = document.createElement("div");
        front.classList.add("card-front");
        const frontImg = document.createElement("img");
        frontImg.src = imageSrc;
        front.appendChild(frontImg);

        // sorrend: először hátlap, aztán előlap
        inner.appendChild(back);
        inner.appendChild(front);
        card.appendChild(inner);

        card.dataset.image = imageSrc;

        card.addEventListener("click", () => flipCard(card));

        return card;
    }



});
