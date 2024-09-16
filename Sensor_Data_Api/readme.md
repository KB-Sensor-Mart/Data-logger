Sensor_Data_Api/
│
├── main.py            # Entry point of the application
|
├── templates/
│   ├── __init__.py
│   └── index.html
│   └── ftp.html
│
├── sensor_data/
│   ├── __init__.py
│   └── data_reader.py
│
├── ftp/
│   ├── __init__.py
│   └── ftp_handler.py
│
├── network/
│   ├── __init__.py
│   └── ipmanager.py
│
├── core/              # New package to organize routes,schemas,and utils 
│   ├── __init__.py
│   ├── routes.py      # All routes will be in this file
│   ├── schemas.py     # All schemas will be in this file
│   └── utils.py       # All utility functions in this file
│
├── requirements.txt
└── README.md


here currently downloading file over ethernet , ip change and login functions are working.