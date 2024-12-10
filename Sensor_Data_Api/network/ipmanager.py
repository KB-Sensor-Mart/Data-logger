import os
import threading 
import time
import serial
import re
import subprocess
from logging_config import get_logger

class NetworkConfigurator:
    def __init__(self, interface, dhcpcd_conf="/etc/dhcpcd.conf"):
        self.interface = interface
        self.dhcpcd_conf = dhcpcd_conf
        self.backup_conf = dhcpcd_conf + ".backup"
        self.logger = get_logger(__name__)
        self.backup_config()

    def backup_config(self):
        try:
            if os.path.exists(self.dhcpcd_conf):
                os.system(f"sudo cp {self.dhcpcd_conf} {self.backup_conf}")
                self.logger.info(f"backup of {self.dhcpcd_conf} created at {self.backup_config}")
            else:
                self.logger.error(f"Configuration file {self.dhcpcd_conf} not found.")
        except Exception as e:
            self.logger.error(f"Failed to create backup: {str(e)}")

    def read_config(self):
        try:
            with open(self.dhcpcd_conf, "r") as file:
                self.logger.info(f"Reading {self.dhcpcd_conf}")
                return file.readlines()
        except FileNotFoundError:
            self.logger.error(f"{self.dhcpcd_conf} not found.")
            return None
        except Exception as e:
            self.logger.error(f"Error reading {self.dhcpcd_conf}: {str(e)}")
            return None

    def write_config(self, lines):
        temp_file = "/tmp/dhcpcd_conf.temp"
        try:
            with open(temp_file, "w") as file:
                file.writelines(lines)
                self.logger.info(f"Temporary configuration written to {temp_file}")
            
            command = f"sudo mv {temp_file} {self.dhcpcd_conf}"
            os.system(command)
            self.logger.info(f"{self.dhcpcd_conf} updated with new configurations")
        except Exception as e:
            self.logger.error(f"Error writing configuration: {str(e)}")

    def validate_ip(self, ip):
        ip_regex = re.compile(
            r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
            r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
            r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
            r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        )
        if not ip_regex.match(ip):
            self.logger.error(f"Invalid IP address format: {ip}")
            return False
        return True

    def change_ip_address(self, new_ip, routers, dns_servers):
        if not self.validate_ip(new_ip):
            self.logger.error(f"Invalid IP address: {new_ip}")
            return {"status": "error", "message": f"Invalid IP address: {new_ip}"}
        
        if not self.validate_ip(routers):
            self.logger.error(f"Invalid router address: {routers}")
            return {"status": "error", "message": f"Invalid router address: {routers}"}

        lines = self.read_config()
        if lines is None:
            self.logger.error("Failed to read the network configuration file.")
            return {"status": "error", "message": "Failed to read the network configuration file."}

        new_conf = []
        inside_static_block = False

        for line in lines:
            if line.startswith(f"interface {self.interface}"):
                inside_static_block = True

            if inside_static_block and line.strip().startswith("static ip_address"):
                new_conf.append(f"static ip_address={new_ip}/24\n")
            elif inside_static_block and line.strip().startswith("static routers"):
                new_conf.append(f"static routers={routers}\n")
            elif inside_static_block and line.strip().startswith("static domain_name_servers"):
                new_conf.append(f"static domain_name_servers={dns_servers}\n")
            elif inside_static_block and line.strip() == "":
                inside_static_block = False
                new_conf.append(line)
            else:
                new_conf.append(line)

        if not inside_static_block:
            new_conf.append(f"\ninterface {self.interface}\n")
            new_conf.append(f"static ip_address={new_ip}/24\n")
            new_conf.append(f"static routers={routers}\n")
            new_conf.append(f"static domain_name_servers={dns_servers}\n")

        # Write the new configuration
        self.write_config(new_conf)
        
        # Restart services and return the result
        if self.restart_dhcpcd():
            if self.restart_pi():
                self.logger.info(f"IP address changed to {new_ip} successfully.")
                return {"status": "success", "message": f"IP address changed to {new_ip} successfully."}
            else:
                self.logger.error("Failed to restart the Raspberry Pi after changing IP address.")
                return {"status": "error", "message": "Failed to restart the Raspberry Pi after changing IP address."}
        else:
            self.logger.error("Failed to restart the DHCP service.")
            return {"status": "error", "message": "Failed to restart the DHCP service."}
    
    def restart_dhcpcd(self):
        try:
            result = subprocess.run(["sudo", "systemctl", "restart", "dhcpcd"], check=True)
            if result.returncode == 0:
                self.logger.info("dhcpcd service restarted successfully")
                return True
            else:
                self.logger.error(f"Failed to restart dhcpcd: {result.stderr}")
                return False
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error restarting dhcpcd: {str(e)}")
            return False

    def restart_pi(self):
        try:
            result = subprocess.run(["sudo", "reboot"], check=True)
            if result.returncode == 0:
                self.logger.info("Rebooting the system...")
                return True
            else:
                self.logger.error(f"Failed to reboot: {result.stderr}")
                return False
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error rebooting system: {str(e)}")
            return False
'''            
class IPSending:
    def __init__(self, serial_port, baud_rate, interface):
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.interface = interface
        self.configurator = NetworkConfigurator(interface)
        self.running = False
        self.lock = threading.Lock()  # Create a lock
        self.ip_thread = None  # Initialize the thread attribute
        self.logger = get_logger(__name__)
    
    def format_ip(self,ip_address):
        octets=ip_address.split('.')
        padded_octets = [octet.zfill(3) for octet in octets]
        formatted_ip = "IP," + ".".join(padded_octets) + ";\r\n"
        return formatted_ip
    
    def send_ip_to_sensor(self):
        self.logger.info("sending IP to sensor in thread initialised")
        while self.running:
            try:
                # Get the current IP address
                current_ip = os.popen('hostname -I').read().strip()
                
                ip_list = current_ip.split()
                last_ip = ip_list[-1]  # Get the last IP address
                
                #print(f"Current IP address: {current_ip}")
                formatted_ip = self.format_ip(last_ip)
                #print(f"Formatted IP: {formatted_ip}")
                
                with self.lock:
                    # Send IP via serial port
                    with serial.Serial(self.serial_port, self.baud_rate, timeout=1) as ser:
                        #print("Serial port opened successfully for sensor ")
                        ser.write(formatted_ip.encode())
                        self.logger.debug(f"IP sent to sensor: {formatted_ip.encode()}")
                # Wait for 10 seconds before sending the IP again
                time.sleep(30)
            except serial.SerialException as e:
                self.logger.error(f"Serial port error: {e}")
                time.sleep(1)  # Wait before retrying
            except Exception as e:
                self.logger.error(f"Error sending IP to sensor: {e}")

    def start_sending_ip(self):
        """Start the thread to send IP to the sensor."""
        if not self.running:
            self.running = True  # Set running flag to True
            self.ip_thread = threading.Thread(target=self.send_ip_to_sensor)
            self.ip_thread.daemon = True  # Daemon thread, will terminate with main program
            self.ip_thread.start()
            self.logger.info("IP sending thread started")
        else:
            self.logger.warning("IP sending thread is already running")

    def stop_sending_ip(self):
        self.running = False  # Set running flag to False
        if self.ip_thread is not None:
            self.ip_thread.join()  # Wait for the thread to finish
            self.logger.info("IP sending thread stopped")
'''         
