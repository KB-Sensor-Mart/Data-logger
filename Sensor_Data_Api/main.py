import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.routes import app as core_app  # Import the router from routes.py
from ftp import ftp_app 
from fastapi.staticfiles import StaticFiles
from network.ipmanager import IPSending
from contextlib import asynccontextmanager
import sys
import logging
from sensor_data.ups import router as ups_router, start_sensor_reading, INA219

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define serial port, baud rate, and network interface
serial_port = "/dev/ttyAMA2"
baud_rate = 115200
interface = "eth0"  
ip_sender = IPSending(serial_port,baud_rate,interface)



# Create the FastAPI app with the lifespan handler
app = FastAPI()

# CORS Middleware for allowing external access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(core_app)# Including all routes from the routes.py file
app.include_router(ftp_app)#includinf Ftp routes from ftp
app.include_router(ups_router)# Include UPS routes


if __name__ == "__main__":
    try:
        logging.info("Starting IP sending thread.")
        ip_sender.start_sending_ip()
        start_sensor_reading()
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        logging.info("Received keyboard interrupt.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        ip_sender.stop_sending_ip()
        logging.info("Gracefully shutting down the application.")
        sys.exit(0)  # Exit the program without a traceback
