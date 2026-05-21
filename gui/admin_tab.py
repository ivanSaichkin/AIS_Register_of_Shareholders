# gui/admin_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QGroupBox, 
                             QLineEdit, QLabel, QMessageBox, QTabWidget)
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
        
        # Таблица компаний (без ID)
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
        # Выпуски акций
        self.share_issues_tab = QWidget()
        issues_layout = QVBoxLayout()
        
        # Поиск по рег номеру
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
        self.add_issue_btn.clicked.connect(self.add_issue)
        self.edit_issue_btn = QPushButton("Редактировать")
        self.edit_issue_btn.clicked.connect(self.edit_issue)
        self.delete_issue_btn = QPushButton("Удалить")
        self.delete_issue_btn.clicked.connect(self.delete_issue)
        
        issues_buttons.addWidget(self.add_issue_btn)
        issues_buttons.addWidget(self.edit_issue_btn)
        issues_buttons.addWidget(self.delete_issue_btn)
        issues_layout.addLayout(issues_buttons)
        
        self.share_issues_tab.setLayout(issues_layout)
        
        # Акционеры
        self.shareholders_tab = QWidget()
        shareholders_layout = QVBoxLayout()
        
        # Поиск по фамилии
        search_shareholders = QHBoxLayout()
        self.shareholder_search_input = QLineEdit()
        self.shareholder_search_input.setPlaceholderText("Поиск по ФИО/наименованию...")
        self.shareholder_search_input.textChanged.connect(self.search_shareholders)
        search_shareholders.addWidget(self.shareholder_search_input)
        
        self.shareholder_search_btn = QPushButton("Поиск")
        self.shareholder_search_btn.clicked.connect(self.search_shareholders)
        search_shareholders.addWidget(self.shareholder_search_btn)
        
        self.clear_shareholder_search_btn = QPushButton("Очистить")
        self.clear_shareholder_search_btn.clicked.connect(self.clear_shareholder_search)
        search_shareholders.addWidget(self.clear_shareholder_search_btn)
        
        shareholders_layout.addLayout(search_shareholders)
        
        self.shareholders_table = QTableWidget()
        self.shareholders_table.setColumnCount(6)
        self.shareholders_table.setHorizontalHeaderLabels(
            ["Тип", "Наименование", "ИНН", "Паспорт/ОГРН", "Адрес", "Статус"]
        )
        shareholders_layout.addWidget(self.shareholders_table)
        
        shareholders_buttons = QHBoxLayout()
        self.add_shareholder_btn = QPushButton("Добавить акционера")
        self.add_shareholder_btn.clicked.connect(self.add_shareholder)
        self.edit_shareholder_btn = QPushButton("Редактировать")
        self.edit_shareholder_btn.clicked.connect(self.edit_shareholder)
        self.delete_shareholder_btn = QPushButton("Удалить")
        self.delete_shareholder_btn.clicked.connect(self.delete_shareholder)
        
        shareholders_buttons.addWidget(self.add_shareholder_btn)
        shareholders_buttons.addWidget(self.edit_shareholder_btn)
        shareholders_buttons.addWidget(self.delete_shareholder_btn)
        shareholders_layout.addLayout(shareholders_buttons)
        
        self.shareholders_tab.setLayout(shareholders_layout)
        
        # Лицевые счета
        self.accounts_tab = QWidget()
        accounts_layout = QVBoxLayout()
        
        # Поиск по номеру счета
        search_accounts = QHBoxLayout()
        self.account_search_input = QLineEdit()
        self.account_search_input.setPlaceholderText("Поиск по номеру счета...")
        self.account_search_input.textChanged.connect(self.search_accounts)
        search_accounts.addWidget(self.account_search_input)
        
        self.account_search_btn = QPushButton("Поиск")
        self.account_search_btn.clicked.connect(self.search_accounts)
        search_accounts.addWidget(self.account_search_btn)
        
        self.clear_account_search_btn = QPushButton("Очистить")
        self.clear_account_search_btn.clicked.connect(self.clear_account_search)
        search_accounts.addWidget(self.clear_account_search_btn)
        
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
        self.add_account_btn.clicked.connect(self.add_account)
        self.edit_account_btn = QPushButton("Редактировать")
        self.edit_account_btn.clicked.connect(self.edit_account)
        self.delete_account_btn = QPushButton("Удалить")
        self.delete_account_btn.clicked.connect(self.delete_account)
        
        accounts_buttons.addWidget(self.add_account_btn)
        accounts_buttons.addWidget(self.edit_account_btn)
        accounts_buttons.addWidget(self.delete_account_btn)
        accounts_layout.addLayout(accounts_buttons)
        
        self.accounts_tab.setLayout(accounts_layout)
        
        # Отчеты
        self.reports_tab = QWidget()
        reports_layout = QVBoxLayout()
        
        # Отчет по городам
        city_report_group = QGroupBox("Отчет по городам")
        city_layout = QHBoxLayout()
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Введите город...")
        city_layout.addWidget(self.city_input)
        
        self.city_report_btn = QPushButton("Сформировать отчет")
        self.city_report_btn.clicked.connect(self.city_report)
        city_layout.addWidget(self.city_report_btn)
        
        self.city_pdf_btn = QPushButton("Сохранить в PDF")
        self.city_pdf_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.city_pdf_btn.clicked.connect(self.export_city_report_pdf)
        city_layout.addWidget(self.city_pdf_btn)
        
        city_report_group.setLayout(city_layout)
        reports_layout.addWidget(city_report_group)
        
        # Отчет по акционерам со статусом
        status_report_group = QGroupBox("Отчет по статусу акционеров")
        status_layout = QHBoxLayout()
        self.status_combo = QLineEdit()
        self.status_combo.setPlaceholderText("Статус (активный/заблокированный)")
        status_layout.addWidget(self.status_combo)
        
        self.status_report_btn = QPushButton("Сформировать отчет")
        self.status_report_btn.clicked.connect(self.status_report)
        status_layout.addWidget(self.status_report_btn)
        
        self.status_pdf_btn = QPushButton("Сохранить в PDF")
        self.status_pdf_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.status_pdf_btn.clicked.connect(self.export_status_report_pdf)
        status_layout.addWidget(self.status_pdf_btn)
        
        status_report_group.setLayout(status_layout)
        reports_layout.addWidget(status_report_group)
        
        # Текстовое поле для вывода отчета
        self.report_text = QTableWidget()
        self.report_text.setColumnCount(4)
        self.report_text.setHorizontalHeaderLabels(["Наименование", "ИНН", "Адрес", "Доп. информация"])
        reports_layout.addWidget(self.report_text)
        
        self.reports_tab.setLayout(reports_layout)
    
    def load_data(self):
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
            self.issues_table.setItem(i, 0, QTableWidgetItem(issue.get('company_name', issue.get('full_name', 'Неизвестно'))))
            self.issues_table.setItem(i, 1, QTableWidgetItem(issue.get('registration_number', '')))
            self.issues_table.setItem(i, 2, QTableWidgetItem(str(issue.get('registration_date', ''))))
            self.issues_table.setItem(i, 3, QTableWidgetItem(issue.get('share_type', '')))
            self.issues_table.setItem(i, 4, QTableWidgetItem(issue.get('category_series', '')))
            self.issues_table.setItem(i, 5, QTableWidgetItem(str(issue.get('quantity', '0'))))
            self.issues_table.setItem(i, 6, QTableWidgetItem(f"{issue.get('nominal_value', 0):,.2f}"))
            self.issues_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, issue.get('issue_id'))
        
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
                self.issues_table.setItem(0, 0, QTableWidgetItem(issue.get('company_name', issue.get('full_name', 'Неизвестно'))))
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
                QMessageBox.information(self, "Результат поиска", "Выпуск акций с таким регистрационным номером не найден")
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
                QMessageBox.information(self, "Результат поиска", "Лицевой счет не найден")
        else:
            self.load_data()
    
    def clear_account_search(self):
        self.account_search_input.clear()
        self.load_data()
    
    def add_company(self):
        dialog = CompanyDialog(self, self.parent.company_model)
        if dialog.exec():
            self.load_data()
    
    def edit_company(self):
        company_id = self.get_selected_company_id()
        if company_id:
            company = self.parent.company_model.get_by_id(company_id)
            if company:
                dialog = CompanyDialog(self, self.parent.company_model, company)
                if dialog.exec():
                    self.load_data()
        else:
            QMessageBox.warning(self, "Предупреждение", "Выберите запись для редактирования")
    
    def delete_company(self):
        company_id = self.get_selected_company_id()
        if company_id:
            reply = QMessageBox.question(self, "Подтверждение", 
                                        "Удалить акционерное общество?",
                                        QMessageBox.StandardButton.Yes | 
                                        QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.parent.company_model.delete(company_id)
                self.load_data()
        else:
            QMessageBox.warning(self, "Предупреждение", "Выберите запись для удаления")
    
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
                                        QMessageBox.StandardButton.Yes | 
                                        QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.parent.share_issue_model.delete(issue_id)
                self.load_data()
        else:
            QMessageBox.warning(self, "Предупреждение", "Выберите запись для удаления")
    
    def add_shareholder(self):
        dialog = ShareholderDialog(self, self.parent.shareholder_model)
        if dialog.exec():
            self.load_data()
    
    def edit_shareholder(self):
        shareholder_id = self.get_selected_shareholder_id()
        if shareholder_id:
            shareholder = self.parent.shareholder_model.get_by_id(shareholder_id)
            if shareholder:
                dialog = ShareholderDialog(self, self.parent.shareholder_model, shareholder)
                if dialog.exec():
                    self.load_data()
        else:
            QMessageBox.warning(self, "Предупреждение", "Выберите запись для редактирования")
    
    def delete_shareholder(self):
        shareholder_id = self.get_selected_shareholder_id()
        if shareholder_id:
            reply = QMessageBox.question(self, "Подтверждение", "Удалить акционера?",
                                        QMessageBox.StandardButton.Yes | 
                                        QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    self.parent.shareholder_model.delete(shareholder_id)
                    self.load_data()
                except ValueError as e:
                    QMessageBox.warning(self, "Ошибка", str(e))
        else:
            QMessageBox.warning(self, "Предупреждение", "Выберите запись для удаления")
    
    def add_account(self):
        dialog = AccountDialog(self, self.parent.account_model, self.parent.shareholder_model)
        if dialog.exec():
            self.load_data()
    
    def edit_account(self):
        account_id = self.get_selected_account_id()
        if account_id:
            account = self.parent.account_model.get_by_id(account_id)
            if account:
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
                QMessageBox.warning(self, "Ошибка", "Нельзя удалить счет с положительным остатком")
            else:
                reply = QMessageBox.question(self, "Подтверждение", "Удалить лицевой счет?",
                                            QMessageBox.StandardButton.Yes | 
                                            QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    self.parent.account_model.db.execute_delete(
                        "DELETE FROM accounts WHERE account_id = %s", (account_id,)
                    )
                    self.load_data()
        else:
            QMessageBox.warning(self, "Предупреждение", "Выберите запись для удаления")
    
    def city_report(self):
        city = self.city_input.text().strip()
        if city:
            companies = self.parent.company_model.get_by_city(city)
            if companies:
                self.report_text.setRowCount(len(companies))
                self.report_text.setColumnCount(4)
                self.report_text.setHorizontalHeaderLabels(
                    ["Наименование", "ИНН", "Адрес", "Уставной капитал"]
                )
                for i, company in enumerate(companies):
                    self.report_text.setItem(i, 0, QTableWidgetItem(company['full_name']))
                    self.report_text.setItem(i, 1, QTableWidgetItem(company['inn']))
                    self.report_text.setItem(i, 2, QTableWidgetItem(company['address']))
                    self.report_text.setItem(i, 3, QTableWidgetItem(f"{company['authorized_capital']:,.2f}"))
                self.report_text.resizeColumnsToContents()
            else:
                QMessageBox.information(self, "Результат", f"Компании в городе '{city}' не найдены")
        else:
            QMessageBox.warning(self, "Ошибка", "Введите город для поиска")
    
    def status_report(self):
        status = self.status_combo.text().strip()
        if status:
            shareholders = self.parent.shareholder_model.get_by_status(status)
            if shareholders:
                self.report_text.setRowCount(len(shareholders))
                self.report_text.setColumnCount(4)
                self.report_text.setHorizontalHeaderLabels(
                    ["Наименование", "Тип", "ИНН", "Статус"]
                )
                for i, sh in enumerate(shareholders):
                    self.report_text.setItem(i, 0, QTableWidgetItem(sh['name']))
                    self.report_text.setItem(i, 1, QTableWidgetItem('Физическое' if sh['type'] == 'individual' else 'Юридическое'))
                    self.report_text.setItem(i, 2, QTableWidgetItem(sh.get('inn', '')))
                    self.report_text.setItem(i, 3, QTableWidgetItem(sh['status']))
                self.report_text.resizeColumnsToContents()
            else:
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
    
    def refresh(self):
        self.load_data()