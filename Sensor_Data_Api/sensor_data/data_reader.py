import serial
import threading
import time 
import csv 
from datetime import datetime
import os
from gps import gps_data
import numpy as np
from obspy import Stream, Trace
from obspy.core import UTCDateTime
from .miniseed import CSVToMiniSEEDConverter
from logging_config import get_logger



logger = get_logger(__name__)

class listNode:
    def __init__(self, val, nxt, prev):
        self.val = val
        self.next = nxt  # it is the starting pointer of circular queue 
        self.prev = prev # it is the end pointer of the circular queue

class MyCircularQueue:
    def __init__(self, k: int):
        self.space = k
        self.left = listNode(0, None, None)
        self.right = listNode(0, None, self.left)
        self.left.next = self.right

    def enQueue(self, value: int) -> bool:
        if self.space == 0:
            logger.warning("Queue is full. Cannot enqueue.")
            return False
        cur = listNode(value, self.right, self.right.prev)
        self.right.prev.next = cur 
        self.right.prev = cur
        self.space -= 1
        logger.info(f"Enqueued value: {value}. Space remaining: {self.space}.")
        return True
    
    def deQueue(self) -> bool:
        if self.isEmpty():
            logger.warning("Queue is empty. Cannot dequeue.")
            return False
        removed_value = self.left.next.val
        self.left.next = self.left.next.next
        self.left.next.prev = self.left
        self.space += 1
        logger.info(f"Dequeued value: {removed_value}. Space available: {self.space}.")
        return True
    
    def Front(self) -> int:
        if self.isEmpty():
            logger.warning("Queue is empty. Cannot access front value.")
            return -1
        return self.left.next.val

    def Rear(self) -> int:
        if self.isEmpty():
            logger.warning("Queue is empty. Cannot access rear value.")
            return -1
        return self.right.prev.val

    def isEmpty(self) -> bool:
        return self.left.next == self.right
    
    def isFull(self) -> bool:
        return self.space == 0

class LogWriter:
    def __init__(self, log_filename="log.csv"):
        self.log_folder = "log"
        self.log_filename = os.path.join(self.log_folder, log_filename)
        self.index_no = 1
        self.ensure_log_folder_exists()
        self.initialize_log_file()

    def ensure_log_folder_exists(self):
        if not os.path.exists(self.log_folder):
            os.makedirs(self.log_folder)
            logger.info(f"Created log folder: {self.log_folder}")

    def initialize_log_file(self):
        if not os.path.exists(self.log_filename):
            with open(self.log_filename, mode='w', newline='') as log_file:
                writer = csv.DictWriter(log_file, fieldnames=['index_no', 'file_name', 'time_of_creation'])
                writer.writeheader()
            logger.info(f"Initialized log file: {self.log_filename}")

    def log_file_creation(self, file_name):
        time_of_creation = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_filename, mode='a', newline='') as log_file:
            writer = csv.DictWriter(log_file, fieldnames=['index_no', 'file_name', 'time_of_creation'])
            writer.writerow({
                'index_no': self.index_no,
                'file_name': file_name,
                'time_of_creation': time_of_creation
            })
        logger.info(f"Logged file creation: {file_name} at {time_of_creation}")
        self.index_no += 1
        
class CSVwriter:
    def __init__(self, filename_prefix, sr_no_limit, log_writer):
        self.filename_prefix = filename_prefix
        self.file_index = 1
        self.sr_no_limit = sr_no_limit
        self.log_writer = log_writer
        self.current_sr_no = 0
        self.current_date = datetime.now().strftime("%d-%m-%Y")
        self.base_folder = "data"
        self.ensure_base_folder_exists()
        self.date_folder = ""
        self.converter =CSVToMiniSEEDConverter()
        self.open_new_file()


    def ensure_base_folder_exists(self):
        if not os.path.exists(self.base_folder):
            os.makedirs(self.base_folder)
            logger.info(f"Created data folder: {self.base_folder}")
      
    
    def open_new_file(self):
        new_date = datetime.now().strftime("%d-%m-%Y")
        if new_date != self.current_date:
            self.current_date = new_date
            self.file_index = 1
            logger.info(f"Date changed. Resetting file index to 1 for date: {self.current_date}")
        date_folder = os.path.join(self.base_folder, self.current_date)
        self.date_folder = date_folder
        if not os.path.exists(date_folder):
            os.makedirs(date_folder)
            logger.info(f"Created date folder: {date_folder}")
        timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
        self.filename = os.path.join(date_folder, f"{timestamp}.csv")
        self.file = open(self.filename, mode='w', newline='')

        #set up csv writer
        self.writer = csv.DictWriter(self.file, fieldnames=['SNO', 'Xdata', 'Ydata', 'Zdata'])
        #write gps data on top of csv file
        self.write_gps_data()
        #write header for sensor data
        self.writer.writeheader()
        self.log_writer.log_file_creation(self.filename)
        logger.info(f"Opened new CSV file for writing: {self.filename}")

    def write_gps_data(self):
        """Writes the GPS data to the first row of the CSV file."""
        self.file.write("Date,Time,Latitude,Longitude\n")
        self.file.write(f"{gps_data['date']},{gps_data['time']},{gps_data['latitude']},{gps_data['longitude']}\n")
        logger.info(f"Wrote GPS data to CSV: {gps_data}")

    def save_data(self, data_point):
        try:
            sr_no = int(data_point['SNO'])
        except ValueError:
            logger.error(f"Invalid sr_no value: {data_point['SNO']} - Skipping this data point.")
            return
        self.writer.writerow(data_point)
        self.current_sr_no = sr_no
        logger.debug(f"Saved data point {sr_no} to {self.filename}")
        if self.current_sr_no >= self.sr_no_limit:
            logger.info(f"CSV file limit reached for {self.filename}. Preparing to create a new file.")
            self.close()
            self.converter.convert_csv_to_miniseed(self.filename)
            self.file_index += 1
            self.open_new_file()
            

    def close(self):
        self.file.close()
        
#this is the files where i will handel the downloading data via ethernet   
class FilesDownloading:
    def __init__(self,base_folder):
        self.base_folder =base_folder
    
    def get_files_by_date(self, date_str):
        date_folder = os.path.join(self.base_folder, date_str)
        if not os.path.exists(date_folder):
            logger.warning(f"No files found for date: {date_str}")
            return []
        files = [os.path.join(date_folder, f) for f in os.listdir(date_folder) if f.endswith('.mseed')]
        logger.info(f"Retrieved {len(files)} files for date: {date_str}")
        return files
    
class SensorDataReader:
    def __init__(self, port, baud_rate, queue_size, csv_filename_prefix, sr_no_limit, log_writer):
        self.port = port
        self.baud_rate = baud_rate
        self.serial_connection = serial.Serial(self.port, self.baud_rate)
        self.data_queue = MyCircularQueue(queue_size)
        self.lock = threading.Lock()
        # Initialize converter and pass to CSVWriter
        self.csv_writer = CSVwriter(csv_filename_prefix, sr_no_limit, log_writer)
        
        self.read_thread = threading.Thread(target=self.read_data)
        self.read_thread.start()
        logger.info(f"Started data reading thread on port: {self.port} with baud rate: {self.baud_rate}")

    def read_data(self):
        while True:
            if self.serial_connection.in_waiting > 0:
                data_line = self.serial_connection.readline().decode('utf-8', errors='replace').strip()
                part = data_line.split(',')
                if len(part) == 4:
                    data_point = {
                        "SNO": part[0],
                        "Xdata": part[1],
                        "Ydata": part[2],
                        "Zdata": part[3]
                    }
                    logger.debug(f"Read data: {data_point}")
                    with self.lock:
                        if self.data_queue.isFull():
                            self.data_queue.deQueue()
                        self.data_queue.enQueue(data_point)
                    self.csv_writer.save_data(data_point)

            
            time.sleep(0.005)

    def get_data(self):
        with self.lock:
            data_list = []
            current = self.data_queue.left.next
            while current != self.data_queue.right:
                data_list.append(current.val)
                current = current.next
            return data_list
    
    def stop(self):
        self.csv_writer.close()
        self.read_thread.join()
