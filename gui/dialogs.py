# gui/dialogs.py - ПОЛНОСТЬЮ ИСПРАВЛЕННАЯ ВЕРСИЯ
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QPushButton, QHBoxLayout, QComboBox, QDateEdit,
                             QTextEdit, QMessageBox, QCheckBox, QLabel)
from PyQt6.QtCore import QDate
from datetime import date

class CompanyDialog(QDialog):
    """Диалог для добавления/редактирования акционерного общества"""
    
    def __init__(self, parent, company_model, company_data=None):
        super().__init__(parent)
        self.model = company_model
        self.company_data = company_data
        self.setup_ui()
        
        if company_data:
            self.setWindowTitle("Редактирование акционерного общества")
            self.load_data()
        else:
            self.setWindowTitle("Добавление акционерного общества")
    
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
        
        # Чекбокс для автоматического создания пользователя
        self.auto_user_checkbox = QCheckBox("Автоматически создать пользователя для сотрудника АО")
        self.auto_user_checkbox.setChecked(True)
        
        form.addRow("Полное наименование:", self.full_name)
        form.addRow("Сокращенное наименование:", self.short_name)
        form.addRow("ИНН:", self.inn)
        form.addRow("ОГРН:", self.ogrn)
        form.addRow("Адрес:", self.address)
        form.addRow("Уставной капитал (руб.):", self.authorized_capital)
        form.addRow("Город:", self.city)
        form.addRow("", self.auto_user_checkbox)
        
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
        self.full_name.setText(self.company_data['full_name'])
        self.short_name.setText(self.company_data['short_name'])
        self.inn.setText(self.company_data['inn'])
        self.ogrn.setText(self.company_data['ogrn'])
        self.address.setPlainText(self.company_data['address'])
        self.authorized_capital.setText(str(self.company_data['authorized_capital']))
        self.city.setText(self.company_data.get('city', ''))
        self.auto_user_checkbox.setChecked(False)
    
    def save(self):
        if not self.full_name.text():
            QMessageBox.warning(self, "Ошибка", "Введите полное наименование")
            return
        if not self.short_name.text():
            QMessageBox.warning(self, "Ошибка", "Введите сокращенное наименование")
            return
        if not self.inn.text():
            QMessageBox.warning(self, "Ошибка", "Введите ИНН")
            return
        if not self.ogrn.text():
            QMessageBox.warning(self, "Ошибка", "Введите ОГРН")
            return
        if not self.address.toPlainText():
            QMessageBox.warning(self, "Ошибка", "Введите адрес")
            return
        if not self.authorized_capital.text():
            QMessageBox.warning(self, "Ошибка", "Введите уставной капитал")
            return
        
        try:
            data = {
                'full_name': self.full_name.text(),
                'short_name': self.short_name.text(),
                'inn': self.inn.text(),
                'ogrn': self.ogrn.text(),
                'address': self.address.toPlainText(),
                'authorized_capital': float(self.authorized_capital.text()),
                'city': self.city.text() if self.city.text() else None
            }
            
            if self.company_data:
                self.model.update(self.company_data['company_id'], data)
                QMessageBox.information(self, "Успех", "Данные обновлены")
            else:
                company_id = self.model.create(data)
                
                if self.auto_user_checkbox.isChecked() and company_id:
                    from database.models import UserModel
                    user_model = UserModel(self.model.db)
                    username = f"emp_{self.short_name.text().lower().replace(' ', '_')[:20]}"
                    user_model.create_user(username, 'employee', None, company_id)
                    QMessageBox.information(self, "Успех", 
                        f"Акционерное общество добавлено.\n"
                        f"Создан пользователь для сотрудника: {username}")
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")


class ShareIssueDialog(QDialog):
    """Диалог для добавления/редактирования выпуска акций"""
    
    def __init__(self, parent, issue_model, company_model, issue_data=None):
        super().__init__(parent)
        self.model = issue_model
        self.company_model = company_model
        self.issue_data = issue_data
        self.setup_ui()
        
        if issue_data:
            self.setWindowTitle("Редактирование выпуска акций")
            self.load_data()
        else:
            self.setWindowTitle("Добавление выпуска акций")
    
    def setup_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()
        
        # Выбор компании
        self.company_combo = QComboBox()
        companies = self.company_model.get_all()
        self.company_ids = {}
        for company in companies:
            self.company_combo.addItem(f"{company['full_name']}")
            self.company_ids[company['full_name']] = company['company_id']
        
        self.registration_number = QLineEdit()
        self.registration_number.setPlaceholderText("Пример: 1-01-00028-A")
        
        self.registration_date = QDateEdit()
        self.registration_date.setDate(QDate.currentDate())
        self.registration_date.setCalendarPopup(True)
        
        self.share_type = QComboBox()
        self.share_type.addItems(["обыкновенная", "привилегированная"])
        
        self.category_series = QLineEdit()
        self.category_series.setPlaceholderText("Например: 01")
        
        self.quantity = QLineEdit()
        self.nominal_value = QLineEdit()
        self.status = QLineEdit()
        self.status.setText("размещен")
        
        form.addRow("Акционерное общество:", self.company_combo)
        form.addRow("Регистрационный номер:", self.registration_number)
        form.addRow("Дата регистрации:", self.registration_date)
        form.addRow("Тип акций:", self.share_type)
        form.addRow("Категория/Серия:", self.category_series)
        form.addRow("Количество акций:", self.quantity)
        form.addRow("Номинальная стоимость (руб.):", self.nominal_value)
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
        if company:
            index = self.company_combo.findText(company['full_name'])
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
        if not self.registration_number.text():
            QMessageBox.warning(self, "Ошибка", "Введите регистрационный номер")
            return
        if not self.quantity.text():
            QMessageBox.warning(self, "Ошибка", "Введите количество акций")
            return
        if not self.nominal_value.text():
            QMessageBox.warning(self, "Ошибка", "Введите номинальную стоимость")
            return
        
        try:
            quantity = int(self.quantity.text())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Количество акций должно быть положительным целым числом")
            return
        
        try:
            nominal = float(self.nominal_value.text())
            if nominal <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Номинальная стоимость должна быть положительным числом")
            return
        
        company_name = self.company_combo.currentText()
        company_id = self.company_ids.get(company_name)
        
        data = {
            'company_id': company_id,
            'registration_number': self.registration_number.text(),
            'registration_date': self.registration_date.date().toPyDate(),
            'share_type': self.share_type.currentText(),
            'category_series': self.category_series.text() if self.category_series.text() else None,
            'quantity': quantity,
            'nominal_value': nominal,
            'status': self.status.text() if self.status.text() else 'размещен'
        }
        
        try:
            if self.issue_data:
                self.model.update(self.issue_data['issue_id'], data)
                QMessageBox.information(self, "Успех", "Данные обновлены")
            else:
                self.model.create(data)
                QMessageBox.information(self, "Успех", "Выпуск акций добавлен")
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")


class ShareholderDialog(QDialog):
    """Диалог для добавления/редактирования акционера"""
    
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
        self.passport_data.setPlaceholderText("Для физических лиц - серия и номер паспорта")
        self.ogrn = QLineEdit()
        self.ogrn.setPlaceholderText("Для юридических лиц - ОГРН")
        self.address = QTextEdit()
        self.address.setMaximumHeight(80)
        self.status = QComboBox()
        self.status.addItems(["активный", "заблокированный", "неактивный"])
        
        # Чекбокс для автоматического создания пользователя
        self.auto_user_checkbox = QCheckBox("Автоматически создать пользователя для акционера")
        self.auto_user_checkbox.setChecked(True)
        
        form.addRow("Тип:", self.type_combo)
        form.addRow("ФИО/Наименование:", self.name)
        form.addRow("ИНН:", self.inn)
        form.addRow("Паспортные данные/ОГРН:", self.passport_data)
        form.addRow("Адрес:", self.address)
        form.addRow("Статус:", self.status)
        form.addRow("", self.auto_user_checkbox)
        
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
            self.passport_data.setPlaceholderText("Серия и номер паспорта")
            self.passport_data.setEnabled(True)
            self.ogrn.setEnabled(False)
            self.ogrn.clear()
        else:
            self.passport_data.setPlaceholderText("ОГРН")
            self.passport_data.setEnabled(True)
            self.ogrn.setEnabled(True)
    
    def load_data(self):
        self.type_combo.setCurrentText(self.shareholder_data['type'])
        self.name.setText(self.shareholder_data['name'])
        self.inn.setText(self.shareholder_data.get('inn', ''))
        passport = self.shareholder_data.get('passport_data', '') or self.shareholder_data.get('ogrn', '')
        self.passport_data.setText(passport)
        self.address.setPlainText(self.shareholder_data['address'])
        self.status.setCurrentText(self.shareholder_data['status'])
        self.auto_user_checkbox.setChecked(False)
    
    def save(self):
        if not self.name.text():
            QMessageBox.warning(self, "Ошибка", "Введите ФИО/наименование")
            return
        if not self.address.toPlainText():
            QMessageBox.warning(self, "Ошибка", "Введите адрес")
            return
        
        data = {
            'type': self.type_combo.currentText(),
            'name': self.name.text(),
            'inn': self.inn.text() if self.inn.text() else None,
            'address': self.address.toPlainText(),
            'status': self.status.currentText()
        }
        
        if self.type_combo.currentText() == "individual":
            data['passport_data'] = self.passport_data.text() if self.passport_data.text() else None
            data['ogrn'] = None
        else:
            data['ogrn'] = self.passport_data.text() if self.passport_data.text() else None
            data['passport_data'] = None
        
        try:
            if self.shareholder_data:
                self.model.update(self.shareholder_data['shareholder_id'], data)
                QMessageBox.information(self, "Успех", "Данные обновлены")
            else:
                shareholder_id = self.model.create(data)
                
                if self.auto_user_checkbox.isChecked() and shareholder_id:
                    from database.models import UserModel
                    user_model = UserModel(self.model.db)
                    username = self.name.text().lower().replace(' ', '_')[:30]
                    # Убираем недопустимые символы
                    username = ''.join(c for c in username if c.isalnum() or c == '_')
                    user_model.create_user(username, 'shareholder', shareholder_id, None)
                    QMessageBox.information(self, "Успех", 
                        f"Акционер добавлен.\n"
                        f"Создан пользователь: {username}")
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")


class AccountDialog(QDialog):
    """Диалог для добавления/редактирования лицевого счета"""
    
    def __init__(self, parent, account_model, shareholder_model, account_data=None):
        super().__init__(parent)
        self.model = account_model
        self.shareholder_model = shareholder_model
        self.account_data = account_data
        self.setup_ui()
        
        if account_data:
            self.setWindowTitle("Редактирование лицевого счета")
            self.load_data()
        else:
            self.setWindowTitle("Добавление лицевого счета")
    
    def setup_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()
        
        # Выбор акционера
        self.shareholder_combo = QComboBox()
        shareholders = self.shareholder_model.get_all()
        self.shareholder_ids = {}
        for sh in shareholders:
            display_text = f"{sh['name']} ({'Физ' if sh['type'] == 'individual' else 'Юр'})"
            self.shareholder_combo.addItem(display_text)
            self.shareholder_ids[display_text] = sh['shareholder_id']
        
        self.account_number = QLineEdit()
        self.account_number.setPlaceholderText("Уникальный номер счета")
        
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
        if status == "закрытый":
            self.close_date.setDate(QDate.currentDate())
    
    def load_data(self):
        # Находим акционера
        shareholder = self.shareholder_model.get_by_id(self.account_data['shareholder_id'])
        if shareholder:
            display_text = f"{shareholder['name']} ({'Физ' if shareholder['type'] == 'individual' else 'Юр'})"
            index = self.shareholder_combo.findText(display_text)
            if index >= 0:
                self.shareholder_combo.setCurrentIndex(index)
        
        self.account_number.setText(self.account_data['account_number'])
        self.open_date.setDate(self.account_data['open_date'])
        if self.account_data.get('close_date'):
            self.close_date.setDate(self.account_data['close_date'])
        self.status_combo.setCurrentText(self.account_data['status'])
    
    def save(self):
        if not self.account_number.text():
            QMessageBox.warning(self, "Ошибка", "Введите номер счета")
            return
        
        shareholder_display = self.shareholder_combo.currentText()
        shareholder_id = self.shareholder_ids.get(shareholder_display)
        
        if not shareholder_id:
            QMessageBox.warning(self, "Ошибка", "Выберите акционера")
            return
        
        data = {
            'shareholder_id': shareholder_id,
            'account_number': self.account_number.text(),
            'open_date': self.open_date.date().toPyDate(),
            'status': self.status_combo.currentText(),
            'current_balance': self.account_data.get('current_balance', 0) if self.account_data else 0
        }
        
        if self.status_combo.currentText() == "закрытый":
            data['close_date'] = self.close_date.date().toPyDate()
        else:
            data['close_date'] = None
        
        try:
            if self.account_data:
                self.model.update(self.account_data['account_id'], data)
                QMessageBox.information(self, "Успех", "Данные обновлены")
            else:
                self.model.create(data)
                QMessageBox.information(self, "Успех", "Лицевой счет добавлен")
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")


class OperationDialog(QDialog):
    """Диалог для добавления операции по лицевому счету с выбором выпуска акций"""
    
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
        self.load_accounts()
        self.account_combo.currentIndexChanged.connect(self.on_account_changed)
        
        # Тип операции
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Зачисление", "Списание"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        
        # Дата
        self.operation_date = QDateEdit()
        self.operation_date.setDate(QDate.currentDate())
        self.operation_date.setCalendarPopup(True)
        
        # Выпуск акций
        self.issue_combo = QComboBox()
        self.load_issues()
        self.issue_combo.currentIndexChanged.connect(self.check_quantity)
        
        # Количество
        self.quantity = QLineEdit()
        self.quantity.textChanged.connect(self.check_quantity)
        
        # Информация о доступном количестве (для списания)
        self.available_label = QLabel()
        self.available_label.setStyleSheet("color: #666; font-size: 10px;")
        
        # Основание
        self.basis_document = QLineEdit()
        self.basis_document.setPlaceholderText("Договор, свидетельство и т.д.")
        
        form.addRow("Лицевой счет:", self.account_combo)
        form.addRow("Тип операции:", self.type_combo)
        form.addRow("Дата операции:", self.operation_date)
        form.addRow("Выпуск акций:", self.issue_combo)
        form.addRow("Количество акций:", self.quantity)
        form.addRow("", self.available_label)
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
        
        # Обновляем информацию при первом открытии
        self.on_account_changed()
        self.on_type_changed()
    
    def load_accounts(self):
        """Загрузка лицевых счетов"""
        accounts = self.account_model.get_all()
        self.account_ids = {}
        self.account_combo.clear()
        for acc in accounts:
            display_text = f"{acc['account_number']} - {acc['shareholder_name']} (остаток: {acc['current_balance']})"
            self.account_combo.addItem(display_text)
            self.account_ids[display_text] = acc['account_id']
    
    def load_issues(self):
        """Загрузка выпусков акций"""
        issues = self.share_issue_model.get_all()
        self.issue_ids = {}
        self.issue_combo.clear()
        for issue in issues:
            display_text = f"{issue['registration_number']} - {issue['company_name']} ({issue['share_type']}, номинал: {issue['nominal_value']} руб.)"
            self.issue_combo.addItem(display_text)
            self.issue_ids[display_text] = issue['issue_id']
    
    def on_account_changed(self):
        """При смене счета - проверяем доступные акции для списания"""
        self.check_quantity()
    
    def on_type_changed(self):
        """При смене типа операции - меняем интерфейс"""
        self.check_quantity()
    
    def check_quantity(self):
        """Проверка количества акций при списании"""
        if self.type_combo.currentText() == "Списание":
            account_display = self.account_combo.currentText()
            account_id = self.account_ids.get(account_display)
            
            if account_id:
                # Получаем остаток по выбранному выпуску
                issue_display = self.issue_combo.currentText()
                issue_id = self.issue_ids.get(issue_display) if issue_display else None
                
                if issue_id:
                    # Запрашиваем количество акций данного выпуска на счете
                    shares = self.account_model.get_shares_on_account(account_id)
                    available = 0
                    for share in shares:
                        if share['issue_id'] == issue_id:
                            available = share['quantity']
                            break
                    
                    self.available_label.setText(f"Доступно акций этого выпуска: {available}")
                    
                    # Проверяем введенное количество
                    try:
                        qty = int(self.quantity.text()) if self.quantity.text() else 0
                        if qty > available:
                            self.available_label.setStyleSheet("color: red; font-size: 10px;")
                            self.available_label.setText(f"Ошибка: доступно только {available} акций!")
                        else:
                            self.available_label.setStyleSheet("color: green; font-size: 10px;")
                    except:
                        pass
                else:
                    self.available_label.setText("Выберите выпуск акций")
            else:
                self.available_label.setText("Выберите лицевой счет")
        else:
            self.available_label.setText("")
    
    def save(self):
        account_display = self.account_combo.currentText()
        account_id = self.account_ids.get(account_display)
        
        if not account_id:
            QMessageBox.warning(self, "Ошибка", "Выберите лицевой счет")
            return
        
        issue_display = self.issue_combo.currentText()
        issue_id = self.issue_ids.get(issue_display)
        
        if not issue_id:
            QMessageBox.warning(self, "Ошибка", "Выберите выпуск акций")
            return
        
        try:
            quantity = int(self.quantity.text())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Количество акций должно быть положительным целым числом")
            return
        
        # Получаем текущий баланс счета по выбранному выпуску
        account = self.account_model.get_by_id(account_id)
        shares_on_account = self.account_model.get_shares_on_account(account_id)
        
        available_for_issue = 0
        for share in shares_on_account:
            if share['issue_id'] == issue_id:
                available_for_issue = share['quantity']
                break
        
        if self.type_combo.currentText() == "Списание" and quantity > available_for_issue:
            QMessageBox.warning(self, "Ошибка", f"Недостаточно акций этого выпуска на счете. Доступно: {available_for_issue}")
            return
        
        data = {
            'account_id': account_id,
            'type_id': 1 if self.type_combo.currentText() == "Зачисление" else 2,
            'operation_date': self.operation_date.date().toPyDate(),
            'share_issue_id': issue_id,
            'quantity': quantity,
            'basis_document': self.basis_document.text() if self.basis_document.text() else None
        }
        
        try:
            self.model.create(data)
            
            # Обновление остатка на счете для конкретного выпуска
            if data['type_id'] == 1:  # Зачисление
                # Общий баланс счета
                new_balance = account['current_balance'] + quantity
                self.account_model.db.execute_update(
                    "UPDATE accounts SET current_balance = %s WHERE account_id = %s",
                    (new_balance, account_id)
                )
                # Добавление связи счет-акции
                self.account_model.add_shares(account_id, issue_id, quantity)
            else:  # Списание
                new_balance = account['current_balance'] - quantity
                self.account_model.db.execute_update(
                    "UPDATE accounts SET current_balance = %s WHERE account_id = %s",
                    (new_balance, account_id)
                )
                # Уменьшение количества акций на счете для конкретного выпуска
                self.account_model.db.execute_update("""
                    UPDATE account_shares 
                    SET quantity = quantity - %s 
                    WHERE account_id = %s AND issue_id = %s AND quantity >= %s
                """, (quantity, account_id, issue_id, quantity))
            
            QMessageBox.information(self, "Успех", "Операция добавлена")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")