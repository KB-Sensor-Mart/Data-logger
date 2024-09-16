from pydantic import BaseModel
from fastapi import Form

class FTPCredentialUpdate(BaseModel):
    host: str 
    port: int 
    username: str 
    password: str
    remote_path: str 

class LoginRequest(BaseModel):
    username: str
    password: str

class ResetPasswordRequest(BaseModel):
    username: str
    new_password: str

class IPChangeRequest(BaseModel):
    ip_address: str
    routers: str
    dns_servers: str
    
class SensorData(BaseModel):
    SNO: int
    Xdata: float
    Ydata: float
    Zdata: float