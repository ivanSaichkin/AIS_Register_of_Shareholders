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
        self.setFixedSize(500, 280)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("АИС Реестр акционеров")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 20px; color: #1a237e;")
        layout.addWidget(title)
        
        # Выбор роли
        role_layout = QHBoxLayout()
        role_layout.addWidget(QLabel("Выберите роль:"))
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Администратор", "Сотрудник АО", "Акционер", "Сотрудник надзора"])
        self.role_combo.currentTextChanged.connect(self.on_role_changed)
        role_layout.addWidget(self.role_combo)
        layout.addLayout(role_layout)
        
        # Выбор пользователя
        user_layout = QHBoxLayout()
        user_layout.addWidget(QLabel("Пользователь:"))
        self.user_combo = QComboBox()
        self.user_combo.setEditable(True)
        self.user_combo.setMinimumWidth(300)
        user_layout.addWidget(self.user_combo)
        layout.addLayout(user_layout)
        
        # Информационная метка
        self.info_label = QLabel("Выберите роль и пользователя для входа")
        self.info_label.setStyleSheet("color: #666; font-size: 9px;")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)
        
        # Кнопки
        button_layout = QHBoxLayout()
        self.login_btn = QPushButton("Войти")
        self.login_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
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
        
        # Получение пользователей с данной ролью из БД
        users = self.user_model.db.execute_query(
            "SELECT username FROM users WHERE role = %s ORDER BY username",
            (role,)
        )
        
        if users:
            for user in users:
                self.user_combo.addItem(user['username'])
            self.info_label.setText(f"Доступно {len(users)} пользователей")
        else:
            # Если нет пользователей, показываем стандартных
            default_users = {
                'admin': ['admin'],
                'employee': [],
                'shareholder': [],
                'supervisor': ['supervisor']
            }
            for user in default_users.get(role, []):
                self.user_combo.addItem(user)
            
            if role == 'employee':
                self.info_label.setText("Нет сотрудников. Добавьте АО для автоматического создания пользователя")
            elif role == 'shareholder':
                self.info_label.setText("Нет акционеров. Добавьте акционера для автоматического создания пользователя")
            else:
                self.info_label.setText("Выберите пользователя из списка")
    
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
            # Для тестовых пользователей
            role = role_map[self.role_combo.currentText()]
            
            # Определяем company_id и shareholder_id для тестовых пользователей
            company_id = None
            shareholder_id = None
            
            if role == 'employee':
                # Пытаемся найти компанию по имени пользователя
                companies = self.user_model.db.execute_query(
                    "SELECT company_id, short_name FROM joint_stock_companies WHERE short_name ILIKE %s",
                    (f'%{username.split("_")[-1] if "_" in username else username}%',)
                )
                if companies:
                    company_id = companies[0]['company_id']
            
            elif role == 'shareholder':
                # Пытаемся найти акционера по имени
                shareholders = self.user_model.db.execute_query(
                    "SELECT shareholder_id, name FROM shareholders WHERE name ILIKE %s",
                    (f'%{username}%',)
                )
                if shareholders:
                    shareholder_id = shareholders[0]['shareholder_id']
            
            self.user_data = {
                'username': username,
                'role': role,
                'company_id': company_id or 1,
                'shareholder_id': shareholder_id or 1
            }
            self.accept()