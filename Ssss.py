import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="☄️ 운석 피하기",
    page_icon="☄️",
    layout="centered"
)

st.title("☄️ 운석 피하기")
st.caption("하늘에서 떨어지는 운석을 피하고 최대한 오래 살아남으세요!")

game_code = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #080b18;
    color: white;
    font-family: Arial, sans-serif;
    text-align: center;
    overflow: hidden;
}

#game {
    width: 100%;
    max-width: 700px;
    height: 650px;
    margin: auto;
    position: relative;
    overflow: hidden;
    border: 3px solid #303858;
    border-radius: 18px;
    background:
        radial-gradient(circle at 20% 20%, #26315d 1px, transparent 2px),
        radial-gradient(circle at 70% 30%, #ffffff 1px, transparent 2px),
        radial-gradient(circle at 40% 70%, #7884ad 1px, transparent 2px),
        #080b18;
    background-size: 130px 130px, 190px 190px, 230px 230px;
}

#top {
    position: absolute;
    top: 10px;
    left: 12px;
    right: 12px;
    z-index: 20;
    display: flex;
    justify-content: space-between;
    font-size: 16px;
    font-weight: bold;
}

#player {
    position: absolute;
    bottom: 45px;
    left: 50%;
    transform: translateX(-50%);
    width: 42px;
    height: 50px;
    font-size: 40px;
    z-index: 10;
    user-select: none;
}

.rock {
    position: absolute;
    top: -70px;
    border-radius: 50%;
    background: radial-gradient(circle at 30% 25%, #ffb36b, #9b4b25 45%, #4b2018 80%);
    box-shadow: 0 0 15px #ff713d;
    z-index: 5;
}

.rock.big {
    background: radial-gradient(circle at 30% 25%, #ffd08a, #ad4922 45%, #391710 80%);
    box-shadow: 0 0 25px #ff4d2e;
}

.rock.fast {
    background: radial-gradient(circle at 30% 25%, #fff0a3, #ff6b25 45%, #6b2117 80%);
}

#shield {
    display: none;
    position: absolute;
    border: 4px solid #54d9ff;
    border-radius: 50%;
    width: 75px;
    height: 75px;
    left: 50%;
    bottom: 32px;
    transform: translateX(-50%);
    z-index: 11;
    box-shadow: 0 0 25px #2acfff;
    animation: shieldPulse .6s infinite alternate;
}

@keyframes shieldPulse {
    from { opacity: .65; }
    to { opacity: 1; }
}

#menu {
    position: absolute;
    inset: 0;
    background: rgba(4,6,15,.94);
    z-index: 50;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 20px;
}

#menu h1 {
    font-size: 34px;
    margin-bottom: 8px;
}

#menu p {
    color: #bfc7e6;
}

button {
    border: none;
    border-radius: 12px;
    padding: 10px 18px;
    margin: 5px;
    background: #29335d;
    color: white;
    font-size: 16px;
    cursor: pointer;
}

button:hover {
    background: #3d4c86;
}

.character {
    display: inline-block;
    width: 95px;
    height: 95px;
    margin: 5px;
    border: 2px solid #444d72;
    border-radius: 15px;
    background: #11172d;
    padding: 8px;
}

.character.selected {
    border-color: #55d9ff;
    box-shadow: 0 0 15px #55d9ff;
}

.charIcon {
    font-size: 35px;
}

#controls {
    position: absolute;
    bottom: 8px;
    left: 0;
    right: 0;
    z-index: 30;
    display: flex;
    justify-content: space-between;
    padding: 0 15px;
    pointer-events: none;
}

.controlGroup {
    display: flex;
    gap: 8px;
}

.control {
    pointer-events: auto;
    width: 48px;
    height: 40px;
    padding: 0;
    margin: 0;
    font-size: 20px;
    border-radius: 10px;
    background: rgba(48,58,100,.9);
}

#skill {
    width: 62px;
    font-size: 14px;
    background: rgba(35,116,145,.95);
}

#message {
    position: absolute;
    top: 45%;
    width: 100%;
    z-index: 40;
    font-size: 28px;
    font-weight: bold;
    text-shadow: 0 0 10px black;
    display: none;
}
</style>
</head>

<body>

<div id="game">

    <div id="top">
        <div>❤️ <span id="hp">3</span></div>
        <div>🏆 <span id="score">0</span></div>
        <div>🛡️ <span id="skillCount">3</span></div>
    </div>

    <div id="player">🧑‍🚀</div>
    <div id="shield"></div>

    <div id="message"></div>

    <div id="controls">
        <div class="controlGroup">
            <button class="control" id="left">◀</button>
            <button class="control" id="right">▶</button>
        </div>

        <button class="control" id="skill">🛡️</button>
    </div>

    <div id="menu">
        <h1>☄️ 운석 피하기</h1>
        <p>캐릭터를 선택하고 운석을 피해보세요!</p>

        <div id="characters"></div>

        <button id="startBtn">🚀 게임 시작</button>

        <p style="font-size:13px;">
            PC: ← → 로 이동 / 스페이스로 방패<br>
            모바일: 아래 버튼으로 이동
        </p>
    </div>
</div>

<script>

const game = document.getElementById("game");
const player = document.getElementById("player");
const shield = document.getElementById("shield");
const hpText = document.getElementById("hp");
const scoreText = document.getElementById("score");
const skillText = document.getElementById("skillCount");
const menu = document.getElementById("menu");
const message = document.getElementById("message");

const characters = [
    {
        name: "우주인",
        icon: "🧑‍🚀",
        speed: 7,
        shield: 3
    },
    {
        name: "로봇",
        icon: "🤖",
        speed: 9,
        shield: 2
    },
    {
        name: "외계인",
        icon: "👽",
        speed: 6,
        shield: 4
    },
    {
        name: "닌자",
        icon: "🥷",
        speed: 11,
        shield: 1
    }
];

let selected = 0;
let playerX = 0;
let speed = 7;

let hp = 3;
let score = 0;
let shieldCount = 3;

let rocks = [];
let gameRunning = false;
let lastTime = 0;
let spawnTimer = 0;
let difficulty = 1;
let shieldActive = false;
let shieldTimer = 0;

const charBox = document.getElementById("characters");

characters.forEach((c, i) => {

    const box = document.createElement("button");
    box.className = "character" + (i === 0 ? " selected" : "");

    box.innerHTML =
        `<div class="charIcon">${c.icon}</div>
         <div>${c.name}</div>
         <small>속도 ${c.speed}</small>`;

    box.onclick = () => {

        selected = i;
        speed = characters[i].speed;

        document.querySelectorAll(".character")
            .forEach(x => x.classList.remove("selected"));

        box.classList.add("selected");

        player.innerText = characters[i].icon;
    };

    charBox.appendChild(box);
});

function startGame() {

    rocks.forEach(r => r.el.remove());
    rocks = [];

    hp = 3;
    score = 0;
    difficulty = 1;

    shieldCount = characters[selected].shield;

    playerX = game.clientWidth / 2;

    hpText.innerText = hp;
    scoreText.innerText = score;
    skillText.innerText = shieldCount;

    player.style.left = playerX + "px";

    menu.style.display = "none";
    message.style.display = "none";

    gameRunning = true;
    lastTime = performance.now();
    spawnTimer = 0;

    requestAnimationFrame(gameLoop);
}

function move(dir) {

    if (!gameRunning) return;

    playerX += dir * speed;

    const half = 25;

    playerX = Math.max(
        half,
        Math.min(game.clientWidth - half, playerX)
    );

    player.style.left = playerX + "px";
}

function activateShield() {

    if (!gameRunning) return;
    if (shieldActive) return;
    if (shieldCount <= 0) return;

    shieldCount--;
    skillText.innerText = shieldCount;

    shieldActive = true;
    shieldTimer = 1500;

    shield.style.display = "block";
}

function spawnRock() {

    const rock = document.createElement("div");
    rock.classList.add("rock");

    const random = Math.random();

    let size;
    let fallSpeed;

    if (random < 0.2) {

        size = 60 + Math.random() * 30;
        fallSpeed = 2.5 + Math.random() * 1.5;
        rock.classList.add("big");

    } else if (random < 0.45) {

        size = 25 + Math.random() * 15;
        fallSpeed = 5 + Math.random() * 2;
        rock.classList.add("fast");

    } else {

        size = 35 + Math.random() * 20;
        fallSpeed = 3 + Math.random() * 2;
    }

    size *= Math.min(1.25, difficulty / 2 + 0.75);

    rock.style.width = size + "px";
    rock.style.height = size + "px";

    let x = Math.random() * (game.clientWidth - size);

    rock.style.left = x + "px";
    rock.style.top = "-80px";

    game.appendChild(rock);

    rocks.push({
        el: rock,
        x: x,
        y: -80,
        size: size,
        speed: fallSpeed * difficulty
    });
}

function collision(a, b) {

    return !(
        a.right < b.left ||
        a.left > b.right ||
        a.bottom < b.top ||
        a.top > b.bottom
    );
}

function hitPlayer(rock) {

    const p = player.getBoundingClientRect();
    const r = rock.el.getBoundingClientRect();

    if (!collision(p, r)) return false;

    if (shieldActive) {
        return "shield";
    }

    return true;
}

function loseHP() {

    hp--;

    hpText.innerText = hp;

    player.style.transform =
        "translateX(-50%) scale(1.3)";

    setTimeout(() => {
        player.style.transform =
            "translateX(-50%) scale(1)";
    }, 120);

    if (hp <= 0) {
        endGame();
    }
}

function endGame() {

    gameRunning = false;

    message.innerHTML =
        `💥 게임 오버!<br>
         <span style="font-size:20px;">점수: ${Math.floor(score)}</span>`;

    message.style.display = "block";

    setTimeout(() => {
        menu.style.display = "flex";
        message.style.display = "none";
    }, 1800);
}

function gameLoop(time) {

    if (!gameRunning) return;

    const dt = Math.min(40, time - lastTime);
    lastTime = time;

    score += dt * 0.01;
    scoreText.innerText = Math.floor(score);

    difficulty =
        1 + Math.floor(score / 100) * 0.15;

    spawnTimer += dt;

    const spawnDelay =
        Math.max(250, 850 / difficulty);

    if (spawnTimer > spawnDelay) {
        spawnTimer = 0;
        spawnRock();

        if (difficulty > 1.5 && Math.random() < 0.25) {
            setTimeout(spawnRock, 100);
        }
    }

    if (shieldActive) {

        shieldTimer -= dt;

        if (shieldTimer <= 0) {
            shieldActive = false;
            shield.style.display = "none";
        }
    }

    for (let i = rocks.length - 1; i >= 0; i--) {

        const r = rocks[i];

        r.y += r.speed * (dt / 16);

        r.el.style.top = r.y + "px";

        const hit = hitPlayer(r);

        if (hit) {

            if (hit === "shield") {
                r.el.remove();
                rocks.splice(i, 1);
                score += 5;
                continue;
            }

            r.el.remove();
            rocks.splice(i, 1);

            loseHP();

            if (!gameRunning) return;

            continue;
        }

        if (r.y > game.clientHeight + 80) {

            r.el.remove();
            rocks.splice(i, 1);

            score += 1;
        }
    }

    requestAnimationFrame(gameLoop);
}

document.addEventListener("keydown", e => {

    if (e.key === "ArrowLeft") {
        e.preventDefault();
        move(-1);
    }

    if (e.key === "ArrowRight") {
        e.preventDefault();
        move(1);
    }

    if (e.code === "Space") {
        e.preventDefault();
        activateShield();
    }
});

let leftPressed = false;
let rightPressed = false;

function holdButton(button, direction) {

    button.addEventListener("touchstart", e => {
        e.preventDefault();
        move(direction);
    });

    button.addEventListener("mousedown", e => {
        e.preventDefault();
        move(direction);
    });
}

holdButton(document.getElementById("left"), -1);
holdButton(document.getElementById("right"), 1);

document.getElementById("skill").addEventListener(
    "click",
    activateShield
);

document.getElementById("startBtn").onclick = startGame;

</script>

</body>
</html>
"""

components.html(game_code, height=680, scrolling=False)
