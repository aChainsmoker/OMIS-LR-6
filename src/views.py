import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any
from controllers import (
    IController, IView, AuthController, DeviceController,
    AnalysisController, DecisionController, ResponseController
)
from models import Device, AuthUser, Request, Analysis, Decision, Response
from patterns import MachineLearningStrategy, StatisticalAnalysisStrategy

class BaseView(ttk.Frame, IView):
    def __init__(self, controller: IController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.id = "base_view"
        if controller:
            controller.add_view(self)
    
    def display(self, data: Any) -> None:
        pass
    
    def update(self, data: Any) -> None:
        pass


class AuthView(BaseView):
    def __init__(self, controller: AuthController, parent=None):
        super().__init__(controller, parent)
        self.controller = controller
        self.setup_ui()
    
    def setup_ui(self):
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.title_label = ttk.Label(self.main_frame, text="🔐 Авторизация", font=('Arial', 16))
        self.title_label.pack(pady=20)
        
        # Поля ввода
        input_frame = ttk.Frame(self.main_frame)
        input_frame.pack(pady=10)
        
        ttk.Label(input_frame, text="Логин:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.username_entry = ttk.Entry(input_frame, width=30)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        self.username_entry.focus()
        
        ttk.Label(input_frame, text="Пароль:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.password_entry = ttk.Entry(input_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Кнопки
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(pady=20)
        
        self.login_btn = ttk.Button(btn_frame, text="Войти", command=self.login)
        self.login_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Регистрация", command=self.show_register).pack(side=tk.LEFT, padx=5)
        
        # Статус
        self.status_label = ttk.Label(self.main_frame, text="", foreground="red")
        self.status_label.pack(pady=10)
        
        # Привязка Enter к входу
        self.username_entry.bind('<Return>', lambda e: self.login())
        self.password_entry.bind('<Return>', lambda e: self.login())
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            self.status_label.config(text="Заполните все поля")
            return
        
        user = self.controller.login(username, password)
        if user:
            self.status_label.config(text=f"Добро пожаловать, {user.full_name}!", foreground="green")
            self.master.event_generate('<<LoginSuccess>>')
    
    def logout(self):
        self.controller.logout()
        self.reset_form()
    
    def reset_form(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.status_label.config(text="")
        self.username_entry.focus()
    
    def show_register(self):
        # Диалог регистрации
        dialog = tk.Toplevel(self)
        dialog.title("Регистрация")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Регистрация нового пользователя", font=('Arial', 14)).pack(pady=10)
        
        # Поля для регистрации
        fields_frame = ttk.Frame(dialog)
        fields_frame.pack(pady=10, padx=20)
        
        ttk.Label(fields_frame, text="Логин:").grid(row=0, column=0, pady=5, sticky=tk.W)
        reg_username = ttk.Entry(fields_frame, width=25)
        reg_username.grid(row=0, column=1, pady=5)
        
        ttk.Label(fields_frame, text="Пароль:").grid(row=1, column=0, pady=5, sticky=tk.W)
        reg_password = ttk.Entry(fields_frame, width=25, show="*")
        reg_password.grid(row=1, column=1, pady=5)
        
        ttk.Label(fields_frame, text="Подтверждение:").grid(row=2, column=0, pady=5, sticky=tk.W)
        reg_confirm = ttk.Entry(fields_frame, width=25, show="*")
        reg_confirm.grid(row=2, column=1, pady=5)
        
        ttk.Label(fields_frame, text="Полное имя:").grid(row=3, column=0, pady=5, sticky=tk.W)
        reg_fullname = ttk.Entry(fields_frame, width=25)
        reg_fullname.grid(row=3, column=1, pady=5)
        
        status_label = ttk.Label(dialog, text="", foreground="red")
        status_label.pack(pady=5)
        
        def register():
            username = reg_username.get()
            password = reg_password.get()
            confirm = reg_confirm.get()
            fullname = reg_fullname.get()
            
            if not all([username, password, confirm]):
                status_label.config(text="Заполните все поля")
                return
            
            if password != confirm:
                status_label.config(text="Пароли не совпадают")
                return
            
            new_user = AuthUser(
                username=username,
                password=password,
                role="user",
                full_name=fullname or username
            )
            
            if self.controller.add_user(new_user):
                messagebox.showinfo("Успех", f"Пользователь {username} зарегистрирован")
                dialog.destroy()
            else:
                status_label.config(text="Пользователь уже существует")
        
        ttk.Button(dialog, text="Зарегистрировать", command=register).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack()
    
    def display(self, data: Any) -> None:
        pass
    
    def update(self, data: Any) -> None:
        if isinstance(data, dict):
            if data.get('type') == 'login_failed':
                self.status_label.config(text=data.get('message', 'Ошибка авторизации'))
            elif data.get('type') == 'user_added':
                messagebox.showinfo("Успех", f"Пользователь {data['user'].username} добавлен")

class DeviceView(BaseView):
    def __init__(self, controller: DeviceController, parent=None):
        super().__init__(controller, parent)
        self.controller = controller
        self.setup_ui()
        self.refresh_devices()
    
    def setup_ui(self):
        # Заголовок
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text="📱 Управление устройствами", 
                 font=('Arial', 16)).pack(side=tk.LEFT)
        
        # Таблица устройств
        self.tree_frame = ttk.Frame(self)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("ID", "Название", "Тип", "Статус", "Подключение")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления (все внизу)
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="➕ Добавить устройство", 
                  command=self.add_device).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 Обновить", 
                  command=self.refresh_devices).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✏️ Редактировать", 
                  command=self.edit_device).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Удалить выбранное", 
                  command=self.delete_device).pack(side=tk.LEFT, padx=5)
    
    def refresh_devices(self):
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Загружаем устройства
        devices = self.controller.get_all_devices()
        for device in devices:
            self.tree.insert("", tk.END, iid=device.id, values=(
                device.id,
                device.name,
                device.type,
                device.status,
                device.connection_info
            ))
    
    def add_device(self):
        dialog = tk.Toplevel(self)
        dialog.title("Добавить устройство")
        dialog.geometry("400x350")
        dialog.transient(self)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Новое устройство", font=('Arial', 14)).pack(pady=10)
        
        fields_frame = ttk.Frame(dialog)
        fields_frame.pack(pady=10, padx=20)
        
        fields = [
            ("ID устройства:", "entry"),
            ("Название:", "entry"),
            ("Тип:", "combobox", ["сенсор", "актуатор", "камера", "динамик", "микрофон", "контроллер"]),
            ("Статус:", "combobox", ["online", "offline", "error", "обслуживание"]),
            ("Информация о подключении:", "entry")
        ]
        
        entries = {}
        for i, (label, field_type, *options) in enumerate(fields):
            ttk.Label(fields_frame, text=label).grid(row=i, column=0, pady=5, sticky=tk.W)
            
            if field_type == "entry":
                entry = ttk.Entry(fields_frame, width=25)
                entry.grid(row=i, column=1, pady=5)
                entries[label] = entry
            elif field_type == "combobox":
                combo = ttk.Combobox(fields_frame, values=options[0], width=22)
                combo.grid(row=i, column=1, pady=5)
                combo.set(options[0][0])
                entries[label] = combo
        
        status_label = ttk.Label(dialog, text="", foreground="red")
        status_label.pack(pady=5)
        
        def save_device():
            device_id = entries["ID устройства:"].get()
            name = entries["Название:"].get()
            device_type = entries["Тип:"].get()
            status = entries["Статус:"].get()
            connection = entries["Информация о подключении:"].get()
            
            if not all([device_id, name, device_type, status]):
                status_label.config(text="Заполните обязательные поля")
                return
            
            device = Device(
                id=device_id,
                name=name,
                type=device_type,
                status=status,
                connection_info=connection or ""
            )
            
            if self.controller.add_device(device):
                dialog.destroy()
                self.refresh_devices()
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Сохранить", command=save_device).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def delete_device(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите устройство для удаления")
            return
        
        try:
            selected_item = selection[0]
            # Используем iid как device_id (мы установили его при создании)
            device_id = selected_item
            item_values = self.tree.item(selected_item)['values']
            
            if item_values and len(item_values) >= 2:
                device_name = str(item_values[1])
            else:
                # Fallback: используем iid как имя
                device_name = str(device_id)
            
            if messagebox.askyesno("Подтверждение", f"Удалить устройство '{device_name}'?"):
                if self.controller.delete_device(str(device_id)):
                    messagebox.showinfo("Успех", "Устройство успешно удалено")
                    self.refresh_devices()
                else:
                    messagebox.showerror("Ошибка", "Не удалось удалить устройство")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении устройства: {str(e)}")
    
    def edit_device(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите устройство для редактирования")
            return
        
        try:
            selected_item = selection[0]
            # Используем iid как device_id (мы установили его при создании)
            device_id = selected_item
            item_values = self.tree.item(selected_item)['values']
            
            # Fallback: берем из values если iid не работает
            if item_values and len(item_values) >= 1:
                # Проверяем, что iid совпадает с первым значением
                if str(item_values[0]) != str(device_id):
                    device_id = str(item_values[0])
            
            device = self.controller.get_device_by_id(str(device_id))
            
            if not device:
                messagebox.showerror("Ошибка", "Устройство не найдено")
                return
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при получении данных устройства: {str(e)}")
            return
        
        dialog = tk.Toplevel(self)
        dialog.title("Редактировать устройство")
        dialog.geometry("400x350")
        dialog.transient(self)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Редактирование устройства", font=('Arial', 14)).pack(pady=10)
        
        fields_frame = ttk.Frame(dialog)
        fields_frame.pack(pady=10, padx=20)
        
        fields = [
            ("ID устройства:", "entry", device.id, True),
            ("Название:", "entry", device.name, False),
            ("Тип:", "combobox", ["сенсор", "актуатор", "камера", "динамик", "микрофон", "контроллер"], device.type),
            ("Статус:", "combobox", ["online", "offline", "error", "обслуживание"], device.status),
            ("Информация о подключении:", "entry", device.connection_info, False)
        ]
        
        entries = {}
        for i, (label, field_type, *values) in enumerate(fields):
            ttk.Label(fields_frame, text=label).grid(row=i, column=0, pady=5, sticky=tk.W)
            
            if field_type == "entry":
                entry = ttk.Entry(fields_frame, width=25)
                entry.insert(0, values[0])
                entry.grid(row=i, column=1, pady=5)
                if len(values) > 1 and values[1]:  # Если readonly
                    entry.config(state='disabled')
                entries[label] = entry
            elif field_type == "combobox":
                combo = ttk.Combobox(fields_frame, values=values[0], width=22)
                combo.grid(row=i, column=1, pady=5)
                combo.set(values[1])
                entries[label] = combo
        
        def save_changes():
            name = entries["Название:"].get()
            device_type = entries["Тип:"].get()
            status = entries["Статус:"].get()
            connection = entries["Информация о подключении:"].get()
            
            if not all([name, device_type, status]):
                messagebox.showerror("Ошибка", "Заполните обязательные поля")
                return
            
            updated_device = Device(
                id=device.id,
                name=name,
                type=device_type,
                status=status,
                connection_info=connection or ""
            )
            
            if self.controller.update_device(updated_device):
                messagebox.showinfo("Успех", "Устройство успешно обновлено")
                dialog.destroy()
                self.refresh_devices()
            else:
                messagebox.showerror("Ошибка", "Не удалось обновить устройство")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Сохранить", command=save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def display(self, data: Any) -> None:
        pass
    
    def update(self, data: Any) -> None:
        if isinstance(data, dict):
            if data.get('type') in ['device_added', 'device_updated', 'device_deleted']:
                self.refresh_devices()


class AnalysisView(BaseView):
    def __init__(self, controller: AnalysisController, parent=None):
        super().__init__(controller, parent)
        self.controller = controller
        self.setup_ui()
    
    def setup_ui(self):
        ttk.Label(self, text="Анализ данных", font=('Arial', 14)).pack(pady=10)
        self.analysis_text = tk.Text(self, height=10, width=50)
        self.analysis_text.pack(pady=5)
        
        ttk.Button(self, text="Выполнить ML анализ", 
                  command=self.perform_ml_analysis).pack(pady=2)
        ttk.Button(self, text="Выполнить статистический анализ", 
                  command=self.perform_stat_analysis).pack(pady=2)
    
    def perform_ml_analysis(self):
        self.controller.set_strategy(MachineLearningStrategy())
        # Здесь должен быть запрос и данные
        request = Request(id="test", language="ru", purpose="test", recognition_accuracy=95)
        analysis = self.controller.perform_analysis(request)
        self.display(analysis)
    
    def perform_stat_analysis(self):
        self.controller.set_strategy(StatisticalAnalysisStrategy())
        request = Request(id="test", language="ru", purpose="test", recognition_accuracy=95)
        analysis = self.controller.perform_analysis(request)
        self.display(analysis)
    
    def display(self, data: Any) -> None:
        if isinstance(data, Analysis):
            text = f"Анализ ID: {data.id}\nРезультат: {data.result}\nДоверие: {data.confidence}"
            self.analysis_text.delete(1.0, tk.END)
            self.analysis_text.insert(1.0, text)
    
    def update(self, data: Any) -> None:
        self.display(data)

class DecisionView(BaseView):
    def __init__(self, controller: DecisionController, parent=None):
        super().__init__(controller, parent)
        self.controller = controller
        self.setup_ui()
    
    def setup_ui(self):
        ttk.Label(self, text="Принятие решений", font=('Arial', 14)).pack(pady=10)
        self.decision_text = tk.Text(self, height=10, width=50)
        self.decision_text.pack(pady=5)
        
        ttk.Button(self, text="Сформировать решение", 
                  command=self.make_decision).pack(pady=5)
    
    def make_decision(self):
        analysis = Analysis(id="test", result="Тестовый анализ", confidence=0.9)
        decision = self.controller.make_decision(analysis)
        self.display(decision)
    
    def display(self, data: Any) -> None:
        if isinstance(data, Decision):
            text = f"Решение ID: {data.id}\nЯзык: {data.language}\nСообщение: {data.message}"
            self.decision_text.delete(1.0, tk.END)
            self.decision_text.insert(1.0, text)
    
    def update(self, data: Any) -> None:
        self.display(data)

class ResponseView(BaseView):
    def __init__(self, controller: ResponseController, parent=None):
        super().__init__(controller, parent)
        self.controller = controller
        self.setup_ui()
    
    def setup_ui(self):
        ttk.Label(self, text="Формирование ответов", font=('Arial', 14)).pack(pady=10)
        self.response_text = tk.Text(self, height=10, width=50)
        self.response_text.pack(pady=5)
        
        ttk.Button(self, text="Сформировать ответ", 
                  command=self.generate_response).pack(pady=5)
        ttk.Button(self, text="Отменить последний ответ", 
                  command=self.undo_response).pack(pady=2)
    
    def generate_response(self):
        decision = Decision(id="test", language="ru", message="Тестовое решение")
        response = self.controller.generate_response(decision)
        self.display(response)
    
    def undo_response(self):
        if self.controller.commands:
            command = self.controller.commands.pop()
            command.undo()
    
    def display(self, data: Any) -> None:
        if isinstance(data, Response):
            text = f"Ответ ID: {data.id}\nЯзык: {data.language}\nСообщение: {data.message}"
            self.response_text.delete(1.0, tk.END)
            self.response_text.insert(1.0, text)
    
    def update(self, data: Any) -> None:
        self.display(data)

