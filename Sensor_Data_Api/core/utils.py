import logging
from ftp.ftp_handler import FTPHandler
import os
import asyncio
import traceback
import io
from fastapi import Request
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from fastapi import HTTPException,WebSocket,FastAPI,WebSocketDisconnect
from io import BytesIO
import zipfile
import time 
from datetime import datetime
from fastapi.responses import StreamingResponse,JSONResponse
from sensor_data.data_reader import SensorDataReader,LogWriter
from login.login import auth_service
from core.schemas import IPChangeRequest,SensorData,FTPCredentialUpdate
from network.ipmanager import NetworkConfigurator
from typing import Tuple

logger = logging.getLogger(__name__)

#checking the initial value of timer 
#start_time = None
upload_interval_time = 10

BASE_FOLDER = "/home/admin/Data-logger/Sensor_Data_Api/data/"

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
ftp_uploader = None
# ---------------- Timer logic-----------
'''async def timer():
	global start_time
	if start_time is None:
		start_time = time.time()
	while True:
		current_time = time.time() - start_time
		print(f"\rTime: {int(current_time)}seconds",end = '')
		await asyncio.sleep(1)
'''
#----------------FTP Logic ----------------------

async def update_ftp_credentials(creds: FTPCredentialUpdate):
    global ftp_uploader
    try:
        ftp_uploader = FTPHandler(
            host=creds.host,
            port=creds.port,
            username=creds.username,
            password=creds.password,
            remote_path=creds.remote_path,
            log_file='./log/uploaded_files_log.json',
            retries=3
        )
        ftp_uploader.connect()
        logging.info("FTP credentials updated and connection erstablished")
        return {"message": "FTP credentials updated successfully"}
    except Exception as e:
        logger.error(f"Error updating FTP credentials: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def start_ftp_upload():
    global ftp_uploader
    global upload_interval_time
    
    if ftp_uploader is None:
        return {"message": "FTP credentials not set"}
    while True:
        try:
			#scan and upload files
            logger.debug("starting ftp scan and upload")
            await ftp_uploader.scan_and_upload(BASE_FOLDER)
            logger.debug(f"Waiting for {upload_interval_time} seconds befor next upload")
            #wait for specific time interval
            await asyncio.sleep(upload_interval_time)
        except Exception as e:
            logger.error(f"Error starting FTP upload: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

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

async def stop_ftp_process():
	global ftp_uploader
	if ftp_uploader is None:
		return{"message": "No FTP process to stop"}
	try:
		#calling upp the disconnect function of FTPHandler
		ftp_uploader.disconnect()
		logging.info("FTP process stopped successfully")
		return{"message": "FTP process stopped succesfully"}
	except Exception as e:
		#Log the error and return an HTTP error response
		logging.error(f"Error stopping FTP process: {e}")
		return JSONResponse(status_code = 500, content = {"message": "Failed to stop FTP"})


class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            logger.info(f"New file detected: {event.src_path}")
            try:
                ftp_uploader.upload_file(event.src_path)
                logger.info(f"File {event.src_path} uploaded successfully.")
            except Exception as e:
                logger.error(f"Failed to upload file {event.src_path}: {e}")


def start_observing_directory():
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, BASE_FOLDER, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

#----------------Login logic --------------------
async def process_login(username: str, password: str) -> tuple[bool, str]:
    try:
        return auth_service.login(username, password)
    except Exception as e:
        # Log error
        logger.error(f"Login failed: {e}")
        return False, "An error occurred during login"

async def process_reset_password(username: str, new_password: str) -> tuple[bool, str]:
    try:
        return auth_service.reset_password(username, new_password)
    except Exception as e:
        logger.error(f"Password reset failed: {e}")
        return False, "An error occurred during password reset"
        

#----------------Download file Logic ----------------------
async def download_files(date, start_time, end_time):
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

#----------------Websocket Logic ----------------------
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
        if websocket.client_state == 1:
            logger.info("Closing WebSocket connection")
            await websocket.close()  # Close the WebSocket connection
            
#----------------Get Data Logic ----------------------
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
    
#----------------post Data Logic ----------------------
async def update_sensor_data(data: SensorData):
    data = sensor_data_reader.get_data()
    if data:
        return JSONResponse(content={"data": data})
    else:
        raise HTTPException(status_code=404, detail="No data available")
   
#----------------change IP Logic ----------------------
async def change_ip(request: IPChangeRequest):
    try: 
        configurator = NetworkConfigurator("eth0")
        configurator.backup_config()
        configurator.change_ip_address(request.ip_address, request.routers, request.dns_servers)
        return {"message": "IP address changed successfully!"}
    except Exception as e:
        logger.error(f"Failed to change IP: {e}")
        raise HTTPException(status_code=500, detail="Failed to change IP address")

