import os
import threading 
import time
import logging
import serial

class NetworkConfigurator:
    def __init__(self, interface, dhcpcd_conf="/etc/dhcpcd.conf"):
        self.interface = interface
        self.dhcpcd_conf = dhcpcd_conf
        self.backup_conf = dhcpcd_conf + ".backup"

    def backup_config(self):
        os.system(f"sudo cp {self.dhcpcd_conf} {self.backup_conf}")

    def read_config(self):
        with open(self.dhcpcd_conf, "r") as file:
            return file.readlines()

    def write_config(self, lines):
        temp_file = "/tmp/dhcpcd_conf.temp"
        with open(temp_file , "w") as file:
            file.writelines(lines)
            
        command = f"sudo mv {temp_file} {self.dhcpcd_conf}"
        os.system(command)
        print(f"Updated{self.dhcpcd_conf} with new configurations")

    def change_ip_address(self, new_ip, routers, dns_servers):
        lines = self.read_config()

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

        self.write_config(new_conf)
        self.restart_dhcpcd()
        self.restart_pi()
        
    def restart_dhcpcd(self):
        os.system("sudo systemctl restart dhcpcd")
        print("dhcpcd service restarted")
        
    def restart_pi(self):
        os.system("sudo reboot")

class IPSending:
    def __init__(self, serial_port, baud_rate, interface):
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.interface = interface
        self.configurator = NetworkConfigurator(interface)
        self.running = False
        self.lock = threading.Lock()  # Create a lock
        self.ip_thread = None  # Initialize the thread attribute
    
    def format_ip(self,ip_address):
        octets=ip_address.split('.')
        padded_octets = [octet.zfill(3) for octet in octets]
        formatted_ip = "IP," + ".".join(padded_octets) + ";\r\n"
        return formatted_ip
    
    def send_ip_to_sensor(self):
        #print("DEBUG: Started sending IP to sensor thread")
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
                        print(f"IP sent to sensor: {formatted_ip.encode()}")
                # Wait for 10 seconds before sending the IP again
                time.sleep(10)
            except serial.SerialException as e:
                print(f"Serial port error: {e}")
                time.sleep(1)  # Wait before retrying
            except Exception as e:
                print(f"Error sending IP to sensor: {e}")

    def start_sending_ip(self):
        """Start the thread to send IP to the sensor."""
        if not self.running:
            self.running = True  # Set running flag to True
            self.ip_thread = threading.Thread(target=self.send_ip_to_sensor)
            self.ip_thread.daemon = True  # Daemon thread, will terminate with main program
            self.ip_thread.start()
            print("IP sending thread started")
        else:
            print("IP sending thread is already running")

    def stop_sending_ip(self):
        self.running = False  # Set running flag to False
        if self.ip_thread is not None:
            self.ip_thread.join()  # Wait for the thread to finish
            print("IP sending thread stopped")
