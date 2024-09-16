from fastapi import APIRouter, WebSocket, Request, HTTPException, WebSocketDisconnect, status, FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sensor_data.data_reader import LogWriter
from core.schemas import FTPCredentialUpdate, IPChangeRequest, SensorData, LoginRequest, ResetPasswordRequest
from core.utils import (check_ftp_connection, 
                       start_ftp_upload, 
                       download_files, 
                       update_ftp_credentials, 
                       get_data, 
                       websocket_endpoint,
                       update_sensor_data,
                       change_ip,
                       stop_ftp_process, 
                       process_login, 
                       process_reset_password)
                       #timer)
from network.ipmanager import NetworkConfigurator
from ftp.ftp_handler import FTPHandler
import asyncio
import logging




logger = logging.getLogger(__name__)

app = APIRouter()
templates = Jinja2Templates(directory="templates")

# Initialize the FTP handler with default settings
ftp_uploader =None

timer_task = None
ftp_upload_task = None
# ---------- HTML "/" and "/ftp" Routes ----------
@app.get("/", response_class=HTMLResponse)
async def get_webpage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/ftp", response_class=HTMLResponse)
async def ftp_page(request: Request):
    return templates.TemplateResponse("ftp.html", {"request": request}) 
    
@app.get("/login",response_class = HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html" ,{"request": request, "action": "login"})

@app.get("/reset-password", response_class=HTMLResponse)
async def reset_password_form(request: Request):
    return templates.TemplateResponse("resetpassword.html", {"request": request, "action": "reset"})


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
    
    
#------------ Timer ----------------
@app.get("/timer")
async def start_timer():
	global timer_task
	if timer_task is None or timer_task.done():
		print("timer started ")
	timer_task = asyncio.create_task(timer())
	return{"message": "timer running in background{timer_task}"}

# ---------- FTP Routes ----------
@app.post("/update_ftp_credentials")
async def update_ftp_credentials_route(creds: FTPCredentialUpdate):
    try:
        # Call the FTP update logic
        response = await update_ftp_credentials(creds)
        return response
    except HTTPException as http_err:
        # If an HTTPException occurs, return the error message
        return {"message": f"Error updating credentials: {http_err.detail}"}
    except Exception as e:
        # Catch all other exceptions and return a generic error message
        return {"message": f"An unexpected error occurred: {str(e)}"}

@app.post("/start_ftp_upload")
async def start_ftp_upload_route():
	global ftp_upload_task 
	if ftp_upload_task is None or ftp_upload_task.done():
		ftp_upload_task=asyncio.create_task(start_ftp_upload())
		return{"message":"periodic ftp upload started"}
	return{"message":"preodic ftp upload is already running"}

@app.get("/check_ftp_connection")
async def check_ftp_connection_route():
    return await check_ftp_connection()
    
@app.post("/stop_ftp_process")
async def stop_ftp_process_route():
	global ftp_upload_task
	if ftp_upload_task:
		ftp_upload_task.cancle() #this stops  periodic upload task
		return{"message":"periodic ftp upload stopped"}
	return{"message":"no ftp process to stop"}

    #response = await stop_ftp_process()


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


