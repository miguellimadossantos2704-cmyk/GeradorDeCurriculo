import asyncio
import json
import logging
import os
import tempfile
import random
from fastapi import FastAPI, UploadFile, File, WebSocket, BackgroundTasks, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AutomationRequest(BaseModel):
    keywords: str

# Store connected active websocket clients
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str, type: str = "info", status: str = "running"):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps({"message": message, "type": type, "status": status}))
            except Exception:
                pass

manager = ConnectionManager()

latest_pdf_path = None

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global latest_pdf_path
    tmp_path = os.path.join(tempfile.gettempdir(), file.filename)
    with open(tmp_path, "wb") as f:
        f.write(await file.read())
    latest_pdf_path = tmp_path
    return {"message": "Success", "filename": file.filename}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def automation_task(keywords: str):
    await manager.broadcast("Starting undetected Selenium driver...", "system")
    
    try:
        # Inicializa o undetected chromedriver
        options = uc.ChromeOptions()
        # options.add_argument('--headless') # Descomente para rodar headless (sem interface)
        
        driver = uc.Chrome(options=options)
        
        platforms = ["Joinrs", "LinkedIn"]
        
        for platform in platforms:
            await manager.broadcast(f"[{platform}] Navigating to job board...", "info")
            await asyncio.sleep(3)  # Simulando tempo de navegação
            
            # Aqui entraria a lógica real do Selenium de navegação, por exemplo:
            # if platform == "LinkedIn":
            #     driver.get("https://www.linkedin.com/jobs/search/?keywords=" + keywords)
            
            await manager.broadcast(f"[{platform}] Found matching roles for: {keywords}", "success")
            await asyncio.sleep(2)
            
            await manager.broadcast(f"[{platform}] Injecting CV payload...", "warning")
            await asyncio.sleep(2)
            
            await manager.broadcast(f"[{platform}] Validating form and applying...", "system")
            await asyncio.sleep(2)
            
            await manager.broadcast(f"[{platform}] Form submitted successfully.", "success")
            await asyncio.sleep(1)
        
        driver.quit()
        await manager.broadcast("SEQUENCE COMPLETE. HYBERNATING...", "system", status="done")

    except Exception as e:
        await manager.broadcast(f"ERROR: {str(e)}", "warning", status="error")

@app.post("/automate")
async def start_automation(req: AutomationRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(automation_task, req.keywords)
    return {"message": "Automation started"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
