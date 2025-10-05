from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Render FastAPI sample", version="1.0.0")

@app.get("/")
def root():
    return {"ok": True, "message": "Hello from Render + FastAPI!"}

@app.get("/healthz")
def healthz():
    # Render のヘルスチェックに使える軽量エンドポイント
    return {"status": "healthy"}

class EchoIn(BaseModel):
    text: str

@app.post("/echo")
def echo(payload: EchoIn):
    return {"you_said": payload.text}

class SumIn(BaseModel):
    numbers: List[float]

@app.post("/sum")
def sum_numbers(payload: SumIn):
    return {"sum": sum(payload.numbers), "count": len(payload.numbers)}
