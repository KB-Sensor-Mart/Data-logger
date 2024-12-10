from fastapi import APIRouter, WebSocket, Request, HTTPException, WebSocketDisconnect, status, FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sensor_data.data_reader import LogWriter,DataStatusChecker
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
from typing import Dict
from sensor_data.device_info import DeviceInfo, StorageInfo

logger = get_logger(__name__)

app = APIRouter()

start_gps_reader()

storage_info = StorageInfo()

device_info = DeviceInfo()

data_status_checker = DataStatusChecker(base_folder="data")

templates = Jinja2Templates(directory="templates")

#-----------route to send the storgae info ---------
# WebSocket route for real-time storage updates
@app.websocket("/ws/storage")
async def websocket_storage_status(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            storage_status = storage_info.get_storage_status()  # Fetch real-time storage info
            await websocket.send_json(storage_status) 
            await asyncio.sleep(5)  
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed.")

@app.get("/api/storage_status", response_class=JSONResponse)
async def get_storage_status():
    storage_status = storage_info.get_storage_status()
    return {"storage_status": storage_status}

#-----------route of sending device id--------------

@app.get("/api/device_id",response_class=JSONResponse)
async def get_device_id():
    device_id = device_info.get_device_id()
    return{"device_id":device_id}

#-----------Files data Status ----------------------
@app.get("/api/date_status")
async def get_date_status() -> Dict[str, str]:
    status = data_status_checker.get_date_status()
    return status
    
@app.websocket("/ws/date_status")
async def websocket_date_status(websocket: WebSocket):
    await websocket.accept()
    try:
        previous_status = {}
        while True:
            # Get the current status
            current_status = data_status_checker.get_date_status()
            # Compare with previous status to detect changes
            if current_status != previous_status:
                await websocket.send_json(current_status)
                previous_status = current_status
            # Sleep for a bit to avoid high CPU usage
            await asyncio.sleep(5)

    except Exception as e:
        print(f"WebSocket connection closed: {e}")
    finally:
        await websocket.close()

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
@app.post("/api/login")
async def login(request: Request, form_data: LoginRequest):
    logger.info("Handling login request")
    try:
        data = await request.json()
        success, message, session_key, expiry_time = await process_login(data['username'], data['password'])
        if not success:
            logger.warning("Login failed for user: %s", data['username'])
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)

        logger.info("Login successful for user: %s", data['username'])
        return JSONResponse(content={
            "message": "Login successful",
            "token": session_key,
            "expiryTime": expiry_time.isoformat()  # Include expiry time in response
        })
    except Exception as e:
        logger.error("Error during login: %s", e)
        raise HTTPException(status_code=500, detail="An error occurred during login")


# JSON-based reset password request (POST)
@app.post("/api/reset-password")
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
@app.get("/api/download_data")
async def download_data_route(date: str, start_time: str, end_time: str):
    logger.info("Download data request received: Date: %s, Start Time: %s, End Time: %s", date, start_time, end_time)
    return await download_files(date, start_time, end_time)

# ---------- Data Routes ----------
@app.get("/api/data")
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
@app.post("/api/ip")
async def post_ip_config(request: IPChangeRequest):
    logger.info("IP configuration request received")
    return await change_ip(request)

# ---------- Shut down route ----------
@app.post("/api/shutdown")
async def shutdown_device():
    logger.info("Shutdown request received")
    return await shutdown()
