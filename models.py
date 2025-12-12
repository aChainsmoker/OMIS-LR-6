# models.py - Модели данных и репозитории
from abc import ABC, abstractmethod
from typing import List, Optional, Any
from dataclasses import dataclass, asdict
import json
import os

# Интерфейс репозитория
class IRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: str) -> Any:
        pass
    
    @abstractmethod
    def save(self, item: Any) -> None:
        pass
    
    @abstractmethod
    def create(self, item: Any) -> None:
        pass

# Классы данных
@dataclass
class Sound:
    id: int
    frequency: int
    noise_level: str
    
@dataclass  
class SensorData:
    id: str
    timestamp: str
    purpose: str
    
@dataclass
class Request:
    id: str
    language: str
    purpose: str
    recognition_accuracy: int
    
@dataclass
class Analysis:
    id: str
    result: str
    confidence: float
    
@dataclass
class Decision:
    id: str
    language: str
    message: str
    
@dataclass
class Response:
    id: str
    language: str
    message: str
    
@dataclass
class User:
    name: str
    user_type: str
    id: int

@dataclass
class Device:
    id: str
    name: str
    type: str
    status: str
    connection_info: str

@dataclass
class AuthUser:
    username: str
    password: str
    role: str = "user"
    full_name: str = ""

# Репозитории
class SoundRepository(IRepository):
    def __init__(self):
        self.sounds: List[Sound] = []
    
    def get_by_id(self, id: str) -> Optional[Sound]:
        for sound in self.sounds:
            if str(sound.id) == id:
                return sound
        return None
    
    def save(self, item: Sound) -> None:
        self.sounds.append(item)
    
    def create(self, item: Sound) -> None:
        self.save(item)
    
    def get_all(self) -> List[Sound]:
        return self.sounds

class DeviceRepository(IRepository):
    def __init__(self, filename="devices.json"):
        self.filename = filename
        self.devices: List[Device] = []
        self.load_from_file()
    
    def load_from_file(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.devices = [Device(**item) for item in data]
            except:
                self.devices = []
        else:
            self.devices = []
    
    def save_to_file(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump([asdict(device) for device in self.devices], f, ensure_ascii=False, indent=2)
    
    def get_by_id(self, id: str) -> Optional[Device]:
        for device in self.devices:
            if device.id == id:
                return device
        return None
    
    def save(self, item: Device) -> None:
        existing = self.get_by_id(item.id)
        if existing:
            self.devices.remove(existing)
        self.devices.append(item)
        self.save_to_file()
    
    def create(self, item: Device) -> None:
        self.save(item)
    
    def delete(self, id: str) -> bool:
        device = self.get_by_id(id)
        if device:
            self.devices.remove(device)
            self.save_to_file()
            return True
        return False
    
    def get_all(self) -> List[Device]:
        return self.devices

class AuthRepository(IRepository):
    def __init__(self, filename="users.json"):
        self.filename = filename
        self.users: List[AuthUser] = []
        self.load_default_users()
        self.load_from_file()
    
    def load_default_users(self):
        self.users = [
            AuthUser(username="admin", password="admin123", role="admin", full_name="Администратор"),
            AuthUser(username="user1", password="user123", role="user", full_name="Обычный пользователь"),
            AuthUser(username="specialist", password="spec123", role="specialist", full_name="Специалист")
        ]
        self.save_to_file()
    
    def load_from_file(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.users = [AuthUser(**item) for item in data]
            except:
                pass
    
    def save_to_file(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump([asdict(user) for user in self.users], f, ensure_ascii=False, indent=2)
    
    def get_by_id(self, username: str) -> Optional[AuthUser]:
        for user in self.users:
            if user.username == username:
                return user
        return None
    
    def save(self, item: AuthUser) -> None:
        existing = self.get_by_id(item.username)
        if existing:
            self.users.remove(existing)
        self.users.append(item)
        self.save_to_file()
    
    def create(self, item: AuthUser) -> None:
        self.save(item)
    
    def authenticate(self, username: str, password: str) -> Optional[AuthUser]:
        user = self.get_by_id(username)
        if user and user.password == password:
            return user
        return None

class SensorDataRepository(IRepository):
    def __init__(self):
        self.data: List[SensorData] = []
    
    def get_by_id(self, id: str) -> Optional[SensorData]:
        for item in self.data:
            if item.id == id:
                return item
        return None
    
    def save(self, item: SensorData) -> None:
        self.data.append(item)
    
    def create(self, item: SensorData) -> None:
        self.save(item)
    
    def get_all(self) -> List[SensorData]:
        return self.data

class RequestRepository(IRepository):
    def __init__(self):
        self.requests: List[Request] = []
    
    def get_by_id(self, id: str) -> Optional[Request]:
        for req in self.requests:
            if req.id == id:
                return req
        return None
    
    def save(self, item: Request) -> None:
        self.requests.append(item)
    
    def create(self, item: Request) -> None:
        self.save(item)
    
    def get_all(self) -> List[Request]:
        return self.requests

class DecisionRepository(IRepository):
    def __init__(self):
        self.decisions: List[Decision] = []
    
    def get_by_id(self, id: str) -> Optional[Decision]:
        for decision in self.decisions:
            if decision.id == id:
                return decision
        return None
    
    def save(self, item: Decision) -> None:
        self.decisions.append(item)
    
    def create(self, item: Decision) -> None:
        self.save(item)
    
    def get_all(self) -> List[Decision]:
        return self.decisions

class ResponseRepository(IRepository):
    def __init__(self):
        self.responses: List[Response] = []
    
    def get_by_id(self, id: str) -> Optional[Response]:
        for resp in self.responses:
            if resp.id == id:
                return resp
        return None
    
    def save(self, item: Response) -> None:
        self.responses.append(item)
    
    def create(self, item: Response) -> None:
        self.save(item)
    
    def get_all(self) -> List[Response]:
        return self.responses

