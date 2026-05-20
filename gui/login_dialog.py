# gui/login_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
from database.models import UserModel

class LoginDialog(QDialog):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.user_model = UserModel(self.db)
        self.user_data = None
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Авторизация")
        self.setFixedSize(400, 200)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("АИС Реестр акционеров")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # Выбор роли
        role_layout = QHBoxLayout()
        role_layout.addWidget(QLabel("Выберите роль:"))
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Администратор", "Сотрудник АО", "Акционер", "Сотрудник надзора"])
        self.role_combo.currentTextChanged.connect(self.on_role_changed)
        role_layout.addWidget(self.role_combo)
        layout.addLayout(role_layout)
        
        # Выбор пользователя (для акционера - выбор по ФИО)
        user_layout = QHBoxLayout()
        user_layout.addWidget(QLabel("Пользователь:"))
        self.user_combo = QComboBox()
        self.user_combo.setEditable(True)
        user_layout.addWidget(self.user_combo)
        layout.addLayout(user_layout)
        
        # Кнопки
        button_layout = QHBoxLayout()
        self.login_btn = QPushButton("Войти")
        self.login_btn.clicked.connect(self.login)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.login_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.on_role_changed(self.role_combo.currentText())
    
    def on_role_changed(self, role_text):
        self.user_combo.clear()
        
        role_map = {
            "Администратор": "admin",
            "Сотрудник АО": "employee", 
            "Акционер": "shareholder",
            "Сотрудник надзора": "supervisor"
        }
        role = role_map[role_text]
        
        # Получение пользователей с данной ролью
        users = self.user_model.db.execute_query(
            "SELECT username FROM users WHERE role = %s",
            (role,)
        )
        
        if users:
            for user in users:
                self.user_combo.addItem(user['username'])
        else:
            # Для демонстрации добавляем тестовых пользователей
            test_users = {
                'admin': ['admin'],
                'employee': ['employee'],
                'shareholder': ['shareholder'],
                'supervisor': ['supervisor']
            }
            for user in test_users.get(role, []):
                self.user_combo.addItem(user)
    
    def login(self):
        username = self.user_combo.currentText()
        if not username:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя")
            return
        
        role_map = {
            "Администратор": "admin",
            "Сотрудник АО": "employee",
            "Акционер": "shareholder",
            "Сотрудник надзора": "supervisor"
        }
        
        user_data = self.user_model.authenticate(username)
        
        if user_data:
            self.user_data = user_data
            self.accept()
        else:
            # Для демонстрации создаем тестовые данные
            self.user_data = {
                'username': username,
                'role': role_map[self.role_combo.currentText()]
            }
            self.accept()