from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Optional
import uuid
import os

app = FastAPI()

# ================= 基本配置 =================

BOARD_SIZE = 15

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


# ================= 房间数据结构 =================

class Room:
    def __init__(self):
        self.board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.turn = 1              # 1 = 黑棋，2 = 白棋
        self.black: Optional[str] = None
        self.white: Optional[str] = None
        self.winner: Optional[int] = None  # 1 / 2 / None
        self.finished: bool = False


rooms: Dict[str, Room] = {}


# ================= 请求模型 =================

class JoinReq(BaseModel):
    room_id: str
    player_id: str


class MoveReq(BaseModel):
    room_id: str
    player_id: str
    x: int
    y: int


# ================= 工具函数 =================

def check_winner(board, x, y, p):
    """
    检查从 (x, y) 落子点开始，是否形成五子连珠
    """
    directions = [
        (1, 0),   # 横
        (0, 1),   # 竖
        (1, 1),   # 右下
        (1, -1),  # 右上
    ]

    for dx, dy in directions:
        cnt = 1

        # 正方向
        i = 1
        while True:
            nx, ny = x + dx * i, y + dy * i
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and board[ny][nx] == p:
                cnt += 1
                i += 1
            else:
                break

        # 反方向
        i = 1
        while True:
            nx, ny = x - dx * i, y - dy * i
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and board[ny][nx] == p:
                cnt += 1
                i += 1
            else:
                break

        if cnt >= 5:
            return True

    return False


def board_full(board):
    return all(all(cell != 0 for cell in row) for row in board)


# ================= API =================

@app.post("/create_room")
def create_room():
    room_id = uuid.uuid4().hex[:8]
    rooms[room_id] = Room()
    return {"room_id": room_id}


@app.post("/join_room")
def join_room(req: JoinReq):
    room = rooms.get(req.room_id)
    if not room:
        raise HTTPException(404, "room not found")

    if room.black == req.player_id:
        return {"role": "black"}
    if room.white == req.player_id:
        return {"role": "white"}

    if room.black is None:
        room.black = req.player_id
        return {"role": "black"}

    if room.white is None:
        room.white = req.player_id
        return {"role": "white"}

    return {"role": "spectator"}


@app.get("/state/{room_id}")
def state(room_id: str):
    room = rooms.get(room_id)
    if not room:
        raise HTTPException(404, "room not found")

    return {
        "board": room.board,
        "turn": "black" if room.turn == 1 else "white",
        "winner": (
            "black" if room.winner == 1 else
            "white" if room.winner == 2 else
            "draw" if room.finished else
            None
        ),
        "finished": room.finished
    }


@app.post("/move")
def move(req: MoveReq):
    room = rooms.get(req.room_id)
    if not room:
        raise HTTPException(404, "room not found")

    # 游戏已结束
    if room.finished:
        return {
            "ok": False,
            "winner": "black" if room.winner == 1 else "white"
        }

    # 校验回合
    if room.turn == 1 and room.black != req.player_id:
        raise HTTPException(403, "not your turn")
    if room.turn == 2 and room.white != req.player_id:
        raise HTTPException(403, "not your turn")

    x, y = req.x, req.y

    # 越界
    if not (0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE):
        raise HTTPException(400, "out of board")

    # 已有棋子
    if room.board[y][x] != 0:
        raise HTTPException(400, "cell occupied")

    # 落子
    room.board[y][x] = room.turn

    # ===== 判断胜利 =====
    if check_winner(room.board, x, y, room.turn):
        room.winner = room.turn
        room.finished = True
        return {
            "ok": True,
            "winner": "black" if room.turn == 1 else "white"
        }

    # ===== 判断平局 =====
    if board_full(room.board):
        room.finished = True
        room.winner = None
        return {
            "ok": True,
            "winner": "draw"
        }

    # 切换回合
    room.turn = 2 if room.turn == 1 else 1
    return {"ok": True}

