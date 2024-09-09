from pydantic import BaseModel

class FTPSettings(BaseModel):
    host: str
    port: int
    username: str
    password: str
    remote_path: str
    log_file: str = "uploaded_files_log.json"
    retries: int = 3


class FTPCredentialUpdate(BaseModel):
    host: str
    port: int
    username: str
    password: str
    remote_path: str


class IPChangeRequest(BaseModel):
    ip_address: str
    routers: str
    dns_servers: str
