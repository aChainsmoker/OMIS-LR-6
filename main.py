from application import SystemApplication
import os

def main():
    print("Запуск системы управления умным домом...")
    
    # Проверяем наличие JSON файлов
    if not os.path.exists("users.json"):
        print("Создаю файл users.json...")
    if not os.path.exists("devices.json"):
        print("Создаю файл devices.json...")
    
    # Создаем и запускаем приложение
    app = SystemApplication()
    app.run()

if __name__ == "__main__":
    main()