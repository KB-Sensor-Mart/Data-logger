from fastapi import FastAPI, WebSocket, Request, HTTPException, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sensor_data.data_reader import SensorDataReader, LogWriter
from core.schemas import FTPSettings, FTPCredentialUpdate, IPChangeRequest
from core.utils import check_ftp_connection, start_ftp_upload, download_files, update_ftp_credentials, get_data, websocket_endpoint,update_sensor_data,change_ip
from network.ipmanager import NetworkConfigurator
from ftp.ftp_handler import FTPHandler
import asyncio
import logging


logger = logging.getLogger(__name__)

app = FastAPI()

            
templates = Jinja2Templates(directory="templates")

# Initialize the log writer
log_writer = LogWriter(log_filename="log.csv")

# Initialize the sensor data reader
sensor_data_reader = SensorDataReader(
    port='/dev/ttyAMA2',
    baud_rate=115200,
    queue_size=1000,
    log_writer=log_writer,
    csv_filename_prefix=" ",
    sr_no_limit=29999
)
# Initialize the FTP handler with default settings
ftp_uploader =None

# ---------- HTML "/" and "/ftp" Routes ----------
@app.get("/", response_class=HTMLResponse)
async def get_webpage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/ftp", response_class=HTMLResponse)
async def ftp_page(request: Request):
    return templates.TemplateResponse("ftp.html", {"request": request}) 

# ---------- FTP Routes ----------
@app.post("/update_ftp_credentials")
async def update_ftp_credentials_route(creds: FTPCredentialUpdate):
    return await update_ftp_credentials(creds)

@app.post("/start_ftp_upload")
async def start_ftp_upload_route():
    return await start_ftp_upload()

@app.get("/check_ftp_connection")
async def check_ftp_connection_route():
    return await check_ftp_connection()

# ---------- Download files Routes ----------
@app.get ("/download_data")
async def download_data_route(date: str, start_time: str, end_time: str):
    return await download_files(date,start_time,end_time)

# ---------- Data Routes ----------
@app.get("/data")
async def get_data_route():
    return get_data()

@app.post("/data")
async def post_data_route(data: SensorData):
    return update_sensor_data

# ---------- Websocket Routes ----------
@app.websocket("/ws")
async def websocket_routes(websocket: WebSocket):
    return websocket_endpoint()

# ---------- IP  Routes ----------
@app.post("/ip")
async def post_ip_config():
    return change_ip()


