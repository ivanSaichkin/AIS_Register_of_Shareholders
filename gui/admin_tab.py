# gui/admin_tab.py - ПОЛНОСТЬЮ ИСПРАВЛЕННАЯ ВЕРСИЯ
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QGroupBox, 
                             QLineEdit, QLabel, QMessageBox, QTabWidget, QComboBox)
from PyQt6.QtCore import Qt
from gui.dialogs import CompanyDialog, ShareIssueDialog, ShareholderDialog, AccountDialog
from utils.pdf_exporter import PDFExporter
from datetime import datetime

class AdminTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Поиск
        search_group = QGroupBox("Поиск")
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по наименованию...")
        self.search_input.textChanged.connect(self.search_companies)
        search_layout.addWidget(self.search_input)
        
        self.search_btn = QPushButton("Поиск")
        self.search_btn.clicked.connect(self.search_companies)
        search_layout.addWidget(self.search_btn)
        
        self.clear_btn = QPushButton("Очистить")
        self.clear_btn.clicked.connect(self.clear_search)
        search_layout.addWidget(self.clear_btn)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # Таблица компаний
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["Полное наименование", "Сокращенное", "ИНН", "ОГРН", 
             "Адрес", "Уставной капитал", "Город"]
        )
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)
        
        # Кнопки управления
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.add_company)
        self.edit_btn = QPushButton("Редактировать")
        self.edit_btn.clicked.connect(self.edit_company)
        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.delete_company)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Вкладки для других сущностей
        self.setup_other_tabs()
    
    def setup_other_tabs(self):
        # ==================== ВЫПУСКИ АКЦИЙ ====================
        self.share_issues_tab = QWidget()
        issues_layout = QVBoxLayout()
        
        search_issues = QHBoxLayout()
        self.issue_search_input = QLineEdit()
        self.issue_search_input.setPlaceholderText("Поиск по регистрационному номеру...")
        search_issues.addWidget(self.issue_search_input)
        
        self.issue_search_btn = QPushButton("Поиск")
        self.issue_search_btn.clicked.connect(self.search_issues)
        search_issues.addWidget(self.issue_search_btn)
        
        self.clear_issue_search_btn = QPushButton("Очистить")
        self.clear_issue_search_btn.clicked.connect(self.clear_issue_search)
        search_issues.addWidget(self.clear_issue_search_btn)
        search_issues.addStretch()
        
        issues_layout.addLayout(search_issues)
        
        self.issues_table = QTableWidget()
        self.issues_table.setColumnCount(7)
        self.issues_table.setHorizontalHeaderLabels(
            ["Компания", "Рег. номер", "Дата регистрации", "Тип", 
             "Категория", "Количество", "Номинальная стоимость"]
        )
        issues_layout.addWidget(self.issues_table)
        
        issues_buttons = QHBoxLayout()
        self.add_issue_btn = QPushButton("Добавить выпуск")
        self.add_issue_btn.setStyleSheet("background-color: #2196F3; color: white;")
        self.add_issue_btn.clicked.connect(self.add_issue)
        self.edit_issue_btn = QPushButton("Редактировать")
        self.edit_issue_btn.clicked.connect(self.edit_issue)
        self.delete_issue_btn = QPushButton("Удалить")
        self.delete_issue_btn.clicked.connect(self.delete_issue)
        
        issues_buttons.addWidget(self.add_issue_btn)
        issues_buttons.addWidget(self.edit_issue_btn)
        issues_buttons.addWidget(self.delete_issue_btn)
        issues_buttons.addStretch()
        issues_layout.addLayout(issues_buttons)
        
        self.share_issues_tab.setLayout(issues_layout)
        
        # ==================== АКЦИОНЕРЫ ====================
        self.shareholders_tab = QWidget()
        shareholders_layout = QVBoxLayout()
        
        search_shareholders = QHBoxLayout()
        self.shareholder_search_input = QLineEdit()
        self.shareholder_search_input.setPlaceholderText("Поиск по ФИО/наименованию...")
        search_shareholders.addWidget(self.shareholder_search_input)
        
        self.shareholder_search_btn = QPushButton("Поиск")
        self.shareholder_search_btn.clicked.connect(self.search_shareholders)
        search_shareholders.addWidget(self.shareholder_search_btn)
        
        self.clear_shareholder_search_btn = QPushButton("Очистить")
        self.clear_shareholder_search_btn.clicked.connect(self.clear_shareholder_search)
        search_shareholders.addWidget(self.clear_shareholder_search_btn)
        search_shareholders.addStretch()
        
        shareholders_layout.addLayout(search_shareholders)
        
        self.shareholders_table = QTableWidget()
        self.shareholders_table.setColumnCount(6)
        self.shareholders_table.setHorizontalHeaderLabels(
            ["Тип", "Наименование", "ИНН", "Паспорт/ОГРН", "Адрес", "Статус"]
        )
        shareholders_layout.addWidget(self.shareholders_table)
        
        shareholders_buttons = QHBoxLayout()
        self.add_shareholder_btn = QPushButton("Добавить акционера")
        self.add_shareholder_btn.setStyleSheet("background-color: #2196F3; color: white;")
        self.add_shareholder_btn.clicked.connect(self.add_shareholder)
        self.edit_shareholder_btn = QPushButton("Редактировать")
        self.edit_shareholder_btn.clicked.connect(self.edit_shareholder)
        self.delete_shareholder_btn = QPushButton("Удалить")
        self.delete_shareholder_btn.clicked.connect(self.delete_shareholder)
        
        shareholders_buttons.addWidget(self.add_shareholder_btn)
        shareholders_buttons.addWidget(self.edit_shareholder_btn)
        shareholders_buttons.addWidget(self.delete_shareholder_btn)
        shareholders_buttons.addStretch()
        shareholders_layout.addLayout(shareholders_buttons)
        
        self.shareholders_tab.setLayout(shareholders_layout)
        
        # ==================== ЛИЦЕВЫЕ СЧЕТА ====================
        self.accounts_tab = QWidget()
        accounts_layout = QVBoxLayout()
        
        search_accounts = QHBoxLayout()
        self.account_search_input = QLineEdit()
        self.account_search_input.setPlaceholderText("Поиск по номеру счета...")
        search_accounts.addWidget(self.account_search_input)
        
        self.account_search_btn = QPushButton("Поиск")
        self.account_search_btn.clicked.connect(self.search_accounts)
        search_accounts.addWidget(self.account_search_btn)
        
        self.clear_account_search_btn = QPushButton("Очистить")
        self.clear_account_search_btn.clicked.connect(self.clear_account_search)
        search_accounts.addWidget(self.clear_account_search_btn)
        search_accounts.addStretch()
        
        accounts_layout.addLayout(search_accounts)
        
        self.accounts_table = QTableWidget()
        self.accounts_table.setColumnCount(6)
        self.accounts_table.setHorizontalHeaderLabels(
            ["Акционер", "Номер счета", "Дата открытия", 
             "Дата закрытия", "Остаток", "Статус"]
        )
        accounts_layout.addWidget(self.accounts_table)
        
        accounts_buttons = QHBoxLayout()
        self.add_account_btn = QPushButton("Добавить счет")
        self.add_account_btn.setStyleSheet("background-color: #2196F3; color: white;")
        self.add_account_btn.clicked.connect(self.add_account)
        self.edit_account_btn = QPushButton("Редактировать")
        self.edit_account_btn.clicked.connect(self.edit_account)
        self.delete_account_btn = QPushButton("Удалить")
        self.delete_account_btn.clicked.connect(self.delete_account)
        
        accounts_buttons.addWidget(self.add_account_btn)
        accounts_buttons.addWidget(self.edit_account_btn)
        accounts_buttons.addWidget(self.delete_account_btn)
        accounts_buttons.addStretch()
        accounts_layout.addLayout(accounts_buttons)
        
        self.accounts_tab.setLayout(accounts_layout)
        
        # ==================== ОТЧЕТЫ ====================
        self.reports_tab = QWidget()
        reports_layout = QVBoxLayout()
        
        # Отчет 1: По городам
        city_report_group = QGroupBox("Отчет по городам")
        city_layout = QHBoxLayout()
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Введите город...")
        self.city_input.setMinimumWidth(200)
        city_layout.addWidget(self.city_input)
        
        self.city_report_btn = QPushButton("Сформировать отчет")
        self.city_report_btn.setStyleSheet("background-color: #2196F3; color: white;")
        self.city_report_btn.clicked.connect(self.city_report)
        city_layout.addWidget(self.city_report_btn)
        
        self.city_pdf_btn = QPushButton("Сохранить в PDF")
        self.city_pdf_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.city_pdf_btn.clicked.connect(self.export_city_report_pdf)
        city_layout.addWidget(self.city_pdf_btn)
        city_layout.addStretch()
        
        city_report_group.setLayout(city_layout)
        reports_layout.addWidget(city_report_group)
        
        # Отчет 2: По статусу акционеров
        status_report_group = QGroupBox("Отчет по статусу акционеров")
        status_layout = QHBoxLayout()
        self.status_combo = QLineEdit()
        self.status_combo.setPlaceholderText("Статус (активный/заблокированный)")
        self.status_combo.setMinimumWidth(200)
        status_layout.addWidget(self.status_combo)
        
        self.status_report_btn = QPushButton("Сформировать отчет")
        self.status_report_btn.setStyleSheet("background-color: #2196F3; color: white;")
        self.status_report_btn.clicked.connect(self.status_report)
        status_layout.addWidget(self.status_report_btn)
        
        self.status_pdf_btn = QPushButton("Сохранить в PDF")
        self.status_pdf_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.status_pdf_btn.clicked.connect(self.export_status_report_pdf)
        status_layout.addWidget(self.status_pdf_btn)
        status_layout.addStretch()
        
        status_report_group.setLayout(status_layout)
        reports_layout.addWidget(status_report_group)
        
        # Отчет 3: Об отдельном АО с выпусками акций
        company_details_group = QGroupBox("Отчет об отдельном акционерном обществе")
        company_details_layout = QHBoxLayout()
        
        self.report_company_combo = QComboBox()
        self.report_company_combo.setMinimumWidth(300)
        company_details_layout.addWidget(self.report_company_combo)
        
        self.company_details_btn = QPushButton("Сформировать и сохранить PDF")
        self.company_details_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.company_details_btn.clicked.connect(self.export_company_details_report)
        company_details_layout.addWidget(self.company_details_btn)
        company_details_layout.addStretch()
        
        company_details_group.setLayout(company_details_layout)
        reports_layout.addWidget(company_details_group)
        
        # Отчет 4: Об акционере и его лицевых счетах
        shareholder_accounts_group = QGroupBox("Отчет об акционере и его лицевых счетах")
        shareholder_accounts_layout = QHBoxLayout()
        
        self.report_shareholder_combo = QComboBox()
        self.report_shareholder_combo.setMinimumWidth(300)
        shareholder_accounts_layout.addWidget(self.report_shareholder_combo)
        
        self.shareholder_accounts_btn = QPushButton("Сформировать и сохранить PDF")
        self.shareholder_accounts_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.shareholder_accounts_btn.clicked.connect(self.export_shareholder_accounts_report)
        shareholder_accounts_layout.addWidget(self.shareholder_accounts_btn)
        shareholder_accounts_layout.addStretch()
        
        shareholder_accounts_group.setLayout(shareholder_accounts_layout)
        reports_layout.addWidget(shareholder_accounts_group)
        
        # Отчет 5: О лицевом счете и акциях на нем
        account_shares_group = QGroupBox("Отчет о лицевом счете и акциях на нем")
        account_shares_layout = QHBoxLayout()
        
        self.report_account_combo = QComboBox()
        self.report_account_combo.setMinimumWidth(300)
        account_shares_layout.addWidget(self.report_account_combo)
        
        self.account_shares_btn = QPushButton("Сформировать и сохранить PDF")
        self.account_shares_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.account_shares_btn.clicked.connect(self.export_account_shares_report)
        account_shares_layout.addWidget(self.account_shares_btn)
        account_shares_layout.addStretch()
        
        account_shares_group.setLayout(account_shares_layout)
        reports_layout.addWidget(account_shares_group)
        
        # Таблица для отображения отчетов
        self.report_text = QTableWidget()
        self.report_text.setColumnCount(4)
        self.report_text.setHorizontalHeaderLabels(["Наименование", "ИНН", "Адрес", "Доп. информация"])
        reports_layout.addWidget(self.report_text)
        
        self.reports_tab.setLayout(reports_layout)
    
    def load_data(self):
        # Загрузка компаний
        companies = self.parent.company_model.get_all()
        self.table.setRowCount(len(companies))
        for i, company in enumerate(companies):
            self.table.setItem(i, 0, QTableWidgetItem(company['full_name']))
            self.table.setItem(i, 1, QTableWidgetItem(company['short_name']))
            self.table.setItem(i, 2, QTableWidgetItem(company['inn']))
            self.table.setItem(i, 3, QTableWidgetItem(company['ogrn']))
            self.table.setItem(i, 4, QTableWidgetItem(company['address']))
            self.table.setItem(i, 5, QTableWidgetItem(f"{company['authorized_capital']:,.2f}"))
            self.table.setItem(i, 6, QTableWidgetItem(company.get('city', '')))
            self.table.item(i, 0).setData(Qt.ItemDataRole.UserRole, company['company_id'])
        self.table.resizeColumnsToContents()
        
        # Загрузка выпусков
        issues = self.parent.share_issue_model.get_all()
        self.issues_table.setRowCount(len(issues))
        for i, issue in enumerate(issues):
            self.issues_table.setItem(i, 0, QTableWidgetItem(issue.get('company_name', 'Неизвестно')))
            self.issues_table.setItem(i, 1, QTableWidgetItem(issue.get('registration_number', '')))
            self.issues_table.setItem(i, 2, QTableWidgetItem(str(issue.get('registration_date', ''))))
            self.issues_table.setItem(i, 3, QTableWidgetItem(issue.get('share_type', '')))
            self.issues_table.setItem(i, 4, QTableWidgetItem(issue.get('category_series', '')))
            self.issues_table.setItem(i, 5, QTableWidgetItem(str(issue.get('quantity', '0'))))
            self.issues_table.setItem(i, 6, QTableWidgetItem(f"{issue.get('nominal_value', 0):,.2f}"))
            self.issues_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, issue.get('issue_id'))
        self.issues_table.resizeColumnsToContents()
        
        # Загрузка акционеров
        shareholders = self.parent.shareholder_model.get_all()
        self.shareholders_table.setRowCount(len(shareholders))
        for i, sh in enumerate(shareholders):
            self.shareholders_table.setItem(i, 0, QTableWidgetItem('Физическое' if sh['type'] == 'individual' else 'Юридическое'))
            self.shareholders_table.setItem(i, 1, QTableWidgetItem(sh['name']))
            self.shareholders_table.setItem(i, 2, QTableWidgetItem(sh.get('inn', '')))
            passport = sh.get('passport_data', '') or sh.get('ogrn', '')
            self.shareholders_table.setItem(i, 3, QTableWidgetItem(passport))
            self.shareholders_table.setItem(i, 4, QTableWidgetItem(sh['address']))
            self.shareholders_table.setItem(i, 5, QTableWidgetItem(sh['status']))
            self.shareholders_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, sh['shareholder_id'])
        self.shareholders_table.resizeColumnsToContents()
        
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
        self.accounts_table.resizeColumnsToContents()
        
        # Заполнение комбобоксов для отчетов
        self.load_report_combos()
    
    def load_report_combos(self):
        """Заполнение комбобоксов для отчетов"""
        # Компании
        companies = self.parent.company_model.get_all()
        self.report_company_combo.clear()
        for company in companies:
            self.report_company_combo.addItem(company['full_name'], company['company_id'])
        
        # Акционеры
        shareholders = self.parent.shareholder_model.get_all()
        self.report_shareholder_combo.clear()
        for sh in shareholders:
            self.report_shareholder_combo.addItem(sh['name'], sh['shareholder_id'])
        
        # Счета
        accounts = self.parent.account_model.get_all()
        self.report_account_combo.clear()
        for acc in accounts:
            self.report_account_combo.addItem(
                f"{acc['account_number']} - {acc['shareholder_name']}", 
                acc['account_id']
            )
    
    def get_selected_company_id(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            return self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        return None
    
    def get_selected_issue_id(self):
        current_row = self.issues_table.currentRow()
        if current_row >= 0:
            return self.issues_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        return None
    
    def get_selected_shareholder_id(self):
        current_row = self.shareholders_table.currentRow()
        if current_row >= 0:
            return self.shareholders_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        return None
    
    def get_selected_account_id(self):
        current_row = self.accounts_table.currentRow()
        if current_row >= 0:
            return self.accounts_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        return None
    
    # ==================== МЕТОДЫ ПОИСКА ====================
    
    def search_companies(self):
        search_text = self.search_input.text()
        if search_text:
            companies = self.parent.company_model.get_by_name(search_text)
        else:
            companies = self.parent.company_model.get_all()
        
        self.table.setRowCount(len(companies))
        for i, company in enumerate(companies):
            self.table.setItem(i, 0, QTableWidgetItem(company['full_name']))
            self.table.setItem(i, 1, QTableWidgetItem(company['short_name']))
            self.table.setItem(i, 2, QTableWidgetItem(company['inn']))
            self.table.setItem(i, 3, QTableWidgetItem(company['ogrn']))
            self.table.setItem(i, 4, QTableWidgetItem(company['address']))
            self.table.setItem(i, 5, QTableWidgetItem(f"{company['authorized_capital']:,.2f}"))
            self.table.setItem(i, 6, QTableWidgetItem(company.get('city', '')))
            self.table.item(i, 0).setData(Qt.ItemDataRole.UserRole, company['company_id'])
    
    def clear_search(self):
        self.search_input.clear()
        self.load_data()
    
    def search_issues(self):
        search_text = self.issue_search_input.text().strip()
        if search_text:
            issue = self.parent.share_issue_model.get_by_registration_number(search_text)
            if issue:
                self.issues_table.setRowCount(1)
                self.issues_table.setItem(0, 0, QTableWidgetItem(issue.get('company_name', 'Неизвестно')))
                self.issues_table.setItem(0, 1, QTableWidgetItem(issue.get('registration_number', '')))
                self.issues_table.setItem(0, 2, QTableWidgetItem(str(issue.get('registration_date', ''))))
                self.issues_table.setItem(0, 3, QTableWidgetItem(issue.get('share_type', '')))
                self.issues_table.setItem(0, 4, QTableWidgetItem(issue.get('category_series', '')))
                self.issues_table.setItem(0, 5, QTableWidgetItem(str(issue.get('quantity', '0'))))
                self.issues_table.setItem(0, 6, QTableWidgetItem(f"{issue.get('nominal_value', 0):,.2f}"))
                self.issues_table.item(0, 0).setData(Qt.ItemDataRole.UserRole, issue.get('issue_id'))
                self.issues_table.resizeColumnsToContents()
            else:
                self.issues_table.setRowCount(0)
                QMessageBox.information(self, "Результат", "Выпуск акций с таким регистрационным номером не найден")
        else:
            self.load_data()
    
    def clear_issue_search(self):
        self.issue_search_input.clear()
        self.load_data()
    
    def search_shareholders(self):
        search_text = self.shareholder_search_input.text()
        if search_text:
            shareholders = self.parent.shareholder_model.get_by_name(search_text)
        else:
            shareholders = self.parent.shareholder_model.get_all()
        
        self.shareholders_table.setRowCount(len(shareholders))
        for i, sh in enumerate(shareholders):
            self.shareholders_table.setItem(i, 0, QTableWidgetItem('Физическое' if sh['type'] == 'individual' else 'Юридическое'))
            self.shareholders_table.setItem(i, 1, QTableWidgetItem(sh['name']))
            self.shareholders_table.setItem(i, 2, QTableWidgetItem(sh.get('inn', '')))
            passport = sh.get('passport_data', '') or sh.get('ogrn', '')
            self.shareholders_table.setItem(i, 3, QTableWidgetItem(passport))
            self.shareholders_table.setItem(i, 4, QTableWidgetItem(sh['address']))
            self.shareholders_table.setItem(i, 5, QTableWidgetItem(sh['status']))
            self.shareholders_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, sh['shareholder_id'])
    
    def clear_shareholder_search(self):
        self.shareholder_search_input.clear()
        self.load_data()
    
    def search_accounts(self):
        search_text = self.account_search_input.text()
        if search_text:
            account = self.parent.account_model.get_by_number(search_text)
            if account:
                self.accounts_table.setRowCount(1)
                self.accounts_table.setItem(0, 0, QTableWidgetItem(account['shareholder_name']))
                self.accounts_table.setItem(0, 1, QTableWidgetItem(account['account_number']))
                self.accounts_table.setItem(0, 2, QTableWidgetItem(str(account['open_date'])))
                self.accounts_table.setItem(0, 3, QTableWidgetItem(str(account.get('close_date', '-'))))
                self.accounts_table.setItem(0, 4, QTableWidgetItem(str(account['current_balance'])))
                self.accounts_table.setItem(0, 5, QTableWidgetItem(account['status']))
                self.accounts_table.item(0, 0).setData(Qt.ItemDataRole.UserRole, account['account_id'])
            else:
                self.accounts_table.setRowCount(0)
                QMessageBox.information(self, "Результат", "Лицевой счет не найден")
        else:
            self.load_data()
    
    def clear_account_search(self):
        self.account_search_input.clear()
        self.load_data()
    
    # ==================== КОМПАНИИ (CRUD) ====================
    
    def add_company(self):
        dialog = CompanyDialog(self, self.parent.company_model)
        if dialog.exec():
            self.load_data()
            self.load_report_combos()
    
    def edit_company(self):
        company_id = self.get_selected_company_id()
        if company_id:
            company = self.parent.company_model.get_by_id(company_id)
            if company:
                dialog = CompanyDialog(self, self.parent.company_model, company)
                if dialog.exec():
                    self.load_data()
                    self.load_report_combos()
        else:
            QMessageBox.warning(self, "Предупреждение", "Выберите запись для редактирования")
    
    def delete_company(self):
        company_id = self.get_selected_company_id()
        if company_id:
            reply = QMessageBox.question(self, "Подтверждение", 
                                        "Удалить акционерное общество?\nЭто также удалит все связанные выпуски акций.",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.parent.company_model.delete(company_id)
                self.load_data()
                self.load_report_combos()
        else:
            QMessageBox.warning(self, "Предупреждение", "Выберите запись для удаления")
    
    # ==================== ВЫПУСКИ АКЦИЙ (CRUD) ====================
    
    def add_issue(self):
        dialog = ShareIssueDialog(self, self.parent.share_issue_model, self.parent.company_model)
        if dialog.exec():
            self.load_data()
    
    def edit_issue(self):
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
    
    def delete_issue(self):
        issue_id = self.get_selected_issue_id()
        if issue_id:
            reply = QMessageBox.question(self, "Подтверждение", "Удалить выпуск акций?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.parent.share_issue_model.delete(issue_id)
                self.load_data()
        else:
            QMessageBox.warning(self, "Предупреждение", "Выберите запись для удаления")
    
    # ==================== АКЦИОНЕРЫ (CRUD) ====================
    
    def add_shareholder(self):
        dialog = ShareholderDialog(self, self.parent.shareholder_model)
        if dialog.exec():
            self.load_data()
            self.load_report_combos()
    
    def edit_shareholder(self):
        shareholder_id = self.get_selected_shareholder_id()
        if shareholder_id:
            shareholder = self.parent.shareholder_model.get_by_id(shareholder_id)
            if shareholder:
                dialog = ShareholderDialog(self, self.parent.shareholder_model, shareholder)
                if dialog.exec():
                    self.load_data()
                    self.load_report_combos()
        else:
            QMessageBox.warning(self, "Предупреждение", "Выберите запись для редактирования")
    
    def delete_shareholder(self):
        shareholder_id = self.get_selected_shareholder_id()
        if shareholder_id:
            reply = QMessageBox.question(self, "Подтверждение", "Удалить акционера?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    self.parent.shareholder_model.delete(shareholder_id)
                    self.load_data()
                    self.load_report_combos()
                except ValueError as e:
                    QMessageBox.warning(self, "Ошибка", str(e))
        else:
            QMessageBox.warning(self, "Предупреждение", "Выберите запись для удаления")
    
    # ==================== ЛИЦЕВЫЕ СЧЕТА (CRUD) ====================
    
    def add_account(self):
        dialog = AccountDialog(self, self.parent.account_model, self.parent.shareholder_model)
        if dialog.exec():
            self.load_data()
            self.load_report_combos()
    
    def edit_account(self):
        account_id = self.get_selected_account_id()
        if account_id:
            account = self.parent.account_model.get_by_id(account_id)
            if account:
                dialog = AccountDialog(self, self.parent.account_model, 
                                      self.parent.shareholder_model, account)
                if dialog.exec():
                    self.load_data()
                    self.load_report_combos()
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
                    self.load_report_combos()
        else:
            QMessageBox.warning(self, "Предупреждение", "Выберите запись для удаления")
    
    # ==================== ОТЧЕТЫ ====================
    
    def city_report(self):
        """Формирование отчета по городам"""
        city = self.city_input.text().strip()
        if city:
            companies = self.parent.company_model.get_by_city(city)
            if companies:
                self.report_text.setRowCount(len(companies))
                self.report_text.setColumnCount(4)
                self.report_text.setHorizontalHeaderLabels(["Наименование", "ИНН", "Адрес", "Уставной капитал"])
                for i, company in enumerate(companies):
                    self.report_text.setItem(i, 0, QTableWidgetItem(company['full_name']))
                    self.report_text.setItem(i, 1, QTableWidgetItem(company['inn']))
                    self.report_text.setItem(i, 2, QTableWidgetItem(company['address']))
                    self.report_text.setItem(i, 3, QTableWidgetItem(f"{company['authorized_capital']:,.2f} руб."))
                self.report_text.resizeColumnsToContents()
                QMessageBox.information(self, "Результат", f"Найдено компаний: {len(companies)}")
            else:
                self.report_text.setRowCount(0)
                QMessageBox.information(self, "Результат", f"Компании в городе '{city}' не найдены")
        else:
            QMessageBox.warning(self, "Ошибка", "Введите город для поиска")
    
    def status_report(self):
        """Формирование отчета по статусу акционеров"""
        status = self.status_combo.text().strip()
        if status:
            shareholders = self.parent.shareholder_model.get_by_status(status)
            if shareholders:
                self.report_text.setRowCount(len(shareholders))
                self.report_text.setColumnCount(4)
                self.report_text.setHorizontalHeaderLabels(["Наименование", "Тип", "ИНН", "Статус"])
                for i, sh in enumerate(shareholders):
                    self.report_text.setItem(i, 0, QTableWidgetItem(sh['name']))
                    self.report_text.setItem(i, 1, QTableWidgetItem('Физическое' if sh['type'] == 'individual' else 'Юридическое'))
                    self.report_text.setItem(i, 2, QTableWidgetItem(sh.get('inn', '-')))
                    self.report_text.setItem(i, 3, QTableWidgetItem(sh['status']))
                self.report_text.resizeColumnsToContents()
                QMessageBox.information(self, "Результат", f"Найдено акционеров: {len(shareholders)}")
            else:
                self.report_text.setRowCount(0)
                QMessageBox.information(self, "Результат", f"Акционеры со статусом '{status}' не найдены")
        else:
            QMessageBox.warning(self, "Ошибка", "Введите статус для поиска")
    
    def export_city_report_pdf(self):
        """Экспорт отчета по городам в PDF"""
        city = self.city_input.text().strip()
        if city:
            companies = self.parent.company_model.get_by_city(city)
            if companies:
                pdf_exporter = PDFExporter(self)
                pdf_exporter.export_companies_report(companies, city)
            else:
                QMessageBox.information(self, "Результат", f"Компании в городе '{city}' не найдены")
        else:
            QMessageBox.warning(self, "Ошибка", "Введите город для поиска")
    
    def export_status_report_pdf(self):
        """Экспорт отчета по статусу акционеров в PDF"""
        status = self.status_combo.text().strip()
        if status:
            shareholders = self.parent.shareholder_model.get_by_status(status)
            if shareholders:
                pdf_exporter = PDFExporter(self)
                pdf_exporter.export_shareholders_report(shareholders, status)
            else:
                QMessageBox.information(self, "Результат", f"Акционеры со статусом '{status}' не найдены")
        else:
            QMessageBox.warning(self, "Ошибка", "Введите статус для поиска")
    
    def export_company_details_report(self):
        """Отчет об отдельном АО с выпусками акций"""
        company_id = self.report_company_combo.currentData()
        if not company_id:
            QMessageBox.warning(self, "Ошибка", "Выберите акционерное общество")
            return
        
        company = self.parent.company_model.get_by_id(company_id)
        if not company:
            QMessageBox.warning(self, "Ошибка", "Компания не найдена")
            return
        
        shares = self.parent.share_issue_model.get_by_company(company_id)
        
        pdf_exporter = PDFExporter(self)
        pdf_exporter.export_company_details_report(company, shares)
    
    def export_shareholder_accounts_report(self):
        """Отчет об акционере и его лицевых счетах"""
        shareholder_id = self.report_shareholder_combo.currentData()
        if not shareholder_id:
            QMessageBox.warning(self, "Ошибка", "Выберите акционера")
            return
        
        shareholder = self.parent.shareholder_model.get_by_id(shareholder_id)
        if not shareholder:
            QMessageBox.warning(self, "Ошибка", "Акционер не найден")
            return
        
        accounts = self.parent.account_model.get_by_shareholder(shareholder_id)
        
        # Получаем акции на всех счетах
        shares_on_accounts = []
        for account in accounts:
            shares = self.parent.account_model.get_shares_on_account(account['account_id'])
            for share in shares:
                share['account_number'] = account['account_number']
                shares_on_accounts.append(share)
        
        pdf_exporter = PDFExporter(self)
        pdf_exporter.export_shareholder_accounts_report(shareholder, accounts, shares_on_accounts)
    
    def export_account_shares_report(self):
        """Отчет о лицевом счете и акциях на нем"""
        account_id = self.report_account_combo.currentData()
        if not account_id:
            QMessageBox.warning(self, "Ошибка", "Выберите лицевой счет")
            return
        
        account = self.parent.account_model.get_by_id(account_id)
        if not account:
            QMessageBox.warning(self, "Ошибка", "Счет не найден")
            return
        
        shares = self.parent.account_model.get_shares_on_account(account_id)
        
        pdf_exporter = PDFExporter(self)
        pdf_exporter.export_account_shares_report(account, shares)
    
    def refresh(self):
        """Обновление всех данных"""
        self.load_data()