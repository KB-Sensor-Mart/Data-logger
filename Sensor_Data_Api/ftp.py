from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request,APIRouter
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from io import BytesIO
import aioftp
import uvicorn
import logging
import os
import asyncio
from logging_config import setup_logging
#continopusly scanning the files 
import threading 
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time


#ftp_app = FastAPI()
ftp_app = APIRouter()

# In-memory storage for FTP credentials
ftp_credentials = {}
upload_folder = "/home/admin/Data-logger/Sensor_Data_Api/data"

upload_task = None  # To store the ongoing upload task
stop_flag = False  # A flag to stop the upload process

#watchdog
watchdog_active = False  # Flag to check if watchdog is running
observer = None  # To manage watchdog observer

# Configure logging
# Set up logging
logger = setup_logging()

upload_interval_time = 301
# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Pydantic model for FTP credentials
class FTPCredentials(BaseModel):
    host: str
    port: int
    username: str
    password: str

   
#watchdog event handler class to detect new files
class NewFileHandler(FileSystemEventHandler):
    def __init__(self, client, remote_dir, event_loop):
        self.client = client
        self.remote_dir = remote_dir
        self.event_loop = event_loop
        
        
    def on_created(self, event):
        global upload_interval_time
        print(f"DEBUG: New file detected in on_created: {event.src_path}")
        if not event.is_directory:
            # If a new file is created, upload it to the FTP server
            logger.info(f"New file detected: {event.src_path}")
            print(f"DEBUG: Sheduling uplaod for new file :{event.src_path}")
            
            
            
            timer = threading.Timer(upload_interval_time, self.function_to_upload_new_file, args=[event.src_path])
            timer.start()
    
    def function_to_upload_new_file(self, file_path):
        print(f"DEBUG: Uploading file in function_to_upload: {file_path}")
        asyncio.run_coroutine_threadsafe(self.upload_new_file(file_path), self.event_loop)
        print(f"DEBUG: Upload completed for file: {file_path}")
    
    async def upload_new_file(self, local_path):
        if not await connect_to_ftp(self.client):
            return
        
        try:
            remote_path = self.remote_dir + local_path[len(upload_folder):local_path.rindex('/')]
            print(f"DEBUG: remote path generated- {remote_path}")
            logger.info(f"Uploading new file: {local_path} to {remote_path}")
            await self.client.upload(local_path, remote_path)
        except Exception as e:
            logger.error(f"Failed to upload file: {local_path}. Error: {e}")
            print(f"Failed to upload file: {local_path}. Error: {e}")
            

# Function to connect to the FTP server with retry logic
async def connect_to_ftp(client, retries=5, delay=5):
    for attempt in range(retries):
        try:
            await client.connect(
                ftp_credentials['host'],
                port=ftp_credentials['port']
            )
            await client.login(
                ftp_credentials['username'],
                ftp_credentials['password']
            )
            return True
        except Exception as e:
            logger.error(f"Connection attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(delay)
    return False
            
# Route to render the HTML form
@ftp_app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

# Route to handle the upload of FTP credentials
@ftp_app.post("/ftp/upload_credentials")
async def upload_ftp_credentials(
    host: str = Form(...),
    port: int = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    remotepath: str = Form(...)
):
    try:
        ftp_credentials['host'] = host.strip()
        ftp_credentials['port'] = port
        ftp_credentials['username'] = username
        ftp_credentials['password'] = password
        ftp_credentials['remotepath'] = remotepath
        return {"message": "FTP credentials uploaded successfully"}
    except Exception as e:
        logger.error(f"Error uploading FTP credentials: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload FTP credentials")

# Route to fetch the current FTP credentials
@ftp_app.get("/ftp/get_credentials")
async def get_ftp_credentials():
    if not ftp_credentials:
        raise HTTPException(status_code=404, detail="FTP credentials not found")
    return ftp_credentials

# Route to check the connection to the FTP server

@ftp_app.get("/ftp/check_connection")
async def check_connection():
    if not ftp_credentials:
        raise HTTPException(status_code=400, detail="FTP credentials not set")
    
    try:
        print(f"DEBUG: attempting to connect with credentials: {ftp_credentials}")
        # Test connection to the FTP server
        client = aioftp.Client()
        await client.connect(
            ftp_credentials['host'],
            port=ftp_credentials['port']
        )
        await client.login(
            ftp_credentials['username'],
            ftp_credentials['password']
        )
        await client.quit()  # Disconnect after checking the connection
        print("DEBUG: connected to ftp")
        return {"message": "Connection to FTP server successful"}
    
    except Exception as e:  # Catch all exceptions
        # Log the error
        logger.error(f"Error connecting to FTP server: {str(e)}")
        print(f"DEBUG: Error connecting to ftp server: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to connect to FTP server")



# Route to upload a file to the FTP server
@ftp_app.post("/ftp/upload_folder")
async def upload_files_to_ftp():
    global upload_task, stop_flag,watchdog_active,observer
    stop_flag =False
    watchdog_active = True

    local_folder = upload_folder  

    if not ftp_credentials:
        raise HTTPException(status_code=400, detail="FTP credentials not provided")
    if not upload_folder:
        raise HTTPException(status_code=400,detail="Folder Path not provided")

    client = aioftp.Client()
    try:
        if not await connect_to_ftp(client):
            return   
        upload_task = asyncio.create_task(upload_directory_recursive(client, upload_folder, ftp_credentials['remotepath']))
        print("DEBUG: files started getting uploading")
        
        #once files are uploaded , setup watchdog to monitor 
        await upload_task #wait for upload to finish
        print("DEBUG: upload task completed")
        
        if observer is None:
            print("DEBUG: initializing observer")
            loop = asyncio.get_event_loop() 
            event_handler = NewFileHandler(client, ftp_credentials['remotepath'],loop)
            observer = Observer()
            observer.schedule(event_handler, upload_folder, recursive=True)
            observer_thread = threading.Thread(target = observer.start)
            observer_thread.start()
            logger.info(f"Started observing folder: {upload_folder} for new files")
            print(f"Observer started for folder: {upload_folder}")
            
        return {"message": "All files uploaded and observing for new files"}

    except Exception as e:
        logger.error(f"Upload error: {e}")
        return {"message": f"Upload failed: {e}"}

async def upload_directory_recursive(client, local_dir, remote_dir):
    global stop_flag
    # Ensure remote directory exists
    await client.make_directory(remote_dir)
    await client.change_directory(remote_dir)

    for entry in os.listdir(local_dir):
        if stop_flag:
            print("Upload stopped by user.")
            await client.quit()
            return  # Stop the upload process
        
        local_path = os.path.join(local_dir, entry)

        if os.path.isdir(local_path):
            # Recursively upload subdirectories
            print(f"DEBUG: procesing directory :{local_path}")
            try:
                remote_path = os.path.join(remote_dir, entry).replace(os.path.sep, '/')
                logger.info(f"Creating remote directory: {remote_path}")
                await client.make_directory(remote_path)
            except aioftp.errors.StatusCodeError:
                # Directory likely already exists, move on
                pass
            await upload_directory_recursive(client, local_path, remote_path)

        elif os.path.isfile(local_path):
            print(f"Uploading file: {local_path}")
            # Upload files directly into the remote directory
            logger.info(f"Uploading file: {local_path} to {remote_dir}")
            await client.upload(local_path,remote_dir)



@ftp_app.post("/ftp/stop_upload")
async def stop_upload():
    global stop_flag, upload_task, watchdog_active , observer

    stop_flag = True  # Set the stop flag to True, which will be checked during the upload

    if upload_task:
        print("DEBUG: Stopping upload task")
        await upload_task  # Wait for the task to stop
        upload_task = None
        
    if watchdog_active and observer:
        print("DEBUG: Stopping observer")
        observer.stop()
        observer.join()
        observer = None
        watchdog_active = False
        logger.info("Stopped observing folder for new files")
     
    return {"message": "Stopped file uploading and folder monitoring"}
 