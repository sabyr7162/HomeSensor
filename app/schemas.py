from pydantic import BaseModel
from typing import Dict, Any


class UserRegisterRequest(BaseModel):
    email: str
    password: str

class UserLoginRequest(BaseModel):
    email: str
    password: str

class DeviceRegisterRequest(BaseModel):
    device_id: str
    name: str
    status: bool

class MeasurementsPostRequest(BaseModel):   
    timestamp: str
    metrics: Dict[str, Any]
