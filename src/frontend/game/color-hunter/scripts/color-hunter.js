const images = [
    "../../assets/images/kep1.jpg",
    "../../assets/images/kep2.jpg",
    "../../assets/images/kep3.jpg",
    "../../assets/images/kep4.jpg",
    "../../assets/images/kep5.jpg",
    "../../assets/images/kep6.jpg",
    "../../assets/images/kep7.jpg",
    "../../assets/images/kep8.jpg",
    "../../assets/images/kep9.jpg",
    "../../assets/images/kep10.jpg",
    "../../assets/images/kep11.jpg",
    "../../assets/images/kep12.jpg",
    "../../assets/images/kep13.jpg",
    "../../assets/images/kep14.jpg"
  ];

const gameBoard = document.getElementById("game-board");
const targetImage = document.getElementById("target-image");
const timerElement = document.getElementById("timer");
const choicesContainer = document.getElementById("choices-container");
const choicesGrid = document.getElementById("choices-grid");
const resultScreen = document.getElementById("result-screen");
const resultMessage = document.getElementById("result-message");
const nextRoundBtn = document.getElementById("next-round");

let timer;
let score = 0;
let currentTarget = "";

startRound()

function startRound() {
    document.getElementById("target-container").classList.remove("hidden");
    choicesContainer.classList.add("hidden");
    resultScreen.classList.add("hidden");

    currentTarget = images[Math.floor(Math.random() * images.length)];
    targetImage.src = currentTarget;

    let timeLeft = 5;
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

    if (choice === currentTarget) {
        score++;
        resultMessage.textContent = `Helyes! Pontjaid: ${score}`;
    } else {
        resultMessage.textContent = `Rossz :( Pontjaid: ${score}`;
    }
}

nextRoundBtn.addEventListener("click", () => {
    resultScreen.classList.add("hidden");
    document.getElementById("target-container").classList.remove("hidden");
    startRound();
});