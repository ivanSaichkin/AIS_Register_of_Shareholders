# gui/dialogs.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QPushButton, QHBoxLayout, QComboBox, QDateEdit,
                             QTextEdit, QMessageBox)
from PyQt6.QtCore import QDate
from datetime import date

class CompanyDialog(QDialog):
    def __init__(self, parent, company_model, company_data=None):
        super().__init__(parent)
        self.model = company_model
        self.company_data = company_data
        self.setup_ui()
        
        if company_data:
            self.setWindowTitle("Редактирование АО")
            self.load_data()
        else:
            self.setWindowTitle("Добавление АО")
    
    def setup_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()
        
        self.full_name = QLineEdit()
        self.short_name = QLineEdit()
        self.inn = QLineEdit()
        self.ogrn = QLineEdit()
        self.address = QTextEdit()
        self.address.setMaximumHeight(80)
        self.authorized_capital = QLineEdit()
        self.city = QLineEdit()
        
        form.addRow("Полное наименование:", self.full_name)
        form.addRow("Сокращенное наименование:", self.short_name)
        form.addRow("ИНН:", self.inn)
        form.addRow("ОГРН:", self.ogrn)
        form.addRow("Адрес:", self.address)
        form.addRow("Уставной капитал (руб.):", self.authorized_capital)
        form.addRow("Город:", self.city)
        
        layout.addLayout(form)
        
        # Кнопки
        buttons = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(self.save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        
        self.setLayout(layout)
    
    def load_data(self):
        self.full_name.setText(self.company_data['full_name'])
        self.short_name.setText(self.company_data['short_name'])
        self.inn.setText(self.company_data['inn'])
        self.ogrn.setText(self.company_data['ogrn'])
        self.address.setPlainText(self.company_data['address'])
        self.authorized_capital.setText(str(self.company_data['authorized_capital']))
        self.city.setText(self.company_data.get('city', ''))
    
    def save(self):
        data = {
            'full_name': self.full_name.text(),
            'short_name': self.short_name.text(),
            'inn': self.inn.text(),
            'ogrn': self.ogrn.text(),
            'address': self.address.toPlainText(),
            'authorized_capital': float(self.authorized_capital.text()),
            'city': self.city.text()
        }
        
        try:
            if self.company_data:
                self.model.update(self.company_data['company_id'], data)
            else:
                self.model.create(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")


class ShareIssueDialog(QDialog):
    def __init__(self, parent, issue_model, company_model, issue_data=None):
        super().__init__(parent)
        self.model = issue_model
        self.company_model = company_model
        self.issue_data = issue_data
        self.setup_ui()
        
        if issue_data:
            self.setWindowTitle("Редактирование выпуска")
            self.load_data()
        else:
            self.setWindowTitle("Добавление выпуска")
    
    def setup_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()
        
        # Выбор компании
        self.company_combo = QComboBox()
        companies = self.company_model.get_all()
        self.company_ids = {}
        for company in companies:
            self.company_combo.addItem(f"{company['full_name']} ({company['short_name']})")
            self.company_ids[company['full_name']] = company['company_id']
        
        self.registration_number = QLineEdit()
        self.registration_date = QDateEdit()
        self.registration_date.setDate(QDate.currentDate())
        self.registration_date.setCalendarPopup(True)
        
        self.share_type = QComboBox()
        self.share_type.addItems(["обыкновенная", "привилегированная"])
        
        self.category_series = QLineEdit()
        self.quantity = QLineEdit()
        self.nominal_value = QLineEdit()
        self.status = QLineEdit()
        self.status.setText("размещен")
        
        form.addRow("Акционерное общество:", self.company_combo)
        form.addRow("Регистрационный номер:", self.registration_number)
        form.addRow("Дата регистрации:", self.registration_date)
        form.addRow("Тип акций:", self.share_type)
        form.addRow("Категория/Серия:", self.category_series)
        form.addRow("Количество:", self.quantity)
        form.addRow("Номинальная стоимость:", self.nominal_value)
        form.addRow("Статус:", self.status)
        
        layout.addLayout(form)
        
        buttons = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(self.save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        
        self.setLayout(layout)
    
    def load_data(self):
        company = self.company_model.get_by_id(self.issue_data['company_id'])
        index = self.company_combo.findText(f"{company['full_name']} ({company['short_name']})")
        if index >= 0:
            self.company_combo.setCurrentIndex(index)
        
        self.registration_number.setText(self.issue_data['registration_number'])
        self.registration_date.setDate(self.issue_data['registration_date'])
        self.share_type.setCurrentText(self.issue_data['share_type'])
        self.category_series.setText(self.issue_data.get('category_series', ''))
        self.quantity.setText(str(self.issue_data['quantity']))
        self.nominal_value.setText(str(self.issue_data['nominal_value']))
        self.status.setText(self.issue_data.get('status', 'размещен'))
    
    def save(self):
        company_name = self.company_combo.currentText().split(' (')[0]
        company_id = self.company_ids.get(company_name)
        
        data = {
            'company_id': company_id,
            'registration_number': self.registration_number.text(),
            'registration_date': self.registration_date.date().toPyDate(),
            'share_type': self.share_type.currentText(),
            'category_series': self.category_series.text(),
            'quantity': int(self.quantity.text()),
            'nominal_value': float(self.nominal_value.text()),
            'status': self.status.text()
        }
        
        try:
            if self.issue_data:
                self.model.update(self.issue_data['issue_id'], data)
            else:
                self.model.create(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")


class ShareholderDialog(QDialog):
    def __init__(self, parent, shareholder_model, shareholder_data=None):
        super().__init__(parent)
        self.model = shareholder_model
        self.shareholder_data = shareholder_data
        self.setup_ui()
        
        if shareholder_data:
            self.setWindowTitle("Редактирование акционера")
            self.load_data()
        else:
            self.setWindowTitle("Добавление акционера")
    
    def setup_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["individual", "legal"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        
        self.name = QLineEdit()
        self.inn = QLineEdit()
        self.passport_data = QLineEdit()
        self.passport_data.setPlaceholderText("Для физических лиц")
        self.ogrn = QLineEdit()
        self.ogrn.setPlaceholderText("Для юридических лиц")
        self.address = QTextEdit()
        self.address.setMaximumHeight(80)
        self.status = QLineEdit()
        self.status.setText("активный")
        
        form.addRow("Тип (individual/legal):", self.type_combo)
        form.addRow("ФИО/Наименование:", self.name)
        form.addRow("ИНН:", self.inn)
        form.addRow("Паспортные данные/ОГРН:", self.passport_data)
        form.addRow("Адрес:", self.address)
        form.addRow("Статус:", self.status)
        
        layout.addLayout(form)
        
        buttons = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(self.save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        
        self.setLayout(layout)
        self.on_type_changed(self.type_combo.currentText())
    
    def on_type_changed(self, type_text):
        if type_text == "individual":
            self.passport_data.setPlaceholderText("Паспортные данные")
            self.ogrn.setEnabled(False)
            self.ogrn.setText("")
        else:
            self.passport_data.setPlaceholderText("ОГРН")
            self.passport_data.setText("")
            self.ogrn.setEnabled(True)
    
    def load_data(self):
        self.type_combo.setCurrentText(self.shareholder_data['type'])
        self.name.setText(self.shareholder_data['name'])
        self.inn.setText(self.shareholder_data.get('inn', ''))
        passport = self.shareholder_data.get('passport_data', '') or self.shareholder_data.get('ogrn', '')
        self.passport_data.setText(passport)
        self.address.setPlainText(self.shareholder_data['address'])
        self.status.setText(self.shareholder_data['status'])
    
    def save(self):
        data = {
            'type': self.type_combo.currentText(),
            'name': self.name.text(),
            'inn': self.inn.text(),
            'address': self.address.toPlainText(),
            'status': self.status.text()
        }
        
        if self.type_combo.currentText() == "individual":
            data['passport_data'] = self.passport_data.text()
            data['ogrn'] = None
        else:
            data['ogrn'] = self.passport_data.text()
            data['passport_data'] = None
        
        try:
            if self.shareholder_data:
                self.model.update(self.shareholder_data['shareholder_id'], data)
            else:
                self.model.create(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")


class AccountDialog(QDialog):
    def __init__(self, parent, account_model, shareholder_model, account_data=None):
        super().__init__(parent)
        self.model = account_model
        self.shareholder_model = shareholder_model
        self.account_data = account_data
        self.setup_ui()
        
        if account_data:
            self.setWindowTitle("Редактирование счета")
            self.load_data()
        else:
            self.setWindowTitle("Добавление счета")
    
    def setup_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()
        
        # Выбор акционера
        self.shareholder_combo = QComboBox()
        shareholders = self.shareholder_model.get_all()
        self.shareholder_ids = {}
        for sh in shareholders:
            self.shareholder_combo.addItem(f"{sh['name']} ({sh['type']})")
            self.shareholder_ids[sh['name']] = sh['shareholder_id']
        
        self.account_number = QLineEdit()
        self.open_date = QDateEdit()
        self.open_date.setDate(QDate.currentDate())
        self.open_date.setCalendarPopup(True)
        
        self.close_date = QDateEdit()
        self.close_date.setDate(QDate(2099, 12, 31))
        self.close_date.setCalendarPopup(True)
        self.close_date.setEnabled(False)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["активный", "закрытый"])
        self.status_combo.currentTextChanged.connect(self.on_status_changed)
        
        form.addRow("Акционер:", self.shareholder_combo)
        form.addRow("Номер счета:", self.account_number)
        form.addRow("Дата открытия:", self.open_date)
        form.addRow("Дата закрытия:", self.close_date)
        form.addRow("Статус:", self.status_combo)
        
        layout.addLayout(form)
        
        buttons = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(self.save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        
        self.setLayout(layout)
    
    def on_status_changed(self, status):
        self.close_date.setEnabled(status == "закрытый")
    
    def load_data(self):
        shareholder = self.shareholder_model.get_by_id(self.account_data['shareholder_id'])
        index = self.shareholder_combo.findText(f"{shareholder['name']} ({shareholder['type']})")
        if index >= 0:
            self.shareholder_combo.setCurrentIndex(index)
        
        self.account_number.setText(self.account_data['account_number'])
        self.open_date.setDate(self.account_data['open_date'])
        if self.account_data.get('close_date'):
            self.close_date.setDate(self.account_data['close_date'])
        self.status_combo.setCurrentText(self.account_data['status'])
    
    def save(self):
        shareholder_name = self.shareholder_combo.currentText().split(' (')[0]
        shareholder_id = self.shareholder_ids.get(shareholder_name)
        
        data = {
            'shareholder_id': shareholder_id,
            'account_number': self.account_number.text(),
            'open_date': self.open_date.date().toPyDate(),
            'status': self.status_combo.currentText()
        }
        
        if self.status_combo.currentText() == "закрытый":
            data['close_date'] = self.close_date.date().toPyDate()
        else:
            data['close_date'] = None
        
        try:
            if self.account_data:
                self.model.update(self.account_data['account_id'], data)
            else:
                self.model.create(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")

class OperationDialog(QDialog):
    """Диалог для добавления операции"""
    def __init__(self, parent, operation_model, account_model, share_issue_model):
        super().__init__(parent)
        self.model = operation_model
        self.account_model = account_model
        self.share_issue_model = share_issue_model
        self.setup_ui()
        self.setWindowTitle("Добавление операции")
    
    def setup_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()
        
        # Выбор счета
        self.account_combo = QComboBox()
        accounts = self.account_model.get_all()
        self.account_ids = {}
        for acc in accounts:
            self.account_combo.addItem(f"{acc['account_number']} - {acc['shareholder_name']}")
            self.account_ids[acc['account_number']] = acc['account_id']
        
        # Тип операции
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Зачисление", "Списание"])
        
        # Дата
        self.operation_date = QDateEdit()
        self.operation_date.setDate(QDate.currentDate())
        self.operation_date.setCalendarPopup(True)
        
        # Выпуск акций
        self.issue_combo = QComboBox()
        issues = self.share_issue_model.get_all()
        self.issue_ids = {}
        for issue in issues:
            self.issue_combo.addItem(f"{issue['registration_number']} - {issue['company_name']}")
            self.issue_ids[issue['registration_number']] = issue['issue_id']
        
        self.quantity = QLineEdit()
        self.basis_document = QLineEdit()
        self.basis_document.setPlaceholderText("Договор, свидетельство и т.д.")
        
        form.addRow("Лицевой счет:", self.account_combo)
        form.addRow("Тип операции:", self.type_combo)
        form.addRow("Дата операции:", self.operation_date)
        form.addRow("Выпуск акций:", self.issue_combo)
        form.addRow("Количество акций:", self.quantity)
        form.addRow("Основание:", self.basis_document)
        
        layout.addLayout(form)
        
        buttons = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(self.save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        
        self.setLayout(layout)
    
    def save(self):
        account_number = self.account_combo.currentText().split(' - ')[0]
        account_id = self.account_ids.get(account_number)
        
        issue_number = self.issue_combo.currentText().split(' - ')[0]
        issue_id = self.issue_ids.get(issue_number)
        
        try:
            quantity = int(self.quantity.text())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Количество акций должно быть положительным числом")
            return
        
        data = {
            'account_id': account_id,
            'type_id': 1 if self.type_combo.currentText() == "Зачисление" else 2,
            'operation_date': self.operation_date.date().toPyDate(),
            'share_issue_id': issue_id,
            'quantity': quantity,
            'basis_document': self.basis_document.text()
        }
        
        try:
            self.model.create(data)
            
            # Обновление остатка на счете
            account = self.account_model.get_by_id(account_id)
            if data['type_id'] == 1:
                new_balance = account['current_balance'] + quantity
                self.account_model.db.execute_update(
                    "UPDATE accounts SET current_balance = %s WHERE account_id = %s",
                    (new_balance, account_id)
                )
                self.account_model.add_shares(account_id, issue_id, quantity)
            else:
                if quantity > account['current_balance']:
                    QMessageBox.warning(self, "Ошибка", "Недостаточно акций на счете")
                    return
                new_balance = account['current_balance'] - quantity
                self.account_model.db.execute_update(
                    "UPDATE accounts SET current_balance = %s WHERE account_id = %s",
                    (new_balance, account_id)
                )
                self.account_model.db.execute_update("""
                    UPDATE account_shares 
                    SET quantity = quantity - %s 
                    WHERE account_id = %s AND issue_id = %s AND quantity >= %s
                """, (quantity, account_id, issue_id, quantity))
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")