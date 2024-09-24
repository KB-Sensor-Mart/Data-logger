import os

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
