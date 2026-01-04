import threading
import queue
import time
from typing import List, Any, Optional
from abc import ABC, abstractmethod

# Импорты для распознавания речи
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("Предупреждение: speech_recognition не установлен. Установите: pip install SpeechRecognition")

from controllers import IController, IView

# Контроллер для распознавания речи (только Google Speech API)
class SpeechRecognitionController(IController):
    """Контроллер управления распознаванием речи"""
    def __init__(self):
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.views: List[IView] = []
        self.microphone = None
        
        # Параметры распознавания
        self.energy_threshold = 300  # Порог энергии для обнаружения речи
        self.pause_threshold = 0.8   # Пауза для окончания фразы
        self.phrase_time_limit = 5   # Максимальная длина фразы
        
        # История распознанных фраз
        self.recognition_history = []
    
    def start_listening(self, timeout=None):
        """Начать прослушивание микрофона в отдельном потоке"""
        if self.is_listening:
            return False
        
        if not SPEECH_RECOGNITION_AVAILABLE:
            return False
        
        self.is_listening = True
        
        # Запускаем поток для прослушивания
        thread = threading.Thread(target=self._listen_loop, args=(timeout,))
        thread.daemon = True
        thread.start()
        
        return True
    
    def stop_listening(self):
        """Остановить прослушивание"""
        self.is_listening = False
    
    def _listen_loop(self, timeout=None):
        """Цикл прослушивания микрофона"""
        if not SPEECH_RECOGNITION_AVAILABLE:
            return
        
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = self.energy_threshold
        recognizer.pause_threshold = self.pause_threshold
        
        try:
            with sr.Microphone() as source:
                self.microphone = source
                recognizer.adjust_for_ambient_noise(source)
                
                start_time = time.time()
                while self.is_listening:
                    if timeout and time.time() - start_time > timeout:
                        break
                    
                    try:
                        audio = recognizer.listen(
                            source, 
                            phrase_time_limit=self.phrase_time_limit,
                            timeout=1
                        )
                        
                        # Распознаем речь через Google Speech API
                        text = self.recognize_audio(audio)
                        if text:
                            self.recognition_history.append({
                                "timestamp": time.time(),
                                "text": text
                            })
                            
                            # Ограничиваем историю
                            if len(self.recognition_history) > 50:
                                self.recognition_history.pop(0)
                            
                            self.audio_queue.put(text)
                    
                    except sr.WaitTimeoutError:
                        continue
                    except Exception as e:
                        print(f"Ошибка при прослушивании: {e}")
        
        except Exception as e:
            print(f"Ошибка микрофона: {e}")
        
        finally:
            self.is_listening = False
            self.microphone = None
    
    def recognize_audio(self, audio_data) -> str:
        """Распознать аудио данные через Google Speech API"""
        if not SPEECH_RECOGNITION_AVAILABLE:
            return ""
        
        try:
            recognizer = sr.Recognizer()
            text = recognizer.recognize_google(audio_data, language="ru-RU")
            return text
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print(f"Ошибка Google Speech API: {e}")
            return ""
        except Exception as e:
            print(f"Ошибка распознавания: {e}")
            return ""
    
    def get_next_phrase(self, timeout=1):
        """Получить следующую распознанную фразу"""
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_recognition_history(self, limit=10):
        """Получить историю распознавания"""
        return self.recognition_history[-limit:] if self.recognition_history else []
    
    def clear_history(self):
        """Очистить историю распознавания"""
        self.recognition_history.clear()
    
    def set_parameters(self, energy_threshold=None, pause_threshold=None, phrase_time_limit=None):
        """Установить параметры распознавания"""
        if energy_threshold is not None:
            self.energy_threshold = energy_threshold
        if pause_threshold is not None:
            self.pause_threshold = pause_threshold
        if phrase_time_limit is not None:
            self.phrase_time_limit = phrase_time_limit
    
    def add_view(self, view: IView) -> None:
        self.views.append(view)
    
    def notify_views(self, data: Any) -> None:
        for view in self.views:
            view.update(data)
    
    def update_view(self, data: Any) -> None:
        self.notify_views(data)

