# gui/supervisor_tab.py - ПОЛНОСТЬЮ ИСПРАВЛЕННАЯ ВЕРСИЯ
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QGroupBox, 
                             QLineEdit, QLabel, QFormLayout, QComboBox,
                             QDateEdit, QMessageBox, QTabWidget)
from PyQt6.QtCore import Qt, QDate
from gui.dialogs import ShareIssueDialog, CompanyDialog, ShareholderDialog, OperationDialog

class SupervisorTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # Вкладки
        self.tab_widget = QTabWidget()
        
        # ==================== ВКЛАДКА УПРАВЛЕНИЯ ====================
        self.manage_tab = QWidget()
        manage_layout = QVBoxLayout()
        
        # Добавление АО
        add_company_group = QGroupBox("Добавление акционерного общества")
        add_company_layout = QHBoxLayout()
        self.add_company_btn = QPushButton("Добавить АО")
        self.add_company_btn.setStyleSheet("background-color: #2196F3; color: white;")
        self.add_company_btn.clicked.connect(self.add_company)
        add_company_layout.addWidget(self.add_company_btn)
        add_company_layout.addStretch()
        add_company_group.setLayout(add_company_layout)
        manage_layout.addWidget(add_company_group)
        
        # Добавление акционера
        add_shareholder_group = QGroupBox("Добавление акционера")
        add_shareholder_layout = QHBoxLayout()
        self.add_shareholder_btn = QPushButton("Добавить акционера")
        self.add_shareholder_btn.setStyleSheet("background-color: #2196F3; color: white;")
        self.add_shareholder_btn.clicked.connect(self.add_shareholder)
        add_shareholder_layout.addWidget(self.add_shareholder_btn)
        add_shareholder_layout.addStretch()
        add_shareholder_group.setLayout(add_shareholder_layout)
        manage_layout.addWidget(add_shareholder_group)
        
        # Добавление операции (теперь с выбором выпуска акций)
        add_operation_group = QGroupBox("Добавление операции по лицевому счету")
        add_operation_layout = QVBoxLayout()
        
        # Информационная метка
        info_label = QLabel("Нажмите кнопку для открытия диалога добавления операции")
        info_label.setStyleSheet("color: #666; margin: 5px;")
        add_operation_layout.addWidget(info_label)
        
        btn_layout = QHBoxLayout()
        self.add_operation_btn = QPushButton("Открыть диалог добавления операции")
        self.add_operation_btn.setStyleSheet("background-color: #4CAF50; color: white; font-size: 12px; padding: 8px;")
        self.add_operation_btn.clicked.connect(self.add_operation)
        btn_layout.addWidget(self.add_operation_btn)
        btn_layout.addStretch()
        add_operation_layout.addLayout(btn_layout)
        
        add_operation_group.setLayout(add_operation_layout)
        manage_layout.addWidget(add_operation_group)
        
        manage_layout.addStretch()
        self.manage_tab.setLayout(manage_layout)
        self.tab_widget.addTab(self.manage_tab, "Управление")
        
        # ==================== ВКЛАДКА АКЦИЙ ====================
        self.shares_tab = QWidget()
        shares_layout = QVBoxLayout()
        
        shares_group = QGroupBox("Ранее зарегистрированные акции")
        shares_table_layout = QVBoxLayout()
        
        self.shares_table = QTableWidget()
        self.shares_table.setColumnCount(7)
        self.shares_table.setHorizontalHeaderLabels(
            ["Компания", "Рег. номер", "Дата", "Тип", "Категория", "Кол-во", "Номинал"]
        )
        shares_table_layout.addWidget(self.shares_table)
        
        shares_buttons = QHBoxLayout()
        self.edit_share_btn = QPushButton("Редактировать")
        self.edit_share_btn.clicked.connect(self.edit_share)
        self.delete_share_btn = QPushButton("Удалить")
        self.delete_share_btn.clicked.connect(self.delete_share)
        shares_buttons.addWidget(self.edit_share_btn)
        shares_buttons.addWidget(self.delete_share_btn)
        shares_buttons.addStretch()
        shares_table_layout.addLayout(shares_buttons)
        
        shares_group.setLayout(shares_table_layout)
        shares_layout.addWidget(shares_group)
        
        self.shares_tab.setLayout(shares_layout)
        self.tab_widget.addTab(self.shares_tab, "Акции")
        
        # ==================== ВКЛАДКА СЧЕТОВ ====================
        self.accounts_tab = QWidget()
        accounts_layout = QVBoxLayout()
        
        accounts_group = QGroupBox("Ранее зарегистрированные лицевые счета")
        accounts_table_layout = QVBoxLayout()
        
        self.accounts_table = QTableWidget()
        self.accounts_table.setColumnCount(6)
        self.accounts_table.setHorizontalHeaderLabels(
            ["Акционер", "Номер счета", "Дата открытия", "Дата закрытия", "Остаток", "Статус"]
        )
        accounts_table_layout.addWidget(self.accounts_table)
        
        accounts_buttons = QHBoxLayout()
        self.edit_account_btn = QPushButton("Редактировать")
        self.edit_account_btn.clicked.connect(self.edit_account)
        self.delete_account_btn = QPushButton("Удалить")
        self.delete_account_btn.clicked.connect(self.delete_account)
        accounts_buttons.addWidget(self.edit_account_btn)
        accounts_buttons.addWidget(self.delete_account_btn)
        accounts_buttons.addStretch()
        accounts_table_layout.addLayout(accounts_buttons)
        
        accounts_group.setLayout(accounts_table_layout)
        accounts_layout.addWidget(accounts_group)
        
        self.accounts_tab.setLayout(accounts_layout)
        self.tab_widget.addTab(self.accounts_tab, "Счета")
        
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)
    
    def load_data(self):
        # Загрузка акций
        shares = self.parent.share_issue_model.get_all()
        self.shares_table.setRowCount(len(shares))
        for i, share in enumerate(shares):
            self.shares_table.setItem(i, 0, QTableWidgetItem(share['company_name']))
            self.shares_table.setItem(i, 1, QTableWidgetItem(share['registration_number']))
            self.shares_table.setItem(i, 2, QTableWidgetItem(str(share['registration_date'])))
            self.shares_table.setItem(i, 3, QTableWidgetItem(share['share_type']))
            self.shares_table.setItem(i, 4, QTableWidgetItem(share.get('category_series', '-')))
            self.shares_table.setItem(i, 5, QTableWidgetItem(str(share['quantity'])))
            self.shares_table.setItem(i, 6, QTableWidgetItem(f"{share['nominal_value']:,.2f}"))
            self.shares_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, share['issue_id'])
        
        # Загрузка счетов
        accounts = self.parent.account_model.get_all()
        self.accounts_table.setRowCount(len(accounts))
        for i, acc in enumerate(accounts):
            self.accounts_table.setItem(i, 0, QTableWidgetItem(acc['shareholder_name']))
            self.accounts_table.setItem(i, 1, QTableWidgetItem(acc['account_number']))
            self.accounts_table.setItem(i, 2, QTableWidgetItem(str(acc['open_date'])))
            self.accounts_table.setItem(i, 3, QTableWidgetItem(str(acc.get('close_date', '-'))))
            self.accounts_table.setItem(i, 4, QTableWidgetItem(str(acc['current_balance'])))
            self.accounts_table.setItem(i, 5, QTableWidgetItem(acc['status']))
            self.accounts_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, acc['account_id'])
        
        self.shares_table.resizeColumnsToContents()
        self.accounts_table.resizeColumnsToContents()
    
    def get_selected_issue_id(self):
        current_row = self.shares_table.currentRow()
        if current_row >= 0:
            return self.shares_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        return None
    
    def get_selected_account_id(self):
        current_row = self.accounts_table.currentRow()
        if current_row >= 0:
            return self.accounts_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        return None
    
    def add_company(self):
        dialog = CompanyDialog(self, self.parent.company_model)
        if dialog.exec():
            self.parent.show_message("Успех", "Акционерное общество добавлено")
            self.load_data()
    
    def add_shareholder(self):
        dialog = ShareholderDialog(self, self.parent.shareholder_model)
        if dialog.exec():
            self.parent.show_message("Успех", "Акционер добавлен")
            self.load_data()
    
    def add_operation(self):
        """Добавление операции через диалог с выбором выпуска акций"""
        dialog = OperationDialog(
            self, 
            self.parent.operation_model,
            self.parent.account_model,
            self.parent.share_issue_model
        )
        if dialog.exec():
            self.parent.show_message("Успех", "Операция добавлена")
            self.load_data()
    
    def edit_share(self):
        issue_id = self.get_selected_issue_id()
        if issue_id:
            issue = self.parent.share_issue_model.db.execute_query(
                "SELECT * FROM share_issues WHERE issue_id = %s", (issue_id,)
            )
            if issue:
                dialog = ShareIssueDialog(self, self.parent.share_issue_model, 
                                         self.parent.company_model, issue[0])
                if dialog.exec():
                    self.load_data()
        else:
            QMessageBox.warning(self, "Предупреждение", "Выберите запись для редактирования")
    
    def delete_share(self):
        issue_id = self.get_selected_issue_id()
        if issue_id:
            reply = QMessageBox.question(self, "Подтверждение", "Удалить выпуск акций?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.parent.share_issue_model.delete(issue_id)
                self.load_data()
        else:
            QMessageBox.warning(self, "Предупреждение", "Выберите запись для удаления")
    
    def edit_account(self):
        account_id = self.get_selected_account_id()
        if account_id:
            account = self.parent.account_model.get_by_id(account_id)
            if account:
                from gui.dialogs import AccountDialog
                dialog = AccountDialog(self, self.parent.account_model, 
                                      self.parent.shareholder_model, account)
                if dialog.exec():
                    self.load_data()
        else:
            QMessageBox.warning(self, "Предупреждение", "Выберите запись для редактирования")
    
    def delete_account(self):
        account_id = self.get_selected_account_id()
        if account_id:
            account = self.parent.account_model.get_by_id(account_id)
            if account and account['current_balance'] > 0:
                QMessageBox.warning(self, "Ошибка", "Нельзя удалить счет с положительным остатком акций")
            else:
                reply = QMessageBox.question(self, "Подтверждение", "Удалить лицевой счет?",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    self.parent.account_model.db.execute_delete(
                        "DELETE FROM accounts WHERE account_id = %s", (account_id,)
                    )
                    self.load_data()
        else:
            QMessageBox.warning(self, "Предупреждение", "Выберите запись для удаления")
    
    def refresh(self):
        self.load_data()