# factories.py - Фабрики для создания контроллеров и представлений
from typing import Dict
from models import (
    SoundRepository, SensorDataRepository, RequestRepository,
    DecisionRepository, ResponseRepository, AuthRepository, DeviceRepository
)
from controllers import (
    RequestController, AnalysisController, DecisionController,
    ResponseController, AuthController, DeviceController
)
from patterns import MachineLearningStrategy
from speech_recognition import SpeechRecognitionController

class ControllerFactory:
    @staticmethod
    def create_controllers(repositories: Dict) -> Dict:
        controllers = {
            'request': RequestController(
                repositories['sound'],
                repositories['sensor']
            ),
            'analysis': AnalysisController(
                repositories['request'],
                MachineLearningStrategy()
            ),
            'decision': DecisionController(
                repositories['request'],
                repositories['decision']
            ),
            'response': ResponseController(
                repositories['request'],
                repositories['response']
            ),
            'auth': AuthController(repositories['auth']),
            'device': DeviceController(repositories['device']),
            'speech': SpeechRecognitionController()  # Добавляем контроллер распознавания речи
        }
        return controllers

class ViewFactory:
    @staticmethod
    def create_views(controllers: Dict, parent) -> Dict:
        from views import (
            AnalysisView, DecisionView, ResponseView,
            AuthView, DeviceView
        )
        views = {
            'analysis': AnalysisView(controllers['analysis'], parent),
            'decision': DecisionView(controllers['decision'], parent),
            'response': ResponseView(controllers['response'], parent),
            'auth': AuthView(controllers['auth'], parent),
            'device': DeviceView(controllers['device'], parent)
        }
        return views

