from logging_config import get_logger
import os
import asyncio
import traceback
import io
from fastapi import Request
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from fastapi import HTTPException,WebSocket,FastAPI,WebSocketDisconnect, BackgroundTasks
from io import BytesIO
import zipfile
import time 
from datetime import datetime
from fastapi.responses import StreamingResponse,JSONResponse
from sensor_data.data_reader import SensorDataReader,LogWriter,mqtt_client,mqtt_topic
from login.login import auth_service
from core.schemas import IPChangeRequest,SensorData,FTPCredentialUpdate
from network.ipmanager import NetworkConfigurator
from typing import Tuple
import subprocess

logger = get_logger(__name__)

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
    queue_size=5000,
    log_writer=log_writer,
    csv_filename_prefix=" ",
    sr_no_limit=29999,
    #mqtt_client=mqtt_client,
    #mqtt_topic=mqtt_topic
)

#----------------Login logic --------------------
async def process_login(username: str, password: str) -> tuple[bool, str, str, datetime]:
    try:
        success, message, session_key,expiry_time = auth_service.login(username, password)
        if not success:
            return success, message, None
        return success, message, session_key,expiry_time
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return False, "An error occurred during login", None,None

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
        logger.info(f"Looking for the files in {date_folder}")

        # Check if directory exists
        if not os.path.exists(date_folder):
            # Debug: print a message if directory is not found
            logger.info(f"Directory not found: {date_folder}")
            raise HTTPException(status_code=404, detail=f"No files found for the date: {formatted_date}")

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # List all files in the directory
            files = os.listdir(date_folder)
            # Debug message: print files found
            logger.info(f"Files found: {files}")

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
                        logger.info(f"Adding file to zip: {file_path}")
                        try:
                            zip_file.write(file_path, file_name)
                        except Exception as e:
                            # Debug: print exception for file addition
                            logger.error(f"Error adding file to zip: {e}")

        # Move the cursor to the beginning of the buffer
        buffer.seek(0)
        # Return the zip file as a streaming response
        return StreamingResponse(buffer, media_type='application/zip',
                                 headers={"Content-Disposition": f"attachment; filename=files_{formatted_date}.zip"})

    except Exception as e:
        # Debug: print exception message and stack trace
        logger.error(f"Exception occurred: {e}")
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

#-----------------Shut down the system logic-----------------------
async def shutdown():
    """Shut down the Raspberry Pi."""
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, subprocess.run, ["sudo", "shutdown", "now"])
        return {"message": "Shutdown command issued."}
    except Exception as e:
        return {"error": str(e)}
