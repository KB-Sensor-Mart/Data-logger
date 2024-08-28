from fastapi import FastAPI, WebSocket, Request, HTTPException, WebSocketDisconnect, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sensor_data.data_reader import SensorDataReader, LogWriter
from network.ipmanager import NetworkConfigurator
import asyncio
import logging
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
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
       
@app.get("/ip/", response_class=HTMLResponse)
async def get_form():
    return """
    <html>
        <body>
            <h2>Change Raspberry Pi IP Address</h2>
            <form action="/change-ip" method="post">
                <label for="ip_address">New IP Address:</label><br>
                <input type="text" id="ip_address" name="ip_address" placeholder="e.g., 192.168.31.86"><br><br>
                <label for="routers">Router:</label><br>
                <input type="text" id="routers" name="routers" placeholder="e.g., 192.168.31.1"><br><br>
                <label for="dns_servers">DNS Servers:</label><br>
                <input type="text" id="dns_servers" name="dns_servers" placeholder="e.g., 255.255.0.0"><br><br>
                <input type="submit" value="Submit">
            </form> 
        </body>
    </html>
    """

@app.post("/change-ip/")
async def change_ip(ip_address: str = Form(...), routers: str = Form(...), dns_servers: str = Form(...)):
    configurator = NetworkConfigurator("eth0")
    configurator.backup_config()
    configurator.change_ip_address(ip_address, routers, dns_servers)
    return {"message": "IP address changed successfully!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
