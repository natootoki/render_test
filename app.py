# app.py（修正版）
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI(title="Render WebSocket Chat")
STATIC_DIR = Path(__file__).parent / "static"

@app.get("/healthz")
def healthz():
    return JSONResponse({"status": "ok"})

# ① WebSocket ルート（先に定義）
class ConnectionManager:
    def __init__(self):
        self.active: set[WebSocket] = set()
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.add(websocket)
    def disconnect(self, websocket: WebSocket):
        self.active.discard(websocket)
    async def broadcast(self, message: dict):
        dead = []
        for ws in list(self.active):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        await manager.broadcast({"system": True, "text": "👋 someone joined"})
        while True:
            data = await ws.receive_json()
            msg = {
                "system": False,
                "name": (data.get("name") or "anonymous")[:32],
                "text": (data.get("text") or "")[:2000],
            }
            await manager.broadcast(msg)
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(ws)
        await manager.broadcast({"system": True, "text": "👋 someone left"})

# ② "/" は index.html を直接返す
@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")

# ③ 静的ファイルは /static 配下にマウント
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
