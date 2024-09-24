from fastapi import APIRouter, WebSocket, Request, HTTPException, WebSocketDisconnect, status, FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sensor_data.data_reader import LogWriter
from core.schemas import FTPCredentialUpdate, IPChangeRequest, SensorData, LoginRequest, ResetPasswordRequest
from core.utils import (download_files,  
                       get_data, 
                       websocket_endpoint,
                       update_sensor_data,
                       change_ip,
                       process_login, 
                       process_reset_password)
from network.ipmanager import NetworkConfigurator
import asyncio
import logging
from gps import start_gps_reader,send_gps_data_via_websocket




logger = logging.getLogger(__name__)

app = APIRouter()

start_gps_reader()

templates = Jinja2Templates(directory="templates")


# ---------- HTML "/" and "/ftp" Routes ----------
@app.get("/", response_class=HTMLResponse)
async def get_webpage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
    
@app.get("/gps", response_class=HTMLResponse)
async def get():
    #print("DEBUG: rendring index.html")
    return templates.TemplateResponse("gps.html", {"request": {}})

@app.get("/ftp", response_class=HTMLResponse)
async def ftp_page(request: Request):
    return templates.TemplateResponse("ftp.html", {"request": request}) 
    
@app.get("/login",response_class = HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html" ,{"request": request, "action": "login"})

@app.get("/reset-password", response_class=HTMLResponse)
async def reset_password_form(request: Request):
    return templates.TemplateResponse("resetpassword.html", {"request": request, "action": "reset"})

#----------------------gps_routes ---------------------------
@app.websocket("/ws/gps")
async def websocket_routes(websocket: WebSocket):
	await websocket.accept()
	try:
		await send_gps_data_via_websocket(websocket)  # Send GPS data via WebSocket
	except WebSocketDisconnect:
		logger.info("WebSocket disconnected")
		
# ---------- Login page routes ----------
@app.post("/login")
async def login(request: Request, form_data: LoginRequest):
    data = await request.json()  # Parsing the incoming JSON data
    success, message = await process_login(data['username'], data['password'])
    if not success:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)
    return JSONResponse(content={"message": "Login successful"})

# JSON-based reset password request (POST)
@app.post("/reset-password")
async def reset_password(request: Request, form_data: ResetPasswordRequest):
    data = await request.json()  # Parsing the incoming JSON data
    success, message = await process_reset_password(data['username'], data['new_password'])
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return JSONResponse(content={"message": "Password reset successful"})

    
# ---------- Download files Routes ----------
@app.get ("/download_data")
async def download_data_route(date: str, start_time: str, end_time: str):
    return await download_files(date,start_time,end_time)

# ---------- Data Routes ----------
@app.get("/data")
async def get_data_route():
    return await get_data()

@app.post("/data")
async def post_data_route(data: SensorData):
    return await update_sensor_data()

# ---------- Websocket Routes ----------
@app.websocket("/ws")
async def websocket_routes(websocket: WebSocket):
    return await websocket_endpoint(websocket)

# ---------- IP  Routes ----------
@app.post("/ip")
async def post_ip_config(request: IPChangeRequest):
    return await change_ip(request)

