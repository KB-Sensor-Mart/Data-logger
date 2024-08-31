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
from pydantic import BaseModel
from contextlib import asynccontextmanager
from network.ipmanager import NetworkConfigurator  #importing the ip change configurations

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
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
