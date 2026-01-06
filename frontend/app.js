document.addEventListener("DOMContentLoaded", () => {

    const canvas = document.getElementById("board");
    const ctx = canvas.getContext("2d");
    const createBtn = document.getElementById("createBtn");
    const info = document.getElementById("info");
    const roomInfo = document.getElementById("roomInfo");

    const SIZE = 15;
    const CELL = 30;
    const RADIUS = 10;

    let roomId = null;
    let myRole = null;
    let gameFinished = false;

    // ===== playerId（兼容老手机）=====
    let playerId = localStorage.getItem("playerId");
    if (!playerId) {
        playerId = Date.now().toString() + Math.random().toString(36).slice(2);
        localStorage.setItem("playerId", playerId);
    }

    // ===== 画棋盘 + 棋子 =====
    function drawBoard(board) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // --- 棋盘线 ---
        ctx.strokeStyle = "#666";
        for (let i = 0; i < SIZE; i++) {
            ctx.beginPath();
            ctx.moveTo(CELL / 2, CELL / 2 + i * CELL);
            ctx.lineTo(CELL / 2 + (SIZE - 1) * CELL, CELL / 2 + i * CELL);
            ctx.stroke();

            ctx.beginPath();
            ctx.moveTo(CELL / 2 + i * CELL, CELL / 2);
            ctx.lineTo(CELL / 2 + i * CELL, CELL / 2 + (SIZE - 1) * CELL);
            ctx.stroke();
        }

        // --- 棋子 ---
        for (let y = 0; y < SIZE; y++) {
            for (let x = 0; x < SIZE; x++) {
                if (board[y][x] !== 0) {
                    ctx.beginPath();
                    ctx.arc(
                        CELL / 2 + x * CELL,
                        CELL / 2 + y * CELL,
                        RADIUS,
                        0,
                        Math.PI * 2
                    );

                    if (board[y][x] === 1) {
                        ctx.fillStyle = "#000";
                        ctx.fill();
                    } else {
                        ctx.fillStyle = "#fff";
                        ctx.fill();
                        ctx.lineWidth = 2;
                        ctx.strokeStyle = "#000";
                        ctx.stroke();
                    }
                }
            }
        }
    }

    // ===== 点击落子 =====
    canvas.addEventListener("click", async (e) => {
        if (!roomId || myRole === "spectator") return;
        if (gameFinished) return;

        const rect = canvas.getBoundingClientRect();
        const x = Math.floor((e.clientX - rect.left) / CELL);
        const y = Math.floor((e.clientY - rect.top) / CELL);

        if (x < 0 || x >= SIZE || y < 0 || y >= SIZE) return;

        await fetch("/move", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                room_id: roomId,
                player_id: playerId,
                x,
                y
            })
        });
    });

    // ===== 创建房间 =====
    createBtn.onclick = async () => {
        const res = await fetch("/create_room", { method: "POST" });
        const data = await res.json();

        roomId = data.room_id;
        history.replaceState(null, "", `/?room=${roomId}`);

        roomInfo.innerHTML =
            `房间号：${roomId}<br>分享链接：${location.href}`;

        joinRoom();
    };

    // ===== 加入房间 =====
    async function joinRoom() {
        const res = await fetch("/join_room", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                room_id: roomId,
                player_id: playerId
            })
        });

        const data = await res.json();
        myRole = data.role;

        poll();
        setInterval(poll, 1000);
    }

    // ===== 拉取棋局状态（★关键修改在这里）=====
    async function poll() {
        const res = await fetch(`/state/${roomId}`);
        const data = await res.json();

        drawBoard(data.board);

        // ===== 游戏结束 =====
        if (data.finished) {
            gameFinished = true;

            if (data.winner === "black") {
                info.innerText = "♟ 黑棋胜利！";
            } else if (data.winner === "white") {
                info.innerText = "♟ 白棋胜利！";
            } else {
                info.innerText = "🤝 平局";
            }
            return;
        }

        // ===== 游戏进行中 =====
        info.innerText = `你是：${myRole} ｜ 当前回合：${data.turn}`;
    }

    // ===== 处理分享链接 =====
    const params = new URLSearchParams(location.search);
    if (params.get("room")) {
        roomId = params.get("room");
        joinRoom();
    }

});
