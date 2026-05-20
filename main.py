# main.py
import sys
from PyQt6.QtWidgets import QApplication
from database.db_manager import DatabaseManager
from gui.login_dialog import LoginDialog
from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Подключение к БД
    db_manager = DatabaseManager(
        host='localhost',
        database='shareholders_registry',
        user='ivan',
        password='123',
        port=5436
    )
    
    if not db_manager.connect():
        print("Ошибка подключения к базе данных")
        print("Убедитесь, что PostgreSQL запущен и база данных создана")
        sys.exit(1)
    
    # Авторизация
    login_dialog = LoginDialog(db_manager)
    
    if login_dialog.exec():
        user_data = login_dialog.user_data
        window = MainWindow(db_manager, user_data)
        window.show()
        sys.exit(app.exec())
    else:
        db_manager.disconnect()
        sys.exit(0)

if __name__ == "__main__":
    main()