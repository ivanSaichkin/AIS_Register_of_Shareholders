# gui/main_window.py
from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QStatusBar, 
                             QMessageBox, QVBoxLayout, QWidget, QMenuBar, QMenu)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from gui.admin_tab import AdminTab
from gui.employee_tab import EmployeeTab
from gui.shareholder_tab import ShareholderTab
from gui.supervisor_tab import SupervisorTab
from gui.login_dialog import LoginDialog
from database.db_manager import DatabaseManager
from database.models import *

class MainWindow(QMainWindow):
    def __init__(self, db_manager: DatabaseManager, user_data: dict):
        super().__init__()
        self.db = db_manager
        self.user_data = user_data
        self.role = user_data['role']
        
        # Инициализация моделей
        self.company_model = CompanyModel(self.db)
        self.share_issue_model = ShareIssueModel(self.db)
        self.shareholder_model = ShareholderModel(self.db)
        self.account_model = AccountModel(self.db)
        self.operation_model = OperationModel(self.db)
        
        self.setup_ui()
        self.setup_menu()
        self.setWindowTitle(f"АИС Реестр акционеров - {self.get_role_name()}")
        self.setGeometry(100, 100, 1400, 800)
    
    def get_role_name(self):
        roles = {
            'admin': 'Администратор',
            'employee': 'Сотрудник АО',
            'shareholder': 'Акционер',
            'supervisor': 'Сотрудник надзора'
        }
        return roles.get(self.role, 'Пользователь')
    
    def setup_menu(self):
        """Создание меню"""
        menubar = self.menuBar()
        
        # Меню "Файл"
        file_menu = menubar.addMenu("Файл")
        
        # Действие "Сменить пользователя"
        logout_action = QAction("Сменить пользователя", self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)
        
        # Разделитель
        file_menu.addSeparator()
        
        # Действие "Выход"
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню "Справка"
        help_menu = menubar.addMenu("Справка")
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def logout(self):
        """Выход из текущего профиля и вход под другим"""
        reply = QMessageBox.question(self, "Подтверждение", 
            "Вы уверены, что хотите выйти из текущего профиля?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # Закрываем текущее окно
            self.close()
            
            # Открываем диалог авторизации заново
            login_dialog = LoginDialog(self.db)
            if login_dialog.exec():
                user_data = login_dialog.user_data
                new_window = MainWindow(self.db, user_data)
                new_window.show()
    
    def show_about(self):
        """Информация о программе"""
        QMessageBox.about(self, "О программе",
            "АИС «Реестр акционеров акционерного общества»\n\n"
            "Версия: 2.0\n\n"
            "Разработано в МГТУ им. Н.Э. Баумана\n"
            "Кафедра ИУ5 «Системы обработки информации и управления»\n\n"
            "Функциональность:\n"
            "• Управление акционерными обществами\n"
            "• Управление выпусками акций\n"
            "• Учет акционеров и лицевых счетов\n"
            "• Операции с акциями\n"
            "• Формирование отчетов с диаграммами\n"
            "• Экспорт отчетов в PDF")
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Добавление вкладок в зависимости от роли
        if self.role == 'admin':
            self.admin_tab = AdminTab(self)
            self.tab_widget.addTab(self.admin_tab, "Акционерные общества")
            self.tab_widget.addTab(self.admin_tab.share_issues_tab, "Выпуски акций")
            self.tab_widget.addTab(self.admin_tab.shareholders_tab, "Акционеры")
            self.tab_widget.addTab(self.admin_tab.accounts_tab, "Лицевые счета")
            self.tab_widget.addTab(self.admin_tab.reports_tab, "Отчеты")
            
        elif self.role == 'employee':
            self.employee_tab = EmployeeTab(self)
            self.tab_widget.addTab(self.employee_tab, "Мое АО")
            self.tab_widget.addTab(self.employee_tab.shares_tab, "Акции")
            self.tab_widget.addTab(self.employee_tab.reports_tab, "Отчеты")
            
        elif self.role == 'shareholder':
            self.shareholder_tab = ShareholderTab(self)
            self.tab_widget.addTab(self.shareholder_tab, "Мои данные")
            self.tab_widget.addTab(self.shareholder_tab.accounts_tab, "Мои счета")
            self.tab_widget.addTab(self.shareholder_tab.operations_tab, "Операции")
            
        elif self.role == 'supervisor':
            self.supervisor_tab = SupervisorTab(self)
            self.tab_widget.addTab(self.supervisor_tab, "Управление")
            self.tab_widget.addTab(self.supervisor_tab.shares_tab, "Акции")
            self.tab_widget.addTab(self.supervisor_tab.accounts_tab, "Счета")
        
        # Статус бар
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage(f"Добро пожаловать, {self.user_data['username']}!")
    
    def show_message(self, title: str, message: str, is_error: bool = False):
        if is_error:
            QMessageBox.critical(self, title, message)
        else:
            QMessageBox.information(self, title, message)
    
    def refresh_all_tabs(self):
        if hasattr(self, 'admin_tab'):
            self.admin_tab.refresh()
        elif hasattr(self, 'employee_tab'):
            self.employee_tab.refresh()
        elif hasattr(self, 'shareholder_tab'):
            self.shareholder_tab.refresh()
        elif hasattr(self, 'supervisor_tab'):
            self.supervisor_tab.refresh()