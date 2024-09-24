import serial
import time 
from datetime import datetime, timedelta
import threading 
import asyncio

gps_data = {
	"date": "N/A",
	"time": "N/A",
	"latitude": "N/A",
	"longitude": "N/A"
}

def get_gps_data(data):
	#print(f"DEBUG:- Raw gps data received: {data}")
	if not data.startswith("$GNRMC"):
		#print("DEBUG: Data do not start with $GNRMC")
		return None 
	parts = data.split(",")
	if len(parts) < 10:
		#print("Data length is less then 10: {len)(parts)}")
		return None
	try:
		#extract time latitude and longitude
		gps_time = parts[1]
		gps_date = parts[9]
		latitude_raw = parts[3]
		latitude_dir = parts[4]
		longitude_raw = parts[5]
		longitude_dir = parts[6]
		
		latitude = convert_to_decimal_degree(latitude_raw, latitude_dir)
		longitude = convert_to_decimal_degree(longitude_raw, longitude_dir)
		
		
		return gps_time, latitude , longitude, gps_date
	except ValueError as e:
		#print("DEBUG: Valueerror in get_gps_data: {e}")
		return None

def convert_to_decimal_degree(raw_value, direction):
	#print(f"DEBUG: Converting raw_value: {raw_value} with direction: {direction}")
	try:
		if len(raw_value) > 7:
			# Latitude has 2 degrees digits, Longitude has 3 degrees digits
			if direction in ["N", "S"]:
				degrees = int(raw_value[:2])  # First 2 digits for latitude
				minutes = float(raw_value[2:])  # Rest is minutes
			elif direction in ["E", "W"]:
				degrees = int(raw_value[:3])  # First 3 digits for longitude
				minutes = float(raw_value[3:])  # Rest is minutes
			
			#print(f"DEBUG: Extracted Degrees: {degrees}, Minutes: {minutes}")
		
			#convert minutes to decimal 
			decimal_degree = degrees + minutes / 60.0
			
			if direction == "S" or direction == "W":
				decimal_degree = -decimal_degree
			#print(f"DEBUG: Final Decimal Degree: {decimal_degree}")
			return round(decimal_degree, 6)
		else:
			#print(f"DEBUG: Invalid raw_value length: {len(raw_value)}")
			return None
	except ValueError as e:
		print(f"DEBUG:- Error converting to decimal degree: {e}")
		return None
			
def format_gps_time(gps_time):
	try:
		gps_time = gps_time.split('.')[0]
		if len(gps_time) != 6 or not gps_time.isdigit():
			raise ValueError("Gps time string is not in correct format")
			
		gps_datetime = datetime.strptime(gps_time,"%H%M%S")
		ist_offset = timedelta(hours=5, minutes=30)
		ist_time = gps_datetime + ist_offset
		return ist_time.strftime("%H:%M:%S")
	except ValueError as e:
		print(f"DEBUG: Error prasing gps time: {e}")
		return "Invalid Time"
	
def format_gps_date(gps_date):
	try:
		# GPS date is in the format DDMMYY
		date_object = datetime.strptime(gps_date, "%d%m%y")
		# Return formatted date as DD/MM/YYYY
		return date_object.strftime("%d/%m/%Y")
	except ValueError:
		print(f"DEBUG error prasing gps date: {e}")
		return "Invalid data"
	
def read_gps_data():
	ser= serial.Serial("/dev/serial0" , 9600)
	print("DEBUG Serial port opened")
	try:
		while True:
			line = ser.readline().decode('utf-8' , errors ='ignore').strip()
			if line:
				#print(f"DEBUG: Raw serial data: {line}")
				result = get_gps_data(line)
				
				if result:
					gps_time,latitude,longitude,gps_date = result
					formatted_gps_time = format_gps_time(gps_time)
					formatted_gps_date = format_gps_date(gps_date)
					
					 # Update the global gps_data dictionary
					gps_data["date"] = formatted_gps_date
					gps_data["time"] = formatted_gps_time
					gps_data["latitude"] = f"{latitude:.6f}"
					gps_data["longitude"] = f"{longitude:.6f}"
					#print(f"DEBUG: Updated gps data {gps_data}")
	except serial.SerialException as e:
		print(f"Serial error: {e}")
	except Exception as e:
		print(f"An error occurred: {e}")
		
		
		
# WebSocket handler
async def send_gps_data_via_websocket(websocket):
	while True:
		try:
			#print(f"DEBUG: Sending GPS data via WebSocket: {gps_data}")
			await websocket.send_json(gps_data)
			await asyncio.sleep(0.5)  # Send GPS data every 1 second
		except Exception as e:
			print(f"WebSocket error: {e}")
			break
			
def start_gps_reader():
    # Start a separate thread for reading GPS data
    threading.Thread(target=read_gps_data, daemon=True).start()


