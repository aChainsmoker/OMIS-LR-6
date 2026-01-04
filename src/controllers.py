from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from datetime import datetime
from models import (
    Sound, SensorData, Request, Analysis, Decision, Response,
    AuthUser, Device,
    SoundRepository, SensorDataRepository, RequestRepository,
    DecisionRepository, ResponseRepository, AuthRepository, DeviceRepository
)
from patterns import IAnalysisStrategy, MachineLearningStrategy, ICommand, AnalysisCommand, ResponseCommand

class IController(ABC):
    @abstractmethod
    def update_view(self, data: Any) -> None:
        pass

class IView(ABC):
    @abstractmethod
    def display(self, data: Any) -> None:
        pass
    
    @abstractmethod
    def update(self, data: Any) -> None:
        pass


class AuthController(IController):
    def __init__(self, auth_repo: AuthRepository):
        self.auth_repo = auth_repo
        self.current_user: Optional[AuthUser] = None
        self.views: List[IView] = []
    
    def login(self, username: str, password: str) -> Optional[AuthUser]:
        user = self.auth_repo.authenticate(username, password)
        if user:
            self.current_user = user
            self.notify_views({"type": "login_success", "user": user})
            return user
        self.notify_views({"type": "login_failed", "message": "Неверные учетные данные"})
        return None
    
    def logout(self) -> None:
        self.current_user = None
        self.notify_views({"type": "logout"})
    
    def get_current_user(self) -> Optional[AuthUser]:
        return self.current_user
    
    def add_user(self, user: AuthUser) -> bool:
        if not self.auth_repo.get_by_id(user.username):
            self.auth_repo.save(user)
            self.notify_views({"type": "user_added", "user": user})
            return True
        self.notify_views({"type": "user_exists", "message": "Пользователь уже существует"})
        return False
    
    def add_view(self, view: IView) -> None:
        self.views.append(view)
    
    def notify_views(self, data: Any) -> None:
        for view in self.views:
            view.update(data)
    
    def update_view(self, data: Any) -> None:
        self.notify_views(data)

class DeviceController(IController):
    def __init__(self, device_repo: DeviceRepository):
        self.device_repo = device_repo
        self.views: List[IView] = []
    
    def get_all_devices(self) -> List[Device]:
        return self.device_repo.get_all()
    
    def add_device(self, device: Device) -> bool:
        if not self.device_repo.get_by_id(device.id):
            self.device_repo.save(device)
            self.notify_views({"type": "device_added", "device": device})
            return True
        self.notify_views({"type": "device_exists", "message": "Устройство с таким ID уже существует"})
        return False
    
    def update_device(self, device: Device) -> bool:
        existing = self.device_repo.get_by_id(device.id)
        if existing:
            self.device_repo.save(device)
            self.notify_views({"type": "device_updated", "device": device})
            return True
        return False
    
    def delete_device(self, device_id: str) -> bool:
        success = self.device_repo.delete(device_id)
        if success:
            self.notify_views({"type": "device_deleted", "device_id": device_id})
        return success
    
    def get_device_by_id(self, device_id: str) -> Optional[Device]:
        return self.device_repo.get_by_id(device_id)
    
    def add_view(self, view: IView) -> None:
        self.views.append(view)
    
    def notify_views(self, data: Any) -> None:
        for view in self.views:
            view.update(data)
    
    def update_view(self, data: Any) -> None:
        self.notify_views(data)


class RequestController(IController):
    def __init__(self, sound_repo: SoundRepository, sensor_repo: SensorDataRepository):
        self.sound_repo = sound_repo
        self.sensor_repo = sensor_repo
        self.current_request = None
        self.views: List[IView] = []
    
    def create_request(self, sound_data: Sound, sensor_data: SensorData) -> Request:
        request = Request(
            id=f"req_{datetime.now().timestamp()}",
            language="ru",
            purpose="Анализ данных",
            recognition_accuracy=95
        )
        self.current_request = request
        self.sound_repo.save(sound_data)
        self.sensor_repo.save(sensor_data)
        self.notify_views(request)
        return request
    
    def get_request(self) -> Optional[Request]:
        return self.current_request
    
    def add_view(self, view: IView) -> None:
        self.views.append(view)
    
    def notify_views(self, data: Any) -> None:
        for view in self.views:
            view.update(data)
    
    def update_view(self, data: Any) -> None:
        self.notify_views(data)

class AnalysisController(IController):
    def __init__(self, request_repo: RequestRepository, strategy: IAnalysisStrategy = None):
        self.request_repo = request_repo
        self.strategy = strategy or MachineLearningStrategy()
        self.current_analysis = None
        self.views: List[IView] = []
        self.commands: List[ICommand] = []
    
    def perform_analysis(self, request: Request) -> Analysis:
        # Получаем данные для анализа
        sensor_data = []
        analysis = self.strategy.analyze_data(sensor_data)
        self.current_analysis = analysis
        
        # Создаем и выполняем команду
        command = AnalysisCommand(self, sensor_data)
        command.execute()
        self.commands.append(command)
        
        self.notify_views(analysis)
        return analysis
    
    def get_analytics(self) -> List[Analysis]:
        return [self.current_analysis] if self.current_analysis else []
    
    def set_strategy(self, strategy: IAnalysisStrategy) -> None:
        self.strategy = strategy
    
    def add_view(self, view: IView) -> None:
        self.views.append(view)
    
    def notify_views(self, data: Any) -> None:
        for view in self.views:
            view.update(data)
    
    def update_view(self, data: Any) -> None:
        self.notify_views(data)
    
    def get_current_state(self):
        return self.current_analysis
    
    def restore_state(self, state):
        self.current_analysis = state

class DecisionController(IController):
    def __init__(self, request_repo: RequestRepository, decision_repo: DecisionRepository):
        self.request_repo = request_repo
        self.decision_repo = decision_repo
        self.current_decision = None
        self.views: List[IView] = []
        self.commands: List[ICommand] = []
    
    def make_decision(self, analysis: Analysis) -> Decision:
        decision = Decision(
            id=f"dec_{datetime.now().timestamp()}",
            language="ru",
            message=f"Решение на основе анализа: {analysis.result}"
        )
        self.current_decision = decision
        self.decision_repo.save(decision)
        
        # Создаем команду
        command = AnalysisCommand(self, [analysis])
        command.execute()
        self.commands.append(command)
        
        self.notify_views(decision)
        return decision
    
    def get_decision(self) -> Optional[Decision]:
        return self.current_decision
    
    def add_view(self, view: IView) -> None:
        self.views.append(view)
    
    def notify_views(self, data: Any) -> None:
        for view in self.views:
            view.update(data)
    
    def update_view(self, data: Any) -> None:
        self.notify_views(data)

class ResponseController(IController):
    def __init__(self, request_repo: RequestRepository, response_repo: ResponseRepository):
        self.request_repo = request_repo
        self.response_repo = response_repo
        self.current_response = None
        self.views: List[IView] = []
        self.commands: List[ICommand] = []
    
    def generate_response(self, decision: Decision) -> Response:
        response = Response(
            id=f"resp_{datetime.now().timestamp()}",
            language=decision.language,
            message=f"Ответ: {decision.message}"
        )
        self.current_response = response
        self.response_repo.save(response)
        
        # Создаем команду
        command = ResponseCommand(self, decision)
        command.execute()
        self.commands.append(command)
        
        self.notify_views(response)
        return response
    
    def get_response(self) -> Optional[Response]:
        return self.current_response
    
    def add_view(self, view: IView) -> None:
        self.views.append(view)
    
    def notify_views(self, data: Any) -> None:
        for view in self.views:
            view.update(data)
    
    def update_view(self, data: Any) -> None:
        self.notify_views(data)
    
    def get_last_response(self):
        return self.current_response
    
    def restore_response(self, response):
        self.current_response = response

