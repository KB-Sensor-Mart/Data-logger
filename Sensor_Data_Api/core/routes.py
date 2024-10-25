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
                       process_reset_password,
                       shutdown)
from network.ipmanager import NetworkConfigurator
import asyncio
from logging_config import get_logger
from gps import start_gps_reader,send_gps_data_via_websocket

logger = get_logger(__name__)

app = APIRouter()

start_gps_reader()

templates = Jinja2Templates(directory="templates")


# ---------- HTML "/" and "/ftp" Routes ----------
@app.get("/", response_class=HTMLResponse)
async def get_webpage(request: Request):
    logger.info("Rendering index.html for / route")
    return templates.TemplateResponse("index.html", {"request": request})
    
@app.get("/gps", response_class=HTMLResponse)
async def get():
    logger.info("Rendering gps.html for /gps route")
    return templates.TemplateResponse("gps.html", {"request": {}})

@app.get("/ftp", response_class=HTMLResponse)
async def ftp_page(request: Request):
    logger.info("Rendering ftp.html for /ftp route")
    return templates.TemplateResponse("ftp.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    logger.info("Rendering login.html for /login route")
    return templates.TemplateResponse("login.html", {"request": request, "action": "login"})

@app.get("/reset-password", response_class=HTMLResponse)
async def reset_password_form(request: Request):
    logger.info("Rendering resetpassword.html for /reset-password route")
    return templates.TemplateResponse("resetpassword.html", {"request": request, "action": "reset"})

#----------------------gps_routes ---------------------------
@app.websocket("/ws/gps")
async def websocket_routes(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection accepted for /ws/gps")
    try:
        await send_gps_data_via_websocket(websocket)  # Send GPS data via WebSocket
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for /ws/gps")

# ---------- Login page routes ----------
@app.post("/login")
async def login(request: Request, form_data: LoginRequest):
    logger.info("Handling login request")
    try:
        data = await request.json()  # Parsing the incoming JSON data
        success, message = await process_login(data['username'], data['password'])
        if not success:
            logger.warning("Login failed for user: %s", data['username'])
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)
        logger.info("Login successful for user: %s", data['username'])
        return JSONResponse(content={"message": "Login successful"})
    except Exception as e:
        logger.error("Error during login: %s", e)
        raise e

# JSON-based reset password request (POST)
@app.post("/reset-password")
async def reset_password(request: Request, form_data: ResetPasswordRequest):
    logger.info("Handling reset password request")
    try:
        data = await request.json()  # Parsing the incoming JSON data
        success, message = await process_reset_password(data['username'], data['new_password'])
        if not success:
            logger.warning("Password reset failed for user: %s", data['username'])
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
        logger.info("Password reset successful for user: %s", data['username'])
        return JSONResponse(content={"message": "Password reset successful"})
    except Exception as e:
        logger.error("Error during password reset: %s", e)
        raise e
    
# ---------- Download files Routes ----------
@app.get("/download_data")
async def download_data_route(date: str, start_time: str, end_time: str):
    logger.info("Download data request received: Date: %s, Start Time: %s, End Time: %s", date, start_time, end_time)
    return await download_files(date, start_time, end_time)

# ---------- Data Routes ----------
@app.get("/data")
async def get_data_route():
    logger.info("Get data request received")
    return await get_data()

@app.post("/data")
async def post_data_route(data: SensorData):
    logger.info("Post data request received with data: %s", data)
    return await update_sensor_data()

# ---------- WebSocket Route ----------
@app.websocket("/ws")
async def websocket_routes(websocket: WebSocket):
    logger.info("WebSocket connection accepted for /ws")
    return await websocket_endpoint(websocket)

# ---------- IP Routes ----------
@app.post("/ip")
async def post_ip_config(request: IPChangeRequest):
    logger.info("IP configuration request received")
    return await change_ip(request)

# ---------- Shut down route ----------
@app.post("/shutdown")
async def shutdown_device():
    logger.info("Shutdown request received")
    return await shutdown()