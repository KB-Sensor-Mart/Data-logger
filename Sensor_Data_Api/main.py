from fastapi import FastAPI, WebSocket, Request, HTTPException, WebSocketDisconnect, Form
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sensor_data.data_reader import SensorDataReader, LogWriter
from sensor_data.data_reader import FilesDownloading
import asyncio
import logging
import os
from datetime import datetime
import zipfile
import traceback
import io
import threading
import uvicorn
from pydantic import BaseModel
from contextlib import asynccontextmanager
from network.ipmanager import NetworkConfigurator  #importing the ip change configurations
from ftp.ftp_handler import FTPHandler
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

#path where data is stored
BASE_FOLDER ="/home/admin/Data-logger/Sensor_Data_Api/data/"

#this is the cors that is used in editing the ip 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],#here * means that all the ip are accessable
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
                
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

class FTPSettings(BaseModel):
    host: str
    port: int
    username: str
    password: str
    remote_path: str
    log_file: str = "uploaded_files_log.json"
    retries: int = 3
    
class NewFileHandler(FileSystemEventHandler):
		def on_created(self, event):
			if not event.is_directory and ftp_connection_established:
				logging.info(f"New file detected: { event.srv_path}")
				#autometically upload new file to ftp server 
				try:
					ftp_uploader.upload_file(event.src_path)
					logging.info(f"File{event.src_path} uploaded to ftp successfully.")
				except Exception as e:
					logging.error(f"Failed to upload file {event.src_path} to FTP: {e}")
		
#start observing base directory for new files 
def start_observing_directory():
	event_handler = NewFileHandler()
	observer = Observer()
	observer.schedule(event_handler, BASE_FOLDER, recursive =False)
	observer.start()
			
	#keep observing in seperate thread
	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		observer.stop()
	observer.join()					
				
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event: Start the data reading threads (Already started in SensorDataReader)
    yield
    # Shutdown event: Ensure proper shutdown of threads and closing of CSV file
    sensor_data_reader.stop()

app.router.lifespan = lifespan

@app.get("/", response_class=HTMLResponse)
async def get_webpage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/ftp", response_class=HTMLResponse)
async def ftp_page(request: Request):
    return templates.TemplateResponse("ftp.html", {"request": request}) 
  

@app.post("/update_ftp_credentials/")
async def update_ftp_credentials(
    host: str = Form(...),
    port: int = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    remote_path: str = Form(...)
):
    global ftp_uploader
    try:
        ftp_uploader = FTPHandler(
            host=host,
            port=port,
            username=username,
            password=password,
            remote_path=remote_path,
            log_file='./log/uploaded_files_log.json',
            retries=3
        )
        ftp_uploader.connect()
        ftp_connection_established = True
        logging.info("FTP credentials updated and connection established.")
        return {"message": "FTP credentials updated successfully"}
    except Exception as e:
        ftp_connection_established = False
        logging.error(f"Error updating FTP credentials: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@app.post("/start_ftp_upload/")
async def start_ftp_upload():
    global ftp_uploader
    if ftp_uploader is None:
        return JSONResponse(status_code=400, content={"message": "FTP credentials not set. Please set them first."})

    try:
        ftp_uploader.trigger_upload(BASE_FOLDER)
        return {"message": "FTP upload process started successfully"}
    except Exception as e:
        logging.error(f"Error starting FTP upload: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
        
@app.get("/check_ftp_connection")
async def check_ftp_connection():
		global ftp_uploader
		if ftp_uploader is None:
			return JSONResponse(status_code = 400, content ={"message":"FTP credentials  not set"})
		
		try:
			success = ftp_uploader.connect()
			if success:
				return {"message": "Successfully connected to the FTP server."}
			else:
				return {"message": "Failed to connect to the FTP server."}
		except Exception as e:
			logger.error(f"Error in /check_ftp_connection: {e}")
			return JSONResponse(status_code=500, content={"message": f"Failed to connect to the FTP server. Error: {str(e)}"})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established")

    try:
        while True:
            data = sensor_data_reader.get_data()
            if data:
                await websocket.send_json(data)
            await asyncio.sleep(0.1)  # Adjusted sleep time to reduce potential issues
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed by the client")
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        logger.info("Closing WebSocket connection")
        await websocket.close()  # Close the WebSocket connection

@app.get("/data/")
async def get_data():
    try:
        data = sensor_data_reader.get_data()
        if data:
            return JSONResponse(content={"data": data})
        else:
            raise HTTPException(status_code=404, detail="No data available")
    except Exception as e:
        logger.error(f"Error retrieving data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/data/")
async def update_sensor_data(request: Request):
    data = sensor_data_reader.get_data()
    if data:
        return JSONResponse(content={"data": data})
    else:
        raise HTTPException(status_code=404, detail="No data available")
         
@app.get("/download_data")
async def download_files(date: str, start_time: str, end_time: str):
    try:
        # Convert the date from YYYY-MM-DD to DD-MM-YYYY
        formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d-%m-%Y")
        date_folder = os.path.join(BASE_FOLDER, formatted_date)

        # Debug: print the path checked
        print(f"Looking for the files in {date_folder}")

        # Check if directory exists
        if not os.path.exists(date_folder):
            # Debug: print a message if directory is not found
            print(f"Directory not found: {date_folder}")
            raise HTTPException(status_code=404, detail=f"No files found for the date: {formatted_date}")

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # List all files in the directory
            files = os.listdir(date_folder)
            # Debug message: print files found
            print(f"Files found: {files}")

            # Parse the start and end time
            try:
                start_t = datetime.strptime(start_time, "%H:%M").time()
                end_t = datetime.strptime(end_time, "%H:%M").time()
            except ValueError as ve:
                raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM")

            # Add each CSV file to the zip if it falls within the time range
            for file_name in files:
                if file_name.endswith('.csv'):
                    file_path = os.path.join(date_folder, file_name)

                    # Extract the time part from file name
                    file_time_str = file_name.split('_')[1][:6]  # Extracting HHMMSS from the filename
                    file_time = datetime.strptime(file_time_str, "%H%M%S").time()

                    # Check if the file time falls within the specified time range
                    if start_t <= file_time <= end_t:
                        print(f"Adding file to zip: {file_path}")
                        try:
                            zip_file.write(file_path, file_name)
                        except Exception as e:
                            # Debug: print exception for file addition
                            print(f"Error adding file to zip: {e}")

        # Move the cursor to the beginning of the buffer
        buffer.seek(0)
        # Return the zip file as a streaming response
        return StreamingResponse(buffer, media_type='application/zip',
                                 headers={"Content-Disposition": f"attachment; filename=files_{formatted_date}.zip"})

    except Exception as e:
        # Debug: print exception message and stack trace
        print(f"Exception occurred: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")
        
            
class IPChangeRequest(BaseModel):
    ip_address: str
    routers: str
    dns_servers: str

@app.post("/ip/")
async def change_ip(request: IPChangeRequest):
    try: 
        configurator = NetworkConfigurator("eth0")
        configurator.backup_config()
        configurator.change_ip_address(request.ip_address, request.routers, request.dns_servers)
        return {"message": "IP address changed successfully!"}
    except Exception as e:
        logger.error(f"Failed to change IP: {e}")
        raise HTTPException(status_code=500, detail="Failed to change IP address")

        
if __name__ == "__main__":
    
	#start directory monetoring in seperate thread
		directory_observer_thread = threading.Thread(target = start_observing_directory)
		directory_observer_thread.daemon =True
		directory_observer_thread.start()

		uvicorn.run(app, host="0.0.0.0", port=8000)

