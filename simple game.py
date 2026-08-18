import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="벽돌 깨기",
    page_icon="🧱",
    layout="centered"
)

st.title("🧱 벽돌 깨기")

game = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    body {
        margin: 0;
        background: #111;
        color: white;
        font-family: Arial, sans-serif;
        text-align: center;
        overflow: hidden;
    }

    #gameContainer {
        width: 100%;
        max-width: 600px;
        margin: auto;
    }

    canvas {
        background: #050505;
        border: 2px solid white;
        border-radius: 10px;
        width: 100%;
        height: auto;
        touch-action: none;
    }

    #info {
        display: flex;
        justify-content: space-between;
        padding: 8px 5px;
        font-size: 18px;
    }

    button {
        background: #ffffff;
        border: none;
        padding: 10px 22px;
        border-radius: 8px;
        font-size: 16px;
        cursor: pointer;
        margin-top: 8px;
    }

    button:hover {
        background: #ddd;
    }
</style>
</head>

<body>

<div id="gameContainer">

    <div id="info">
        <span>점수: <b id="score">0</b></span>
        <span>목숨: <b id="lives">3</b></span>
        <span>레벨: <b id="level">1</b></span>
    </div>

    <canvas id="game" width="600" height="500"></canvas>

    <button onclick="restartGame()">🔄 다시 시작</button>

</div>

<script>

const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

const W = canvas.width;
const H = canvas.height;

// 공
let ball = {
    x: W / 2,
    y: H - 60,
    r: 8,
    dx: 4,
    dy: -4
};

// 패들
let paddle = {
    width: 100,
    height: 12,
    x: W / 2 - 50,
    y: H - 30,
    speed: 8
};

let score = 0;
let lives = 3;
let level = 1;

let keys = {
    left: false,
    right: false
};

// 벽돌
let bricks = [];

function createBricks() {

    bricks = [];

    const rows = 5 + level - 1;
    const cols = 8;

    const brickWidth = 62;
    const brickHeight = 22;
    const gap = 8;

    const startX = 35;
    const startY = 45;

    for (let r = 0; r < rows; r++) {

        for (let c = 0; c < cols; c++) {

            bricks.push({
                x: startX + c * (brickWidth + gap),
                y: startY + r * (brickHeight + gap),
                width: brickWidth,
                height: brickHeight,
                alive: true
            });

        }
    }
}

createBricks();

function drawBall() {

    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.r, 0, Math.PI * 2);

    ctx.fillStyle = "#ffffff";
    ctx.fill();

    ctx.closePath();
}

function drawPaddle() {

    ctx.fillStyle = "#00d9ff";

    ctx.fillRect(
        paddle.x,
        paddle.y,
        paddle.width,
        paddle.height
    );
}

function drawBricks() {

    bricks.forEach((brick, index) => {

        if (!brick.alive) return;

        ctx.fillStyle =
            ["#ff4d4d", "#ff9f43", "#feca57",
             "#1dd1a1", "#54a0ff", "#a55eea"][index % 6];

        ctx.fillRect(
            brick.x,
            brick.y,
            brick.width,
            brick.height
        );
    });
}

function draw() {

    ctx.clearRect(0, 0, W, H);

    drawBricks();
    drawBall();
    drawPaddle();

    update();

    requestAnimationFrame(draw);
}

function update() {

    // 패들 이동
    if (keys.left) {
        paddle.x -= paddle.speed;
    }

    if (keys.right) {
        paddle.x += paddle.speed;
    }

    // 화면 밖 방지
    if (paddle.x < 0)
        paddle.x = 0;

    if (paddle.x + paddle.width > W)
        paddle.x = W - paddle.width;

    // 공 이동
    ball.x += ball.dx;
    ball.y += ball.dy;

    // 좌우 벽
    if (ball.x - ball.r < 0 ||
        ball.x + ball.r > W) {

        ball.dx *= -1;
    }

    // 위쪽 벽
    if (ball.y - ball.r < 0) {

        ball.dy *= -1;
    }

    // 패들 충돌
    if (
        ball.y + ball.r >= paddle.y &&
        ball.y - ball.r <= paddle.y + paddle.height &&
        ball.x >= paddle.x &&
        ball.x <= paddle.x + paddle.width &&
        ball.dy > 0
    ) {

        ball.dy *= -1;

        // 패들 위치에 따라 공의 방향 변경
        let hit =
            (ball.x - (paddle.x + paddle.width / 2))
            / (paddle.width / 2);

        ball.dx = hit * 6;
    }

    // 벽돌 충돌
    bricks.forEach(brick => {

        if (!brick.alive) return;

        if (
            ball.x + ball.r > brick.x &&
            ball.x - ball.r < brick.x + brick.width &&
            ball.y + ball.r > brick.y &&
            ball.y - ball.r < brick.y + brick.height
        ) {

            brick.alive = false;

            ball.dy *= -1;

            score += 10;

            document.getElementById("score")
                .textContent = score;

            checkLevel();
        }

    });

    // 공이 아래로 떨어짐
    if (ball.y - ball.r > H) {

        lives--;

        document.getElementById("lives")
            .textContent = lives;

        if (lives <= 0) {

            alert("게임 오버!\n점수: " + score);

            restartGame();

        } else {

            resetBall();
        }
    }
}

function checkLevel() {

    const remaining =
        bricks.filter(b => b.alive).length;

    if (remaining === 0) {

        level++;

        document.getElementById("level")
            .textContent = level;

        ball.dx *= 1.1;
        ball.dy *= 1.1;

        createBricks();

        resetBall();
    }
}

function resetBall() {

    ball.x = W / 2;
    ball.y = H - 60;

    ball.dx = 4 + (level - 1) * 0.5;
    ball.dy = -4 - (level - 1) * 0.5;

    paddle.x = W / 2 - paddle.width / 2;
}

function restartGame() {

    score = 0;
    lives = 3;
    level = 1;

    document.getElementById("score")
        .textContent = score;

    document.getElementById("lives")
        .textContent = lives;

    document.getElementById("level")
        .textContent = level;

    createBricks();
    resetBall();
}

// 키보드
document.addEventListener("keydown", e => {

    if (e.key === "ArrowLeft" || e.key === "a")
        keys.left = true;

    if (e.key === "ArrowRight" || e.key === "d")
        keys.right = true;
});

document.addEventListener("keyup", e => {

    if (e.key === "ArrowLeft" || e.key === "a")
        keys.left = false;

    if (e.key === "ArrowRight" || e.key === "d")
        keys.right = false;
});

// 마우스
canvas.addEventListener("mousemove", e => {

    const rect = canvas.getBoundingClientRect();

    const mouseX =
        (e.clientX - rect.left)
        * (W / rect.width);

    paddle.x =
        mouseX - paddle.width / 2;

});

// 모바일 터치
canvas.addEventListener("touchmove", e => {

    e.preventDefault();

    const rect = canvas.getBoundingClientRect();

    const touchX =
        (e.touches[0].clientX - rect.left)
        * (W / rect.width);

    paddle.x =
        touchX - paddle.width / 2;

}, { passive: false });

draw();

</script>

</body>
</html>
"""

components.html(game, height=590, scrolling=False)
