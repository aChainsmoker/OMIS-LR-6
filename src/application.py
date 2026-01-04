import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Dict, Any
import threading
import time
import os

from models import (
    SoundRepository, SensorDataRepository, RequestRepository,
    DecisionRepository, ResponseRepository, AuthRepository, DeviceRepository
)
from factories import ControllerFactory, ViewFactory

class SystemApplication:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Система Управления - Умный Дом с распознаванием речи")
        self.root.geometry("1100x850")
        
        # Создаем репозитории
        self.repositories = {
            'sound': SoundRepository(),
            'sensor': SensorDataRepository(),
            'request': RequestRepository(),
            'decision': DecisionRepository(),
            'response': ResponseRepository(),
            'auth': AuthRepository(),
            'device': DeviceRepository()
        }
        
        # Создаем контроллеры через фабрику
        self.controllers = ControllerFactory.create_controllers(self.repositories)
        
        # Создаем контейнеры для UI
        self.setup_ui()
        
        # Создаем представления через фабрику (теперь передаем content_container)
        self.views = ViewFactory.create_views(self.controllers, self.content_container)
        
        # Текущее состояние и пользователь
        self.current_state = "auth"  # Начинаем с авторизации
        self.current_user = None
        
        # Переменные для голосового управления
        self.voice_command_mode = False
        self.last_voice_command = ""
        
        self.show_auth_state()
        
        # Обработчики событий авторизации
        self.root.bind('<<LoginSuccess>>', self.on_login_success)
        
        # Запускаем фоновый поток для проверки голосовых команд
        self.start_voice_input_checker()
    
    def setup_ui(self):
        # Создаем главный контейнер
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Создаем контейнер для навигации (будет скрыт до авторизации)
        self.nav_container = ttk.Frame(self.main_container)
        
        # Создаем контейнер для содержимого
        self.content_container = ttk.Frame(self.main_container)
        self.content_container.pack(fill=tk.BOTH, expand=True)
    
    def clear_content_container(self):
        """Очищает контейнер содержимого"""
        for widget in self.content_container.winfo_children():
            widget.pack_forget()  # Используем pack_forget вместо destroy
    
    def on_login_success(self, event=None):
        """Обработчик успешной авторизации"""
        auth_controller = self.controllers['auth']
        self.current_user = auth_controller.get_current_user()
        
        if self.current_user:
            # Скрываем интерфейс авторизации
            self.clear_content_container()
            
            # Создаем и показываем панель навигации
            self.create_navigation()
            self.nav_container.pack(fill=tk.X, padx=10, pady=5)
            
            # Показываем состояние диалога
            self.show_dialog_state()
    
    def create_navigation(self):
        """Создает панель навигации"""
        # Очищаем навигационный контейнер
        for widget in self.nav_container.winfo_children():
            widget.destroy()
        
        # Информация о пользователе
        user_frame = ttk.Frame(self.nav_container)
        user_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(user_frame, text=f"👤 {self.current_user.full_name}", 
                 font=('Arial', 10)).pack(side=tk.LEFT)
        
        # Индикатор голосовых команд
        if hasattr(self, 'voice_command_mode') and self.voice_command_mode:
            voice_indicator = ttk.Label(user_frame, text="🎤 ВКЛ", foreground="green")
            voice_indicator.pack(side=tk.LEFT, padx=5)
        
        # Кнопки навигации
        nav_frame = ttk.Frame(self.nav_container)
        nav_frame.pack(side=tk.LEFT, expand=True)
        
        nav_buttons = [
            ("💬 Диалог", self.show_dialog_state),
            ("📊 Анализ", self.show_analysis_state),
            ("🎯 Решения", self.show_decision_state),
            ("📝 Ответы", self.show_response_state),
            ("📱 Устройства", self.show_device_state),
            ("⚙️ Настройки", self.show_settings_state)
        ]
        
        for text, command in nav_buttons:
            ttk.Button(nav_frame, text=text, command=command).pack(side=tk.LEFT, padx=2)
        
        # Кнопка выхода
        exit_frame = ttk.Frame(self.nav_container)
        exit_frame.pack(side=tk.RIGHT, padx=10)
        
        ttk.Button(exit_frame, text="🚪 Выход", 
                  command=self.logout).pack()
    
    def logout(self):
        """Выход из системы"""
        auth_controller = self.controllers['auth']
        auth_controller.logout()
        self.current_user = None
        
        # Скрываем навигацию
        self.nav_container.pack_forget()
        
        # Показываем авторизацию
        self.show_auth_state()
    
    def show_auth_state(self):
        """Показывает интерфейс авторизации"""
        self.current_state = "auth"
        self.clear_content_container()
        
        # Показываем представление авторизации
        self.views['auth'].pack(in_=self.content_container, fill=tk.BOTH, expand=True)
    
    def show_dialog_state(self):
        """Показывает интерфейс диалога"""
        if not self.current_user:
            self.show_auth_state()
            return
            
        self.current_state = "dialog"
        self.clear_content_container()
        
        # Создаем интерфейс диалога
        dialog_frame = ttk.Frame(self.content_container)
        dialog_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заголовок
        ttk.Label(dialog_frame, text="💬 Чат-система с голосовым управлением", 
                 font=('Arial', 16)).pack(pady=20)
        
        # Поле чата (только для чтения)
        chat_frame = ttk.Frame(dialog_frame)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.chat_text = tk.Text(chat_frame, height=20, state='disabled', wrap=tk.WORD)
        self.chat_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(chat_frame, command=self.chat_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_text.config(yscrollcommand=scrollbar.set)
        
        # Панель ввода
        input_frame = ttk.Frame(dialog_frame)
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.input_entry = ttk.Entry(input_frame, width=50)
        self.input_entry.pack(side=tk.LEFT, padx=5)
        self.input_entry.bind('<Return>', self.send_message)
        
        ttk.Button(input_frame, text="Отправить", 
                  command=self.send_message).pack(side=tk.LEFT, padx=5)
        
        # Кнопка голосового ввода
        btn_text = "🎤 Голосовой ввод ВКЛ" if self.voice_command_mode else "🎤 Голосовой ввод"
        self.voice_input_btn = ttk.Button(input_frame, text=btn_text, 
                  command=self.toggle_voice_commands)
        self.voice_input_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(input_frame, text="🧹 Очистить чат", 
                  command=self.clear_chat).pack(side=tk.LEFT, padx=5)
        
        # Статус синхронизации
        ttk.Label(dialog_frame, text="🔄 Синхронизация с устройствами каждые 30 сек", 
                 font=('Arial', 10)).pack(pady=5)
        
        # Подключенные устройства
        self.update_device_list()
    
    def show_device_state(self):
        """Показывает интерфейс управления устройствами"""
        if not self.current_user:
            self.show_auth_state()
            return
            
        self.current_state = "device"
        self.clear_content_container()
        
        # Показываем представление устройств
        self.views['device'].pack(in_=self.content_container, fill=tk.BOTH, expand=True)
    
    def show_analysis_state(self):
        """Показывает интерфейс анализа"""
        if not self.current_user:
            self.show_auth_state()
            return
            
        self.current_state = "analysis"
        self.clear_content_container()
        
        # Показываем представление анализа
        self.views['analysis'].pack(in_=self.content_container, fill=tk.BOTH, expand=True)
    
    def show_decision_state(self):
        """Показывает интерфейс решений"""
        if not self.current_user:
            self.show_auth_state()
            return
            
        self.current_state = "decision"
        self.clear_content_container()
        
        # Показываем представление решений
        self.views['decision'].pack(in_=self.content_container, fill=tk.BOTH, expand=True)
    
    def show_response_state(self):
        """Показывает интерфейс ответов"""
        if not self.current_user:
            self.show_auth_state()
            return
            
        self.current_state = "response"
        self.clear_content_container()
        
        # Показываем представление ответов
        self.views['response'].pack(in_=self.content_container, fill=tk.BOTH, expand=True)
    
    def show_settings_state(self):
        """Показывает интерфейс настроек"""
        if not self.current_user:
            self.show_auth_state()
            return
            
        self.current_state = "settings"
        self.clear_content_container()
        
        # Создаем интерфейс настроек
        settings_frame = ttk.Frame(self.content_container)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(settings_frame, text="⚙️ Настройки системы", 
                 font=('Arial', 16)).pack(pady=20)
        
        # Настройки стиля
        style_frame = ttk.LabelFrame(settings_frame, text="Настройки стиля")
        style_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(style_frame, text="Голос системы:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Combobox(style_frame, values=["Мужской", "Женский", "Нейтральный"]).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(style_frame, text="Тембр:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Scale(style_frame, from_=0, to=100, orient=tk.HORIZONTAL).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(style_frame, text="Скорость:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Scale(style_frame, from_=0, to=100, orient=tk.HORIZONTAL).grid(row=2, column=1, padx=5, pady=5)
        
        # Специальные команды
        cmd_frame = ttk.LabelFrame(settings_frame, text="Специальные команды")
        cmd_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(cmd_frame, text="Ключевое слово:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(cmd_frame, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(cmd_frame, text="Добавить команду").grid(row=1, column=0, columnspan=2, pady=10)
        
        # Кнопки управления
        btn_frame = ttk.Frame(settings_frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="💾 Сохранить", 
                  command=self.save_settings).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="↩️ Назад", 
                  command=self.show_dialog_state).pack(side=tk.LEFT, padx=10)
    
    def send_message(self, event=None):
        """Отправляет сообщение в чат"""
        message = self.input_entry.get()
        if message and self.current_user:
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Временно включаем текстовое поле для вставки
            self.chat_text.config(state='normal')
            self.chat_text.insert(tk.END, f"[{timestamp}] Вы: {message}\n")
            
            # Имитация ответа системы
            response = "Принято в обработку. Анализирую запрос..."
            self.chat_text.insert(tk.END, f"[{timestamp}] Система: {response}\n")
            
            # Прокрутка вниз
            self.chat_text.see(tk.END)
            # Отключаем редактирование обратно
            self.chat_text.config(state='disabled')
            
            self.input_entry.delete(0, tk.END)
    
    def start_voice_input_checker(self):
        """Запускает фоновый поток для автоматической отправки распознанной речи в чат"""
        def check_voice_input():
            while True:
                if hasattr(self, 'controllers') and 'speech' in self.controllers:
                    phrase = self.controllers['speech'].get_next_phrase(timeout=0.5)
                    if phrase and self.current_user and self.voice_command_mode:
                        # Автоматически отправляем распознанную речь в чат
                        if hasattr(self, 'chat_text') and self.current_state == "dialog":
                            self.root.after(0, lambda text=phrase: self.send_voice_message(text))
                time.sleep(0.1)
        
        thread = threading.Thread(target=check_voice_input, daemon=True)
        thread.start()
    
    def send_voice_message(self, text: str):
        """Отправить распознанную речь напрямую в чат"""
        if not text or not self.current_user:
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Временно включаем текстовое поле для вставки
        self.chat_text.config(state='normal')
        self.chat_text.insert(tk.END, f"[{timestamp}] Вы (голос): {text}\n")
        
        # Имитация ответа системы
        response = "Принято в обработку. Анализирую запрос..."
        self.chat_text.insert(tk.END, f"[{timestamp}] Система: {response}\n")
        
        # Прокрутка вниз
        self.chat_text.see(tk.END)
        # Отключаем редактирование обратно
        self.chat_text.config(state='disabled')
    
    def add_to_chat(self, message: str):
        """Добавить сообщение в чат"""
        if hasattr(self, 'chat_text'):
            timestamp = time.strftime("%H:%M:%S")
            self.chat_text.config(state='normal')
            self.chat_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.chat_text.see(tk.END)
            self.chat_text.config(state='disabled')
    
    def toggle_voice_commands(self):
        """Включить/выключить голосовой ввод (через кнопку Голосовой ввод)"""
        self.voice_command_mode = not self.voice_command_mode
        
        if self.voice_command_mode:
            self.voice_input_btn.config(text="🎤 Голосовой ввод ВКЛ")
            
            # Автоматически запускаем распознавание
            speech_controller = self.controllers['speech']
            if not speech_controller.is_listening:
                speech_controller.start_listening()
            
            self.add_to_chat("🤖 Голосовой ввод активирован. Говорите, ваши слова будут автоматически отправлены в чат.")
        else:
            self.voice_input_btn.config(text="🎤 Голосовой ввод")
            
            # Останавливаем распознавание
            speech_controller = self.controllers['speech']
            if speech_controller.is_listening:
                speech_controller.stop_listening()
            
            self.add_to_chat("🤖 Голосовой ввод отключен.")
    
    def update_device_list(self):
        """Обновить список устройств в диалоге"""
        if hasattr(self, 'current_state') and self.current_state == "dialog":
            device_controller = self.controllers['device']
            devices = device_controller.get_all_devices()
            online_devices = [d for d in devices if d.status == 'online']
            
            # Создаем или обновляем фрейм устройств
            if hasattr(self, 'device_frame'):
                try:
                    self.device_frame.destroy()
                except:
                    pass
            
            if online_devices:
                # Находим dialog_frame
                dialog_frame = None
                for widget in self.content_container.winfo_children():
                    if isinstance(widget, ttk.Frame):
                        dialog_frame = widget
                        break
                
                if dialog_frame:
                    self.device_frame = ttk.LabelFrame(dialog_frame, text="✅ Подключенные устройства")
                    self.device_frame.pack(fill=tk.X, padx=20, pady=10)
                    
                    for device in online_devices[:3]:
                        ttk.Label(self.device_frame, 
                                 text=f"• {device.name} ({device.type}) - {device.connection_info}").pack(anchor=tk.W)
                    
                    if len(online_devices) > 3:
                        ttk.Label(self.device_frame, 
                                 text=f"... и ещё {len(online_devices) - 3} устройств").pack(anchor=tk.W)
        
        # Планируем следующее обновление через 30 секунд
        if hasattr(self, 'root'):
            self.root.after(30000, self.update_device_list)
    
    
    def clear_chat(self):
        """Очищает чат"""
        if hasattr(self, 'chat_text'):
            self.chat_text.config(state='normal')
            self.chat_text.delete(1.0, tk.END)
            self.chat_text.config(state='disabled')
    
    def save_settings(self):
        """Сохраняет настройки"""
        messagebox.showinfo("Настройки", "Настройки успешно сохранены")
        self.show_dialog_state()
    
    def run(self):
        """Запускает приложение"""
        self.root.mainloop()

# ====================== КОНТЕЙНЕР ЗАВИСИМОСТЕЙ ======================

class DependencyContainer:
    def __init__(self):
        self.registry = {}
    
    def register(self, interface, implementation):
        self.registry[interface] = implementation
    
    def resolve(self, interface):
        if interface in self.registry:
            return self.registry[interface]()
        raise ValueError(f"Не зарегистрировано: {interface}")

class SystemConfigurator:
    def __init__(self):
        self.container = DependencyContainer()
        self.setup_dependencies()
    
    def setup_dependencies(self):
        from patterns import IAnalysisStrategy, MachineLearningStrategy
        # Регистрируем репозитории
        self.container.register(SoundRepository, SoundRepository)
        self.container.register(SensorDataRepository, SensorDataRepository)
        self.container.register(RequestRepository, RequestRepository)
        self.container.register(DecisionRepository, DecisionRepository)
        self.container.register(ResponseRepository, ResponseRepository)
        self.container.register(AuthRepository, AuthRepository)
        self.container.register(DeviceRepository, DeviceRepository)
        
        # Регистрируем стратегии
        self.container.register(IAnalysisStrategy, MachineLearningStrategy)
    
    def create_repositories(self) -> Dict[str, Any]:
        repos = {
            'sound': self.container.resolve(SoundRepository),
            'sensor': self.container.resolve(SensorDataRepository),
            'request': self.container.resolve(RequestRepository),
            'decision': self.container.resolve(DecisionRepository),
            'response': self.container.resolve(ResponseRepository),
            'auth': self.container.resolve(AuthRepository),
            'device': self.container.resolve(DeviceRepository)
        }
        return repos
    
    def create_controllers(self, repos: Dict) -> Dict:
        return ControllerFactory.create_controllers(repos)
    
    def link_components(self):
        # Дополнительная логика связывания компонентов
        pass

