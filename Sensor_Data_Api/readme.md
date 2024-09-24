# Sensor Data API - Python FastAPI Backend

## Project Overview
This project is a FastAPI-based backend application designed to perform the following functionalities:
1. **User Login** - Authenticate users using a secure login system.
2. **Reset Password** - Enable users to reset their password.
3. **Send Data to Server via WebSocket** - Real-time data transmission to the server through WebSocket.
4. **FTP Commands** - Upload and manage files using FTP.
5. **File Download via Ethernet** - Download files over Ethernet.
6. **GPS Readings** - Collect and display GPS readings.
7. **Graph Plotting** - Use JavaScript on the frontend to plot graphs based on collected data.
8. **IP Address Management** - Change the Raspberry Pi IP address from the web interface.

--------------------------------------------------------------------
## Project Structure
`````````````````````````````````````````````````````````````````````
Sensor_Data_Api/
│
├── main.py            # Entry point of the application
│
├── core/              # Core components for routing, schemas, and utilities
│    ├── __init__.py
│    ├── routes.py     # All API routes (except FTP-related routes)
│    ├── schemas.py    # Data models and schemas
│    └── utils.py      # Utility functions
│
├── login/             # User login and authentication logic
│    ├── __init__.py
│    ├── dbconfig.py   # Database configuration
│    └── login.py      # Login and password reset functionality
│
├── network/           # Network-related functions
│    ├── __init__.py
│    └── ipmanager.py  # IP address management
│
├── sensor_data/       # Sensor data reading and handling
│    ├── __init__.py
│    └── data_reader.py
│
├── static/            # Static files (JavaScript, CSS)
│    └── script.js
│
├── templates/         # HTML templates for the frontend
│    ├── __init__.py
│    ├── index.html    # Main dashboard page
│    ├── ftp.html      # FTP file upload/download page
│    ├── gps.html      # GPS readings display page
│    ├── login.html    # User login page
│    └── resetpassword.html  # Reset password page
│
├── ftp.py             # FTP-related routes and functionality
│
├── gps.py             # GPS data handling and routes
│
├── logging_config.py  # Application logging configuration
│
├── requirements.txt   # Project dependencies
└── README.md          # Project documentation

``````````````````````````````````````````````````````````````````````


----------------------------
## Setup Instructions
----------------------------

### Pre-requisites
Before starting, ensure you have a properly configured Raspberry Pi with the following:

1. **GPS Module** connected and working with the Raspberry Pi serial port.
2. **Sensor** connected and communicating via serial port.
3. **Serial Communication Enabled** on the Raspberry Pi.

---------------------------
### Installation Steps
---------------------------

1. **Clone the repository:**
    ```bash
    git clone https://github.com/your-repository-url.git
    cd Sensor_Data_Api
    ```

2. **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Activate the virtual environment:**
    ```bash
    source venv/bin/activate
    ```

4. **Run the server:**
    ```bash
    python main.py
    ```

5. **Access the application locally or on the network:**
    Use the IP address and port of your Raspberry Pi, for example:
    ```
    http://192.168.31.41:8000
    ```

---

## Configuring GPS and Sensor

### Enable Serial Communication on Raspberry Pi

1. **Configure GPS:**
    - Connect your GPS module to the serial port.
    - Ensure the GPS data is being received correctly.

2. **Configure the Sensor:**
    - Connect your sensor to the Raspberry Pi's serial port.
    - Verify communication between the sensor and Raspberry Pi.

3. **Enable Serial Communication:**
    - Open Raspberry Pi configuration settings:
        *sudo raspi-config
 
    - Navigate to `Interfacing Options` → `Serial` → Enable.
    - Reboot the Raspberry Pi.


## Troubleshooting

### Common Errors and Fixes

1. **Hardware Connection Issues:**
    - Ensure all serial port connections (sensor and GPS) are properly set.
    - Check power supply to connected devices.

2. **IP Address Configuration:**
    - Verify the Raspberry Pi's IP address using:
    ```bash
    hostname -I
    ```
    - Confirm the correct IP address is used when accessing the web interface.

3. **Port Configuration:**
    - Make sure the correct port configurations are set for both the sensor and GPS modules in the Raspberry Pi.

4. **Serial Communication:**
    - Check if serial communication is enabled using the `raspi-config` tool.
    - Confirm data is flowing correctly from the sensor and GPS.

****************************
Additional Help
****************************
If you encounter any other issues, reach out to the Developer of this software:-
- Email: [bhaskerj09@gmail.com](mailto:bhaskerj09@gmail.com)


## Future Improvements

- Adding more advanced sensor data handling capabilities.
- Improving the frontend for a better user experience.
- Expanding the network capabilities to support multiple device connections.


