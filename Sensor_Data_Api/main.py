from fastapi import FastAPI, WebSocket, Request, HTTPException, WebSocketDisconnect, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sensor_data.data_reader import SensorDataReader, LogWriter
import asyncio
import logging
from pydantic import BaseModel
from contextlib import asynccontextmanager
from network.ipmanager import NetworkConfigurator  #importing the ip change configurations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

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
