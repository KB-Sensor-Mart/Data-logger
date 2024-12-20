import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.routes import app as core_app  # Import the router from routes.py
from ftp import ftp_app 
from fastapi.staticfiles import StaticFiles
#from network.ipmanager import IPSending
from contextlib import asynccontextmanager
import sys
from sensor_data.ups import router as ups_router, start_sensor_reading, INA219, read_sensor_data
from logging_config import get_logger
import asyncio

# Configure logging
logger = get_logger(__name__)

# Define serial port, baud rate, and network interface
serial_port = "/dev/ttyAMA2"
baud_rate = 115200
interface = "eth0"  
#ip_sender = IPSending(serial_port,baud_rate,interface)



# Create the FastAPI app with the lifespan handler
app = FastAPI()

# CORS Middleware for allowing external access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://enginx1-anshuman1.in1.pitunnel.net" , "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(core_app)# Including all routes from the routes.py file
app.include_router(ftp_app)#includinf Ftp routes from ftp
app.include_router(ups_router)# Include UPS routes


if __name__ == "__main__":
    try:
        #logger.info("Starting IP sending thread.")
        #ip_sender.start_sending_ip()
        start_sensor_reading()
        uvicorn.run(app, host="0.0.0.0", port=8000)
        logger.info("fast api server started")
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        #ip_sender.stop_sending_ip()
        logger.info("Gracefully shutting down the application.")
        sys.exit(0)  # Exit the program without a traceback
