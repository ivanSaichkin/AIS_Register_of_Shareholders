# gui/main_window.py
from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QStatusBar, 
                             QMessageBox, QVBoxLayout, QWidget)
from PyQt6.QtCore import Qt
from gui.admin_tab import AdminTab
from gui.employee_tab import EmployeeTab
from gui.shareholder_tab import ShareholderTab
from gui.supervisor_tab import SupervisorTab
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