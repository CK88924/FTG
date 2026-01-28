from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from .ws import router as ws_router

app = FastAPI()

app.include_router(ws_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get():
    return RedirectResponse(url="/static/index.html")
