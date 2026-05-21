# gui/shareholder_tab.py - ПОЛНОСТЬЮ ИСПРАВЛЕННАЯ ВЕРСИЯ
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QGroupBox, 
                             QLineEdit, QLabel, QFormLayout, QComboBox,
                             QMessageBox, QTabWidget)
from PyQt6.QtCore import Qt
from gui.dialogs import ShareholderDialog
from utils.pdf_exporter import PDFExporter
from datetime import datetime

class ShareholderTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.shareholder_id = parent.user_data.get('shareholder_id', 1)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # Информация об акционере
        self.info_group = QGroupBox("Мои данные")
        info_layout = QFormLayout()
        
        self.name_label = QLabel()
        self.type_label = QLabel()
        self.inn_label = QLabel()
        self.address_label = QLabel()
        self.status_label = QLabel()
        
        info_layout.addRow("ФИО/Наименование:", self.name_label)
        info_layout.addRow("Тип:", self.type_label)
        info_layout.addRow("ИНН:", self.inn_label)
        info_layout.addRow("Адрес:", self.address_label)
        info_layout.addRow("Статус:", self.status_label)
        
        self.edit_btn = QPushButton("Редактировать личные данные")
        self.edit_btn.setStyleSheet("background-color: #2196F3; color: white;")
        self.edit_btn.clicked.connect(self.edit_shareholder)
        info_layout.addRow("", self.edit_btn)
        
        self.info_group.setLayout(info_layout)
        main_layout.addWidget(self.info_group)
        
        # Вкладки
        self.tab_widget = QTabWidget()
        
        # Вкладка лицевых счетов
        self.accounts_tab = QWidget()
        accounts_layout = QVBoxLayout()
        
        # Поиск счетов
        search_group = QGroupBox("Поиск лицевых счетов")
        search_layout = QHBoxLayout()
        
        self.search_type = QComboBox()
        self.search_type.addItems(["По номеру счета", "По статусу"])
        self.search_type.currentTextChanged.connect(self.on_search_type_changed)
        search_layout.addWidget(QLabel("Поиск:"))
        search_layout.addWidget(self.search_type)
        
        self.account_number_input = QLineEdit()
        self.account_number_input.setPlaceholderText("Введите номер счета...")
        search_layout.addWidget(self.account_number_input)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["активный", "закрытый"])
        self.status_combo.setVisible(False)
        search_layout.addWidget(self.status_combo)
        
        self.search_btn = QPushButton("Поиск")
        self.search_btn.setStyleSheet("background-color: #2196F3; color: white;")
        self.search_btn.clicked.connect(self.search_accounts)
        search_layout.addWidget(self.search_btn)
        
        self.clear_btn = QPushButton("Очистить")
        self.clear_btn.clicked.connect(self.clear_accounts_search)
        search_layout.addWidget(self.clear_btn)
        search_layout.addStretch()
        
        search_group.setLayout(search_layout)
        accounts_layout.addWidget(search_group)
        
        # Таблица счетов
        self.accounts_table = QTableWidget()
        self.accounts_table.setColumnCount(5)
        self.accounts_table.setHorizontalHeaderLabels(
            ["Номер счета", "Дата открытия", "Дата закрытия", "Остаток", "Статус"]
        )
        self.accounts_table.itemSelectionChanged.connect(self.on_account_selected)
        accounts_layout.addWidget(self.accounts_table)
        
        # Кнопка экспорта счетов
        accounts_export_layout = QHBoxLayout()
        self.export_accounts_pdf_btn = QPushButton("Экспортировать все счета в PDF")
        self.export_accounts_pdf_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.export_accounts_pdf_btn.clicked.connect(self.export_accounts_pdf)
        accounts_export_layout.addStretch()
        accounts_export_layout.addWidget(self.export_accounts_pdf_btn)
        accounts_layout.addLayout(accounts_export_layout)
        
        # Таблица акций на счете
        shares_group = QGroupBox("Акции на выбранном счете")
        shares_layout = QVBoxLayout()
        self.shares_table = QTableWidget()
        self.shares_table.setColumnCount(4)
        self.shares_table.setHorizontalHeaderLabels(
            ["Компания", "Рег. номер", "Тип", "Кол-во"]
        )
        shares_layout.addWidget(self.shares_table)
        
        # Кнопка экспорта акций на счете
        shares_export_layout = QHBoxLayout()
        self.export_shares_pdf_btn = QPushButton("Экспортировать акции счета в PDF")
        self.export_shares_pdf_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.export_shares_pdf_btn.clicked.connect(self.export_shares_on_account_pdf)
        shares_export_layout.addStretch()
        shares_export_layout.addWidget(self.export_shares_pdf_btn)
        shares_layout.addLayout(shares_export_layout)
        
        shares_group.setLayout(shares_layout)
        accounts_layout.addWidget(shares_group)
        
        self.accounts_tab.setLayout(accounts_layout)
        self.tab_widget.addTab(self.accounts_tab, "Мои счета")
        
        # Вкладка операций
        self.operations_tab = QWidget()
        operations_layout = QVBoxLayout()
        
        # Выбор счета для операций
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("Выберите счет:"))
        self.account_combo = QComboBox()
        self.account_combo.setMinimumWidth(300)
        self.account_combo.currentIndexChanged.connect(self.load_operations)
        select_layout.addWidget(self.account_combo)
        select_layout.addStretch()
        operations_layout.addLayout(select_layout)
        
        # Таблица операций
        self.operations_table = QTableWidget()
        self.operations_table.setColumnCount(5)
        self.operations_table.setHorizontalHeaderLabels(
            ["Дата", "Тип", "Компания", "Кол-во", "Основание"]
        )
        operations_layout.addWidget(self.operations_table)
        
        # Кнопка экспорта операций
        operations_export_layout = QHBoxLayout()
        self.export_operations_pdf_btn = QPushButton("Экспортировать операции в PDF")
        self.export_operations_pdf_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.export_operations_pdf_btn.clicked.connect(self.export_operations_pdf)
        operations_export_layout.addStretch()
        operations_export_layout.addWidget(self.export_operations_pdf_btn)
        operations_layout.addLayout(operations_export_layout)
        
        self.operations_tab.setLayout(operations_layout)
        self.tab_widget.addTab(self.operations_tab, "Операции по счетам")
        
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)
    
    def on_search_type_changed(self, search_type):
        is_number = search_type == "По номеру счета"
        self.account_number_input.setVisible(is_number)
        self.status_combo.setVisible(not is_number)
    
    def load_data(self):
        shareholder = self.parent.shareholder_model.get_by_id(self.shareholder_id)
        if shareholder:
            self.name_label.setText(shareholder['name'])
            self.type_label.setText("Физическое лицо" if shareholder['type'] == 'individual' else "Юридическое лицо")
            self.inn_label.setText(shareholder.get('inn', '-'))
            self.address_label.setText(shareholder['address'])
            self.status_label.setText(shareholder['status'])
        
        self.load_accounts()
    
    def load_accounts(self):
        accounts = self.parent.account_model.get_by_shareholder(self.shareholder_id)
        self.accounts_table.setRowCount(len(accounts))
        for i, acc in enumerate(accounts):
            self.accounts_table.setItem(i, 0, QTableWidgetItem(acc['account_number']))
            self.accounts_table.setItem(i, 1, QTableWidgetItem(str(acc['open_date'])))
            self.accounts_table.setItem(i, 2, QTableWidgetItem(str(acc.get('close_date', '-'))))
            self.accounts_table.setItem(i, 3, QTableWidgetItem(str(acc['current_balance'])))
            self.accounts_table.setItem(i, 4, QTableWidgetItem(acc['status']))
            
            # Сохраняем ID для внутреннего использования
            self.accounts_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, acc['account_id'])
        
        # Обновляем комбобокс для операций
        self.account_combo.clear()
        for acc in accounts:
            self.account_combo.addItem(f"{acc['account_number']} (остаток: {acc['current_balance']})", acc['account_id'])
        
        self.accounts_table.resizeColumnsToContents()
    
    def get_selected_account_id(self):
        current_row = self.accounts_table.currentRow()
        if current_row >= 0:
            return self.accounts_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        return None
    
    def on_account_selected(self):
        account_id = self.get_selected_account_id()
        if account_id:
            shares = self.parent.account_model.get_shares_on_account(account_id)
            
            self.shares_table.setRowCount(len(shares))
            for i, share in enumerate(shares):
                self.shares_table.setItem(i, 0, QTableWidgetItem(share['company_name']))
                self.shares_table.setItem(i, 1, QTableWidgetItem(share['registration_number']))
                self.shares_table.setItem(i, 2, QTableWidgetItem(share['share_type']))
                self.shares_table.setItem(i, 3, QTableWidgetItem(str(share['quantity'])))
            
            self.shares_table.resizeColumnsToContents()
    
    def search_accounts(self):
        search_type = self.search_type.currentText()
        
        if search_type == "По номеру счета":
            account_number = self.account_number_input.text().strip()
            if account_number:
                account = self.parent.account_model.get_by_number(account_number)
                if account and account['shareholder_id'] == self.shareholder_id:
                    self.accounts_table.setRowCount(1)
                    self.accounts_table.setItem(0, 0, QTableWidgetItem(account['account_number']))
                    self.accounts_table.setItem(0, 1, QTableWidgetItem(str(account['open_date'])))
                    self.accounts_table.setItem(0, 2, QTableWidgetItem(str(account.get('close_date', '-'))))
                    self.accounts_table.setItem(0, 3, QTableWidgetItem(str(account['current_balance'])))
                    self.accounts_table.setItem(0, 4, QTableWidgetItem(account['status']))
                    self.accounts_table.item(0, 0).setData(Qt.ItemDataRole.UserRole, account['account_id'])
                else:
                    self.accounts_table.setRowCount(0)
                    QMessageBox.information(self, "Результат", "Счет не найден")
        
        elif search_type == "По статусу":
            status = self.status_combo.currentText()
            accounts = self.parent.account_model.get_by_status(status)
            accounts = [a for a in accounts if a['shareholder_id'] == self.shareholder_id]
            
            self.accounts_table.setRowCount(len(accounts))
            for i, acc in enumerate(accounts):
                self.accounts_table.setItem(i, 0, QTableWidgetItem(acc['account_number']))
                self.accounts_table.setItem(i, 1, QTableWidgetItem(str(acc['open_date'])))
                self.accounts_table.setItem(i, 2, QTableWidgetItem(str(acc.get('close_date', '-'))))
                self.accounts_table.setItem(i, 3, QTableWidgetItem(str(acc['current_balance'])))
                self.accounts_table.setItem(i, 4, QTableWidgetItem(acc['status']))
                self.accounts_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, acc['account_id'])
    
    def clear_accounts_search(self):
        self.account_number_input.clear()
        self.load_accounts()
    
    def load_operations(self):
        account_id = self.account_combo.currentData()
        if account_id:
            operations = self.parent.operation_model.get_by_account(account_id)
            
            self.operations_table.setRowCount(len(operations))
            for i, op in enumerate(operations):
                self.operations_table.setItem(i, 0, QTableWidgetItem(str(op['operation_date'])))
                self.operations_table.setItem(i, 1, QTableWidgetItem(op['operation_type']))
                self.operations_table.setItem(i, 2, QTableWidgetItem(op['company_name']))
                self.operations_table.setItem(i, 3, QTableWidgetItem(str(op['quantity'])))
                self.operations_table.setItem(i, 4, QTableWidgetItem(op.get('basis_document', '-')))
            
            self.operations_table.resizeColumnsToContents()
    
    def edit_shareholder(self):
        shareholder = self.parent.shareholder_model.get_by_id(self.shareholder_id)
        if shareholder:
            dialog = ShareholderDialog(self, self.parent.shareholder_model, shareholder)
            if dialog.exec():
                self.load_data()
    
    def export_accounts_pdf(self):
        """Экспорт всех счетов акционера в PDF"""
        accounts = self.parent.account_model.get_by_shareholder(self.shareholder_id)
        if accounts:
            shareholder = self.parent.shareholder_model.get_by_id(self.shareholder_id)
            pdf_exporter = PDFExporter(self)
            pdf_exporter.export_accounts_report(accounts, shareholder.get('name') if shareholder else None)
        else:
            QMessageBox.information(self, "Результат", "Нет лицевых счетов для экспорта")
    
    def export_shares_on_account_pdf(self):
        """Экспорт акций на выбранном счете в PDF"""
        account_id = self.get_selected_account_id()
        if account_id:
            shares = self.parent.account_model.get_shares_on_account(account_id)
            if shares:
                account = self.parent.account_model.get_by_id(account_id)
                pdf_exporter = PDFExporter(self)
                pdf_exporter.export_account_shares_report(account, shares)
            else:
                QMessageBox.information(self, "Результат", "Нет акций на выбранном счете")
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите лицевой счет")
    
    def export_operations_pdf(self):
        """Экспорт операций по выбранному счету в PDF"""
        account_id = self.account_combo.currentData()
        if account_id:
            operations = self.parent.operation_model.get_by_account(account_id)
            if operations:
                account = self.parent.account_model.get_by_id(account_id)
                pdf_exporter = PDFExporter(self)
                pdf_exporter.export_operations_report(operations, account.get('account_number') if account else None)
            else:
                QMessageBox.information(self, "Результат", "Нет операций для экспорта")
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите лицевой счет")
    
    def refresh(self):
        self.load_data()