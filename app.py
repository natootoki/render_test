from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Render WebSocket Chat")

# 静的ファイル（index.html）をルートにマウント
app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/healthz")
def healthz():
    return JSONResponse({"status": "ok"})

class ConnectionManager:
    def __init__(self):
        self.active: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active.discard(websocket)

    async def broadcast(self, message: dict):
        # 送信失敗した接続は切断
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
            # data 例: {"name":"taro","text":"hello"}
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
