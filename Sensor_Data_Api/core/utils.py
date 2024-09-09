import logging
from ftp.ftp_handler import FTPHandler
import os
import time
import traceback
import io
import Request
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from fastapi import HTTPException,WebSocket,FastAPI
from io import BytesIO
import zipfile
from datetime import datetime
from fastapi.responses import StreamingResponse,JSONResponse
from sensor_data.data_reader import SensorDataReader

logger = logging.getLogger(__name__)

BASE_FOLDER = "/home/admin/Data-logger/Sensor_Data_Api/data/"

ftp_uploader = None

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


#----------------FTP Logic ----------------------
async def update_ftp_credentials(creds):
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
        return {"message": "FTP credentials updated successfully"}
    except Exception as e:
        logger.error(f"Error updating FTP credentials: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def start_ftp_upload():
    global ftp_uploader
    if ftp_uploader is None:
        return {"message": "FTP credentials not set"}
    try:
        ftp_uploader.trigger_upload(BASE_FOLDER)
        return {"message": "FTP upload started"}
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
async def update_sensor_data(request: Request):
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

         