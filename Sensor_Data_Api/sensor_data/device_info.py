import uuid
import shutil

class DeviceInfo:
    """Class to retrieve unique device information like MAC address or Serial Number."""
    def __init__(self):
        self.mac_address = None
        self.serial_number = None

    def get_mac_address(self) -> str:
        """Retrieve the MAC address of the device."""
        try:
            mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
            self.mac_address = ':'.join(mac[i:i+2] for i in range(0, len(mac), 2))
            return self.mac_address
        except Exception as e:
            return f"Error retrieving MAC address: {str(e)}"

    def get_serial_number(self) -> str:
        """Retrieve the Serial Number of the Raspberry Pi."""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('Serial'):
                        self.serial_number = line.split(':')[1].strip()
                        return self.serial_number
        except Exception as e:
            return f"Error retrieving Serial Number: {str(e)}"

    def get_device_id(self) -> dict:
        """Return both MAC address and Serial Number as a dictionary."""
        return {
            "mac_address": self.get_mac_address(),
            "serial_number": self.get_serial_number(),
        }

class StorageInfo:

    
    def get_storage_status(self) -> dict:
        """Retrieve storage information like available, used, and total space."""
        try:
            total, used, free = shutil.disk_usage("/")
            return {
                "total_storage": f"{total // (1024 ** 3)} GB",
                "used_storage": f"{used // (1024 ** 3)} GB",
                "free_storage": f"{free // (1024 ** 3)} GB",
            }
        except Exception as e:
            return {"error": f"Error retrieving storage information: {str(e)}"}    
