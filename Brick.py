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
        background: white;
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


// =============================
// 공 여러 개
// =============================

let balls = [];

function createBall(x, y, dx, dy) {

    return {
        x: x,
        y: y,
        r: 8,
        dx: dx,
        dy: dy
    };

}


// =============================
// 패들
// =============================

let paddle = {
    width: 100,
    height: 12,
    x: W / 2 - 50,
    y: H - 30,
    speed: 8
};


// =============================
// 게임 정보
// =============================

let score = 0;
let lives = 3;
let level = 1;

let keys = {
    left: false,
    right: false
};


// =============================
// 벽돌
// =============================

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

            // 약 10개 중 1개 확률
            const special = Math.random() < 0.1;

            bricks.push({

                x: startX + c * (brickWidth + gap),
                y: startY + r * (brickHeight + gap),

                width: brickWidth,
                height: brickHeight,

                alive: true,

                // 일반 벽돌 = 1
                // 파란 벽돌 = 3
                hp: special ? 3 : 1,

                maxHp: special ? 3 : 1,

                special: special

            });

        }
    }
}


// =============================
// 공 그리기
// =============================

function drawBall(ball) {

    ctx.beginPath();

    ctx.arc(
        ball.x,
        ball.y,
        ball.r,
        0,
        Math.PI * 2
    );

    ctx.fillStyle = "white";

    ctx.fill();

    ctx.closePath();
}


// =============================
// 패들 그리기
// =============================

function drawPaddle() {

    ctx.fillStyle = "#00d9ff";

    ctx.fillRect(
        paddle.x,
        paddle.y,
        paddle.width,
        paddle.height
    );
}


// =============================
// 벽돌 그리기
// =============================

function drawBricks() {

    bricks.forEach((brick, index) => {

        if (!brick.alive) return;


        // 특수 벽돌
        if (brick.special) {

            if (brick.hp === 3) {

                ctx.fillStyle = "#006eff";

            } else if (brick.hp === 2) {

                ctx.fillStyle = "#38a9ff";

            } else {

                ctx.fillStyle = "#8bd5ff";

            }

        }

        // 일반 벽돌
        else {

            ctx.fillStyle =
                [
                    "#ff4d4d",
                    "#ff9f43",
                    "#feca57",
                    "#1dd1a1",
                    "#54a0ff",
                    "#a55eea"
                ][index % 6];

        }


        ctx.fillRect(
            brick.x,
            brick.y,
            brick.width,
            brick.height
        );


        // 파란 벽돌 체력 표시
        if (brick.special) {

            ctx.fillStyle = "white";

            ctx.font = "bold 13px Arial";

            ctx.textAlign = "center";

            ctx.fillText(
                brick.hp,
                brick.x + brick.width / 2,
                brick.y + 16
            );

        }

    });

}


// =============================
// 화면 그리기
// =============================

function draw() {

    ctx.clearRect(0, 0, W, H);

    drawBricks();

    balls.forEach(ball => {
        drawBall(ball);
    });

    drawPaddle();

    update();

    requestAnimationFrame(draw);
}


// =============================
// 공 하나 업데이트
// =============================

function updateBall(ball) {

    ball.x += ball.dx;
    ball.y += ball.dy;


    // 좌우 벽

    if (
        ball.x - ball.r < 0 ||
        ball.x + ball.r > W
    ) {

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


        let hit =
            (
                ball.x -
                (paddle.x + paddle.width / 2)
            )
            /
            (paddle.width / 2);


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


            // 공 방향 반전

            ball.dy *= -1;


            // 특수 벽돌

            if (brick.special) {

                brick.hp--;


                // 3번 모두 맞음
                if (brick.hp <= 0) {

                    brick.alive = false;

                    score += 30;

                    document.getElementById("score")
                        .textContent = score;


                    // ==========================
                    // 공 3개 생성
                    // ==========================

                    // 기존 공 방향을 기준으로
                    // 서로 다른 방향으로 생성

                    const speed =
                        Math.sqrt(
                            ball.dx * ball.dx +
                            ball.dy * ball.dy
                        );


                    balls.push(
                        createBall(
                            ball.x,
                            ball.y,
                            speed * 0.9,
                            -speed
                        )
                    );


                    balls.push(
                        createBall(
                            ball.x,
                            ball.y,
                            -speed * 0.9,
                            -speed
                        )
                    );


                    // 기존 공은 그대로 유지

                }

            }


            // 일반 벽돌

            else {

                brick.alive = false;

                score += 10;

                document.getElementById("score")
                    .textContent = score;

            }


            checkLevel();

        }

    });

}


// =============================
// 게임 업데이트
// =============================

function update() {


    // 패들 이동

    if (keys.left) {

        paddle.x -= paddle.speed;

    }

    if (keys.right) {

        paddle.x += paddle.speed;

    }


    // 화면 밖 방지

    if (paddle.x < 0) {

        paddle.x = 0;

    }

    if (paddle.x + paddle.width > W) {

        paddle.x =
            W - paddle.width;

    }


    // 모든 공 업데이트

    for (
        let i = balls.length - 1;
        i >= 0;
        i--
    ) {

        let ball = balls[i];

        updateBall(ball);


        // 아래로 떨어진 공

        if (ball.y - ball.r > H) {

            balls.splice(i, 1);

        }

    }


    // 공이 전부 사라졌을 때

    if (balls.length === 0) {

        lives--;

        document.getElementById("lives")
            .textContent = lives;


        if (lives <= 0) {

            alert(
                "게임 오버!\n점수: " + score
            );

            restartGame();

        }

        else {

            resetBall();

        }

    }

}


// =============================
// 레벨 체크
// =============================

function checkLevel() {

    const remaining =
        bricks.filter(
            brick => brick.alive
        ).length;


    if (remaining === 0) {

        level++;


        document.getElementById("level")
            .textContent = level;


        createBricks();

        resetBall();

    }

}


// =============================
// 공 초기화
// =============================

function resetBall() {

    balls = [];


    balls.push(
        createBall(
            W / 2,
            H - 60,
            4 + (level - 1) * 0.5,
            -4 - (level - 1) * 0.5
        )
    );


    paddle.x =
        W / 2 -
        paddle.width / 2;

}


// =============================
// 게임 재시작
// =============================

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


// =============================
// 키보드
// =============================

document.addEventListener(
    "keydown",
    e => {

        if (
            e.key === "ArrowLeft" ||
            e.key.toLowerCase() === "a"
        ) {

            keys.left = true;

        }


        if (
            e.key === "ArrowRight" ||
            e.key.toLowerCase() === "d"
        ) {

            keys.right = true;

        }

    }
);


document.addEventListener(
    "keyup",
    e => {

        if (
            e.key === "ArrowLeft" ||
            e.key.toLowerCase() === "a"
        ) {

            keys.left = false;

        }


        if (
            e.key === "ArrowRight" ||
            e.key.toLowerCase() === "d"
        ) {

            keys.right = false;

        }

    }
);


// =============================
// 마우스
// =============================

canvas.addEventListener(
    "mousemove",
    e => {

        const rect =
            canvas.getBoundingClientRect();


        const mouseX =
            (e.clientX - rect.left)
            *
            (W / rect.width);


        paddle.x =
            mouseX -
            paddle.width / 2;

    }
);


// =============================
// 모바일
// =============================

canvas.addEventListener(
    "touchmove",
    e => {

        e.preventDefault();


        const rect =
            canvas.getBoundingClientRect();


        const touchX =
            (e.touches[0].clientX - rect.left)
            *
            (W / rect.width);


        paddle.x =
            touchX -
            paddle.width / 2;

    },
    {
        passive: false
    }
);


// 게임 시작

createBricks();

resetBall();

draw();

</script>

</body>
</html>
"""

components.html(
    game,
    height=590,
    scrolling=False
)
