import ftplib
import os
import json
import logging
import psutil
import time

class FTPHandler:
		def __init__(self, host, port, username, password, remote_path, log_file="uploaded_files_log.json", retries=3):
			"""
			Initializes the FTPHandler class with FTP server credentials and paths.
			"""
			self.host = host
			self.port = port  # Added port for FTP connection
			self.username = username
			self.password = password
			self.remote_path = remote_path
			self.log_file = log_file
			self.retries = retries
			self.ftp = None
			self.log = logging.getLogger("FTPHandler")
			logging.basicConfig(level=logging.DEBUG)
			 
		def is_file_open(self, file_path):
			self.log.debug(f"Checking if file is open: {file_path}")
			"""
			Checks if a file is open by another process using psutil.
			Returns True if the file is open, False otherwise.
			"""
			for proc in psutil.process_iter(['pid','name','open_files']):
				try:
					open_files = proc.info['open_files']
					if open_files:
							if any(file.path == file_path for file in proc.info['open_files']):
									self.log.debug(f"File is open: {file_path}")
									return True
				except (psutil.NoSuchProcess, psutil.AccessDenied):
					continue
			self.log.debug(f"File is not open: {file_path}")
			return False
			
		def connect(self):
			self.log.debug(f"Connecting to FTP server {self.host}:{self.port}")
			"""
			Establishes a connection to the FTP server.
			"""
			try:
				self.ftp = ftplib.FTP()
				self.ftp.connect(self.host, self.port)  # Connect with host and port
				self.ftp.login(self.username, self.password)
				self.log.info(f"Connected to FTP server: {self.host}")
				self.change_directory_or_create(self.remote_path)
				return True
			except ftplib.error_perm as e:
					self.log.error(f"FTP permission error : {e}")
			except Exception as e:
					self.log.error(f"Error connecting to FTP server : {e}")
					return False

		def change_directory_or_create(self, path):
			self.log.debug(f"Changing to remote directory: {path}")
			"""
			Tries to change to the specified directory on the FTP server. 
			If the directory does not exist, it creates it.
			"""
			try:
				self.ftp.cwd(path)
				self.log.info(f"Changed to remote directory: {path}")
			except ftplib.error_perm:
				# Directory doesn't exist, create it
				self.create_remote_directory(path)

		def create_remote_directory(self, path):
			self.log.debug(f"Creating remote directory: {path}")
			"""
			Creates the specified directory on the remote FTP server.
			"""
			directories = path.split('/')
			current_path = ""
			for directory in directories:
				if directory:  # Only process non-empty directory names
					current_path += f"/{directory}"
					try:
						self.ftp.mkd(current_path)
						self.log.info(f"Created remote directory: {current_path}")
					except ftplib.error_perm:
						# Directory likely already exists
						pass
			self.ftp.cwd(path)

		def upload_file(self, local_file_path):
			"""
			Uploads a file to the remote FTP server.
			Retries if it fails, logs the upload status.
			"""
			file_name = os.path.basename(local_file_path)
			self.log.debug(f"Attempting to upload file: {file_name}")
			
			if self.is_file_open(local_file_path):
				self.log.error(f"File {file_name} is in use, cannot upload.")
				return {"file_name": file_name, "status": "File in use"}
			
			attempt = 0
			while attempt < self.retries:
				try:
					with open(local_file_path, 'rb') as file:
						self.ftp.storbinary(f"STOR {file_name}", file)
						self.log.info(f"Uploaded file: {file_name}")
						self.log_uploaded_file(local_file_path)
						return {"file_name": file_name, "status": "Completed"}
				except (ftplib.error_perm, ftplib.error_reply, ftplib.error_temp) as e:
					self.log.error(f"FTP error uploading file {file_name}: {e}")
				except Exception as e:
					self.log.error(f"Failed to upload file {file_name}: {e}")
				attempt += 1
				time.sleep(5)  # Increase delay before retrying
			return {"file_name": file_name, "status": "Failed after retries"}

		def log_uploaded_file(self, file_path):
			self.log.debug(f"Logging uploaded file: {file_path}")
			"""
			Logs the path of successfully uploaded files to a JSON file.
			Ensures that files are not uploaded multiple times.
			"""
			if not os.path.exists(self.log_file):
				with open(self.log_file, 'w') as log:
					json.dump([], log)
			
			with open(self.log_file, 'r+') as log:
				uploaded_files = json.load(log)
				if file_path not in uploaded_files:
					uploaded_files.append(file_path)
					log.seek(0)
					json.dump(uploaded_files, log, indent=4)
					self.log.info(f"Logged uploaded file: {file_path}")

		def scan_and_upload(self, path_folder):
			self.log.debug(f"Scanning folder for upload: {path_folder}")
			"""
			Scans a folder and uploads all files that have not been uploaded yet.
			"""
			uploaded_files = self.read_uploaded_files_log()
			
			for root, dirs, files in os.walk(path_folder):
				for file_name in files:
					file_path = os.path.join(root, file_name)
					if file_path not in uploaded_files:
						self.upload_file(file_path)

		def read_uploaded_files_log(self):
			self.log.debug(f"Reading uploaded files log from: {self.log_file}")
			"""
			Reads the log file and returns a list of already uploaded files.
			"""
			if not os.path.exists(self.log_file):
				return []
			
			with open(self.log_file, 'r') as log:
				return json.load(log)

		def close(self):
			"""
			Closes the FTP connection.
			"""
			if self.ftp:
				self.ftp.quit()
				self.log.info("FTP connection closed.")

		def trigger_upload(self, local_directory):
			"""
			This method simulates a trigger mechanism by scanning the directory for new files
			and automatically uploading them when they are created.
			"""
			self.scan_and_upload(local_directory)
                        
if __name__=="__main__":
        folder_path = 'data'
        log_file='./log/uploaded_files_log.json'
        scan_and_upload(path_folder = folder_path,log_file_path=log_file,use_passive=True)
        print("Scanning and uploading completed.")
