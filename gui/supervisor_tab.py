# gui/supervisor_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QGroupBox, 
                             QLineEdit, QLabel, QFormLayout, QComboBox,
                             QDateEdit, QMessageBox, QTabWidget, QTextEdit)
from PyQt6.QtCore import Qt, QDate
from gui.dialogs import ShareIssueDialog, CompanyDialog, ShareholderDialog

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
        
        # Вкладка управления (добавление информации)
        self.manage_tab = QWidget()
        manage_layout = QVBoxLayout()
        
        # Добавление АО
        add_company_group = QGroupBox("Добавление акционерного общества")
        add_company_layout = QHBoxLayout()
        self.add_company_btn = QPushButton("Добавить АО")
        self.add_company_btn.clicked.connect(self.add_company)
        add_company_layout.addWidget(self.add_company_btn)
        add_company_group.setLayout(add_company_layout)
        manage_layout.addWidget(add_company_group)
        
        # Добавление акционера
        add_shareholder_group = QGroupBox("Добавление акционера")
        add_shareholder_layout = QHBoxLayout()
        self.add_shareholder_btn = QPushButton("Добавить акционера")
        self.add_shareholder_btn.clicked.connect(self.add_shareholder)
        add_shareholder_layout.addWidget(self.add_shareholder_btn)
        add_shareholder_group.setLayout(add_shareholder_layout)
        manage_layout.addWidget(add_shareholder_group)
        
        # Добавление операции
        add_operation_group = QGroupBox("Добавление операции по лицевому счету")
        add_operation_layout = QFormLayout()
        
        self.op_account = QLineEdit()
        self.op_account.setPlaceholderText("Номер лицевого счета")
        self.op_type = QComboBox()
        self.op_type.addItems(["Зачисление", "Списание"])
        self.op_date = QDateEdit()
        self.op_date.setDate(QDate.currentDate())
        self.op_date.setCalendarPopup(True)
        self.op_quantity = QLineEdit()
        self.op_basis = QLineEdit()
        self.op_basis.setPlaceholderText("Основание операции")
        
        add_operation_layout.addRow("Лицевой счет:", self.op_account)
        add_operation_layout.addRow("Тип операции:", self.op_type)
        add_operation_layout.addRow("Дата:", self.op_date)
        add_operation_layout.addRow("Количество акций:", self.op_quantity)
        add_operation_layout.addRow("Основание:", self.op_basis)
        
        self.add_operation_btn = QPushButton("Добавить операцию")
        self.add_operation_btn.clicked.connect(self.add_operation)
        add_operation_layout.addRow("", self.add_operation_btn)
        
        add_operation_group.setLayout(add_operation_layout)
        manage_layout.addWidget(add_operation_group)
        
        self.manage_tab.setLayout(manage_layout)
        self.tab_widget.addTab(self.manage_tab, "Управление")
        
        # Вкладка акций
        self.shares_tab = QWidget()
        shares_layout = QVBoxLayout()
        
        # Таблица акций для редактирования
        shares_group = QGroupBox("Ранее зарегистрированные акции")
        shares_table_layout = QVBoxLayout()
        
        self.shares_table = QTableWidget()
        self.shares_table.setColumnCount(8)
        self.shares_table.setHorizontalHeaderLabels(
            ["ID", "Компания", "Рег. номер", "Дата", "Тип", "Категория", "Кол-во", "Номинал"]
        )
        shares_table_layout.addWidget(self.shares_table)
        
        shares_buttons = QHBoxLayout()
        self.edit_share_btn = QPushButton("Редактировать")
        self.edit_share_btn.clicked.connect(self.edit_share)
        self.delete_share_btn = QPushButton("Удалить")
        self.delete_share_btn.clicked.connect(self.delete_share)
        shares_buttons.addWidget(self.edit_share_btn)
        shares_buttons.addWidget(self.delete_share_btn)
        shares_table_layout.addLayout(shares_buttons)
        
        shares_group.setLayout(shares_table_layout)
        shares_layout.addWidget(shares_group)
        
        self.shares_tab.setLayout(shares_layout)
        self.tab_widget.addTab(self.shares_tab, "Акции")
        
        # Вкладка счетов
        self.accounts_tab = QWidget()
        accounts_layout = QVBoxLayout()
        
        # Таблица счетов для редактирования
        accounts_group = QGroupBox("Ранее зарегистрированные лицевые счета")
        accounts_table_layout = QVBoxLayout()
        
        self.accounts_table = QTableWidget()
        self.accounts_table.setColumnCount(7)
        self.accounts_table.setHorizontalHeaderLabels(
            ["ID", "Акционер", "Номер", "Дата открытия", "Дата закрытия", "Остаток", "Статус"]
        )
        accounts_table_layout.addWidget(self.accounts_table)
        
        accounts_buttons = QHBoxLayout()
        self.edit_account_btn = QPushButton("Редактировать")
        self.edit_account_btn.clicked.connect(self.edit_account)
        self.delete_account_btn = QPushButton("Удалить")
        self.delete_account_btn.clicked.connect(self.delete_account)
        accounts_buttons.addWidget(self.edit_account_btn)
        accounts_buttons.addWidget(self.delete_account_btn)
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
            self.shares_table.setItem(i, 0, QTableWidgetItem(str(share['issue_id'])))
            self.shares_table.setItem(i, 1, QTableWidgetItem(share['company_name']))
            self.shares_table.setItem(i, 2, QTableWidgetItem(share['registration_number']))
            self.shares_table.setItem(i, 3, QTableWidgetItem(str(share['registration_date'])))
            self.shares_table.setItem(i, 4, QTableWidgetItem(share['share_type']))
            self.shares_table.setItem(i, 5, QTableWidgetItem(share.get('category_series', '-')))
            self.shares_table.setItem(i, 6, QTableWidgetItem(str(share['quantity'])))
            self.shares_table.setItem(i, 7, QTableWidgetItem(f"{share['nominal_value']:,.2f}"))
        
        # Загрузка счетов
        accounts = self.parent.account_model.get_all()
        self.accounts_table.setRowCount(len(accounts))
        for i, acc in enumerate(accounts):
            self.accounts_table.setItem(i, 0, QTableWidgetItem(str(acc['account_id'])))
            self.accounts_table.setItem(i, 1, QTableWidgetItem(acc['shareholder_name']))
            self.accounts_table.setItem(i, 2, QTableWidgetItem(acc['account_number']))
            self.accounts_table.setItem(i, 3, QTableWidgetItem(str(acc['open_date'])))
            self.accounts_table.setItem(i, 4, QTableWidgetItem(str(acc.get('close_date', '-'))))
            self.accounts_table.setItem(i, 5, QTableWidgetItem(str(acc['current_balance'])))
            self.accounts_table.setItem(i, 6, QTableWidgetItem(acc['status']))
        
        self.shares_table.resizeColumnsToContents()
        self.accounts_table.resizeColumnsToContents()
    
    def add_company(self):
        dialog = CompanyDialog(self, self.parent.company_model)
        if dialog.exec():
            self.parent.show_message("Успех", "Акционерное общество добавлено")
    
    def add_shareholder(self):
        dialog = ShareholderDialog(self, self.parent.shareholder_model)
        if dialog.exec():
            self.parent.show_message("Успех", "Акционер добавлен")
    
    def add_operation(self):
        """Добавление операции по лицевому счету"""
        account_number = self.op_account.text()
        if not account_number:
            QMessageBox.warning(self, "Ошибка", "Введите номер лицевого счета")
            return
        
        # Поиск счета
        account = self.parent.account_model.get_by_number(account_number)
        if not account:
            QMessageBox.warning(self, "Ошибка", "Лицевой счет не найден")
            return
        
        try:
            quantity = int(self.op_quantity.text())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Количество акций должно быть положительным числом")
            return
        
        # Получение списка выпусков акций
        issues = self.parent.share_issue_model.get_all()
        if not issues:
            QMessageBox.warning(self, "Ошибка", "Нет доступных выпусков акций")
            return
        
        # Для простоты берем первый выпуск
        issue_id = issues[0]['issue_id']
        
        operation_data = {
            'account_id': account['account_id'],
            'type_id': 1 if self.op_type.currentText() == "Зачисление" else 2,
            'operation_date': self.op_date.date().toPyDate(),
            'share_issue_id': issue_id,
            'quantity': quantity,
            'basis_document': self.op_basis.text()
        }
        
        try:
            self.parent.operation_model.create(operation_data)
            
            # Обновление остатка на счете
            if operation_data['type_id'] == 1:  # Зачисление
                new_balance = account['current_balance'] + quantity
                self.parent.account_model.db.execute_update(
                    "UPDATE accounts SET current_balance = %s WHERE account_id = %s",
                    (new_balance, account['account_id'])
                )
                # Добавление связи счет-акции
                self.parent.account_model.add_shares(account['account_id'], issue_id, quantity)
            else:  # Списание
                if quantity > account['current_balance']:
                    QMessageBox.warning(self, "Ошибка", "Недостаточно акций на счете")
                    return
                new_balance = account['current_balance'] - quantity
                self.parent.account_model.db.execute_update(
                    "UPDATE accounts SET current_balance = %s WHERE account_id = %s",
                    (new_balance, account['account_id'])
                )
                # Уменьшение количества акций на счете
                self.parent.account_model.db.execute_update("""
                    UPDATE account_shares 
                    SET quantity = quantity - %s 
                    WHERE account_id = %s AND issue_id = %s AND quantity >= %s
                """, (quantity, account['account_id'], issue_id, quantity))
            
            self.parent.show_message("Успех", "Операция добавлена")
            self.op_account.clear()
            self.op_quantity.clear()
            self.op_basis.clear()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка добавления операции: {str(e)}")
    
    def edit_share(self):
        selected = self.shares_table.currentRow()
        if selected >= 0:
            issue_id = int(self.shares_table.item(selected, 0).text())
            issue = self.parent.share_issue_model.db.execute_query(
                "SELECT * FROM share_issues WHERE issue_id = %s", (issue_id,)
            )
            if issue:
                dialog = ShareIssueDialog(self, self.parent.share_issue_model, 
                                         self.parent.company_model, issue[0])
                if dialog.exec():
                    self.load_data()
    
    def delete_share(self):
        selected = self.shares_table.currentRow()
        if selected >= 0:
            issue_id = int(self.shares_table.item(selected, 0).text())
            reply = QMessageBox.question(self, "Подтверждение", "Удалить выпуск акций?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.parent.share_issue_model.delete(issue_id)
                self.load_data()
    
    def edit_account(self):
        selected = self.accounts_table.currentRow()
        if selected >= 0:
            account_id = int(self.accounts_table.item(selected, 0).text())
            account = self.parent.account_model.get_by_id(account_id)
            if account:
                from gui.dialogs import AccountDialog
                dialog = AccountDialog(self, self.parent.account_model, 
                                      self.parent.shareholder_model, account)
                if dialog.exec():
                    self.load_data()
    
    def delete_account(self):
        selected = self.accounts_table.currentRow()
        if selected >= 0:
            account_id = int(self.accounts_table.item(selected, 0).text())
            account = self.parent.account_model.get_by_id(account_id)
            if account and account['current_balance'] > 0:
                QMessageBox.warning(self, "Ошибка", "Нельзя удалить счет с положительным остатком")
            else:
                reply = QMessageBox.question(self, "Подтверждение", "Удалить лицевой счет?",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    self.parent.account_model.db.execute_delete(
                        "DELETE FROM accounts WHERE account_id = %s", (account_id,)
                    )
                    self.load_data()
    
    def refresh(self):
        self.load_data()