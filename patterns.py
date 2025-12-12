# patterns.py - Паттерны проектирования (Стратегия, Команда)
from abc import ABC, abstractmethod
from typing import List, Any
from models import Analysis, Decision

# ====================== ПАТТЕРН СТРАТЕГИЯ ======================

class IAnalysisStrategy(ABC):
    @abstractmethod
    def analyze_data(self, data: List[Any]) -> Analysis:
        pass

class MachineLearningStrategy(IAnalysisStrategy):
    def analyze_data(self, data: List[Any]) -> Analysis:
        # Реализация анализа через машинное обучение
        return Analysis(id="ml_1", result="ML Analysis Result", confidence=0.95)

class StatisticalAnalysisStrategy(IAnalysisStrategy):
    def analyze_data(self, data: List[Any]) -> Analysis:
        # Реализация статистического анализа
        return Analysis(id="stat_1", result="Statistical Analysis Result", confidence=0.88)

# ====================== ПАТТЕРН КОМАНДА ======================

class ICommand(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass
    
    @abstractmethod
    def undo(self) -> None:
        pass

class AnalysisCommand(ICommand):
    def __init__(self, controller, data: List[Any]):
        self.controller = controller
        self.data = data
        self.previous_state = None
    
    def execute(self) -> None:
        self.previous_state = self.controller.get_current_state()
        result = self.controller.perform_analysis(self.data)
        return result
    
    def undo(self) -> None:
        if self.previous_state:
            self.controller.restore_state(self.previous_state)

class ResponseCommand(ICommand):
    def __init__(self, controller, decision: Decision):
        self.controller = controller
        self.decision = decision
        self.previous_response = None
    
    def execute(self) -> None:
        self.previous_response = self.controller.get_last_response()
        result = self.controller.generate_response(self.decision)
        return result
    
    def undo(self) -> None:
        if self.previous_response:
            self.controller.restore_response(self.previous_response)

