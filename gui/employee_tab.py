# gui/employee_tab.py - ПОЛНОСТЬЮ ИСПРАВЛЕННАЯ ВЕРСИЯ
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QGroupBox, 
                             QLineEdit, QLabel, QFormLayout, QComboBox,
                             QMessageBox, QTabWidget)
from PyQt6.QtCore import Qt
from gui.dialogs import CompanyDialog
from utils.pdf_exporter import PDFExporter
from datetime import datetime
from reportlab.lib.pagesizes import A4

class EmployeeTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.company_id = parent.user_data.get('company_id', 1)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # Информация о компании
        self.company_group = QGroupBox("Информация о моем акционерном обществе")
        company_layout = QFormLayout()
        
        self.company_name_label = QLabel()
        self.company_short_label = QLabel()
        self.company_inn_label = QLabel()
        self.company_ogrn_label = QLabel()
        self.company_address_label = QLabel()
        self.company_capital_label = QLabel()
        
        company_layout.addRow("Полное наименование:", self.company_name_label)
        company_layout.addRow("Сокращенное наименование:", self.company_short_label)
        company_layout.addRow("ИНН:", self.company_inn_label)
        company_layout.addRow("ОГРН:", self.company_ogrn_label)
        company_layout.addRow("Адрес:", self.company_address_label)
        company_layout.addRow("Уставной капитал:", self.company_capital_label)
        
        self.edit_company_btn = QPushButton("Редактировать информацию")
        self.edit_company_btn.setStyleSheet("background-color: #2196F3; color: white;")
        self.edit_company_btn.clicked.connect(self.edit_company)
        company_layout.addRow("", self.edit_company_btn)
        
        self.company_group.setLayout(company_layout)
        main_layout.addWidget(self.company_group)
        
        # Вкладки
        self.tab_widget = QTabWidget()
        
        # Вкладка акций
        self.shares_tab = QWidget()
        shares_layout = QVBoxLayout()
        
        # Поиск акций
        search_group = QGroupBox("Поиск акций")
        search_layout = QHBoxLayout()
        
        self.search_type = QComboBox()
        self.search_type.addItems(["По регистрационному номеру", "По диапазону номинальной стоимости"])
        self.search_type.currentTextChanged.connect(self.on_search_type_changed)
        search_layout.addWidget(QLabel("Тип поиска:"))
        search_layout.addWidget(self.search_type)
        
        self.reg_number_input = QLineEdit()
        self.reg_number_input.setPlaceholderText("Введите регистрационный номер...")
        search_layout.addWidget(self.reg_number_input)
        
        self.nominal_range_widget = QWidget()
        range_layout = QHBoxLayout()
        self.nominal_min = QLineEdit()
        self.nominal_min.setPlaceholderText("Мин. стоимость")
        self.nominal_max = QLineEdit()
        self.nominal_max.setPlaceholderText("Макс. стоимость")
        range_layout.addWidget(self.nominal_min)
        range_layout.addWidget(self.nominal_max)
        self.nominal_range_widget.setLayout(range_layout)
        self.nominal_range_widget.setVisible(False)
        search_layout.addWidget(self.nominal_range_widget)
        
        self.search_btn = QPushButton("Поиск")
        self.search_btn.setStyleSheet("background-color: #2196F3; color: white;")
        self.search_btn.clicked.connect(self.search_shares)
        search_layout.addWidget(self.search_btn)
        
        self.clear_search_btn = QPushButton("Очистить")
        self.clear_search_btn.clicked.connect(self.clear_search)
        search_layout.addWidget(self.clear_search_btn)
        search_layout.addStretch()
        
        search_group.setLayout(search_layout)
        shares_layout.addWidget(search_group)
        
        # Таблица акций
        self.shares_table = QTableWidget()
        self.shares_table.setColumnCount(6)
        self.shares_table.setHorizontalHeaderLabels(
            ["Рег. номер", "Дата регистрации", "Тип", "Категория", "Количество", "Номинальная стоимость"]
        )
        shares_layout.addWidget(self.shares_table)
        
        self.shares_tab.setLayout(shares_layout)
        self.tab_widget.addTab(self.shares_tab, "Акции")
        
        # Вкладка отчетов
        self.reports_tab = QWidget()
        reports_layout = QVBoxLayout()
        
        # Отчет 1: Акции компании и их наличие на лицевых счетах
        report1_group = QGroupBox("Отчет: Акции компании и их наличие на лицевых счетах")
        report1_layout = QVBoxLayout()
        
        btn_layout1 = QHBoxLayout()
        self.report1_btn = QPushButton("Сформировать отчет")
        self.report1_btn.setStyleSheet("background-color: #2196F3; color: white;")
        self.report1_btn.clicked.connect(self.generate_shares_accounts_report)
        btn_layout1.addWidget(self.report1_btn)
        
        self.report1_pdf_btn = QPushButton("Сохранить в PDF")
        self.report1_pdf_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.report1_pdf_btn.clicked.connect(self.export_shares_accounts_pdf)
        btn_layout1.addWidget(self.report1_pdf_btn)
        btn_layout1.addStretch()
        
        report1_layout.addLayout(btn_layout1)
        
        self.report1_table = QTableWidget()
        self.report1_table.setColumnCount(4)
        self.report1_table.setHorizontalHeaderLabels(
            ["Рег. номер", "Тип", "Кол-во в выпуске", "На лицевых счетах"]
        )
        report1_layout.addWidget(self.report1_table)
        
        report1_group.setLayout(report1_layout)
        reports_layout.addWidget(report1_group)
        
        # Отчет 2: Акционеры, владеющие акциями компании
        report2_group = QGroupBox("Отчет: Акционеры, владеющие акциями компании")
        report2_layout = QVBoxLayout()
        
        btn_layout2 = QHBoxLayout()
        self.report2_btn = QPushButton("Сформировать отчет")
        self.report2_btn.setStyleSheet("background-color: #2196F3; color: white;")
        self.report2_btn.clicked.connect(self.generate_shareholders_report)
        btn_layout2.addWidget(self.report2_btn)
        
        self.report2_pdf_btn = QPushButton("Сохранить в PDF")
        self.report2_pdf_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.report2_pdf_btn.clicked.connect(self.export_shareholders_pdf)
        btn_layout2.addWidget(self.report2_pdf_btn)
        btn_layout2.addStretch()
        
        report2_layout.addLayout(btn_layout2)
        
        self.report2_table = QTableWidget()
        self.report2_table.setColumnCount(4)
        self.report2_table.setHorizontalHeaderLabels(
            ["Акционер", "Тип", "ИНН", "Кол-во акций"]
        )
        report2_layout.addWidget(self.report2_table)
        
        report2_group.setLayout(report2_layout)
        reports_layout.addWidget(report2_group)
        
        self.reports_tab.setLayout(reports_layout)
        self.tab_widget.addTab(self.reports_tab, "Отчеты")
        
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)
    
    def on_search_type_changed(self, search_type):
        is_range = search_type == "По диапазону номинальной стоимости"
        self.reg_number_input.setVisible(not is_range)
        self.nominal_range_widget.setVisible(is_range)
    
    def load_data(self):
        # Загрузка информации о компании
        company = self.parent.company_model.get_by_id(self.company_id)
        if company:
            self.company_name_label.setText(company['full_name'])
            self.company_short_label.setText(company['short_name'])
            self.company_inn_label.setText(company['inn'])
            self.company_ogrn_label.setText(company['ogrn'])
            self.company_address_label.setText(company['address'])
            self.company_capital_label.setText(f"{company['authorized_capital']:,.2f} руб.")
        
        # Загрузка акций компании
        self.load_company_shares()
    
    def load_company_shares(self):
        issues = self.parent.share_issue_model.get_by_company(self.company_id)
        self.shares_table.setRowCount(len(issues))
        for i, issue in enumerate(issues):
            self.shares_table.setItem(i, 0, QTableWidgetItem(issue['registration_number']))
            self.shares_table.setItem(i, 1, QTableWidgetItem(str(issue['registration_date'])))
            self.shares_table.setItem(i, 2, QTableWidgetItem(issue['share_type']))
            self.shares_table.setItem(i, 3, QTableWidgetItem(issue.get('category_series', '-')))
            self.shares_table.setItem(i, 4, QTableWidgetItem(str(issue['quantity'])))
            self.shares_table.setItem(i, 5, QTableWidgetItem(f"{issue['nominal_value']:,.2f}"))
        self.shares_table.resizeColumnsToContents()
    
    def search_shares(self):
        search_type = self.search_type.currentText()
        
        if search_type == "По регистрационному номеру":
            reg_number = self.reg_number_input.text().strip()
            if reg_number:
                issue = self.parent.share_issue_model.get_by_registration_number(reg_number)
                if issue and issue['company_id'] == self.company_id:
                    self.shares_table.setRowCount(1)
                    self.shares_table.setItem(0, 0, QTableWidgetItem(issue['registration_number']))
                    self.shares_table.setItem(0, 1, QTableWidgetItem(str(issue['registration_date'])))
                    self.shares_table.setItem(0, 2, QTableWidgetItem(issue['share_type']))
                    self.shares_table.setItem(0, 3, QTableWidgetItem(issue.get('category_series', '-')))
                    self.shares_table.setItem(0, 4, QTableWidgetItem(str(issue['quantity'])))
                    self.shares_table.setItem(0, 5, QTableWidgetItem(f"{issue['nominal_value']:,.2f}"))
                else:
                    self.shares_table.setRowCount(0)
                    QMessageBox.information(self, "Результат", "Акция не найдена")
        
        elif search_type == "По диапазону номинальной стоимости":
            try:
                min_val = float(self.nominal_min.text()) if self.nominal_min.text() else 0
                max_val = float(self.nominal_max.text()) if self.nominal_max.text() else float('inf')
                
                issues = self.parent.share_issue_model.get_by_nominal_range(min_val, max_val)
                issues = [i for i in issues if i['company_id'] == self.company_id]
                
                self.shares_table.setRowCount(len(issues))
                for i, issue in enumerate(issues):
                    self.shares_table.setItem(i, 0, QTableWidgetItem(issue['registration_number']))
                    self.shares_table.setItem(i, 1, QTableWidgetItem(str(issue['registration_date'])))
                    self.shares_table.setItem(i, 2, QTableWidgetItem(issue['share_type']))
                    self.shares_table.setItem(i, 3, QTableWidgetItem(issue.get('category_series', '-')))
                    self.shares_table.setItem(i, 4, QTableWidgetItem(str(issue['quantity'])))
                    self.shares_table.setItem(i, 5, QTableWidgetItem(f"{issue['nominal_value']:,.2f}"))
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Введите корректные значения стоимости")
    
    def clear_search(self):
        self.reg_number_input.clear()
        self.nominal_min.clear()
        self.nominal_max.clear()
        self.load_company_shares()
    
    def edit_company(self):
        company = self.parent.company_model.get_by_id(self.company_id)
        if company:
            dialog = CompanyDialog(self, self.parent.company_model, company)
            if dialog.exec():
                self.load_data()
    
    def generate_shares_accounts_report(self):
        """Отчет об акциях компании и на каких лицевых счетах они есть"""
        query = """
            SELECT 
                si.registration_number,
                si.share_type,
                si.quantity as total_quantity,
                COALESCE(SUM(acs.quantity), 0) as on_accounts
            FROM share_issues si
            LEFT JOIN account_shares acs ON si.issue_id = acs.issue_id
            WHERE si.company_id = %s
            GROUP BY si.issue_id, si.registration_number, si.share_type, si.quantity
            ORDER BY si.issue_id
        """
        results = self.parent.db.execute_query(query, (self.company_id,))
        
        self.report1_table.setRowCount(len(results))
        for i, row in enumerate(results):
            self.report1_table.setItem(i, 0, QTableWidgetItem(row['registration_number']))
            self.report1_table.setItem(i, 1, QTableWidgetItem(row['share_type']))
            self.report1_table.setItem(i, 2, QTableWidgetItem(str(row['total_quantity'])))
            self.report1_table.setItem(i, 3, QTableWidgetItem(str(row['on_accounts'])))
        
        self.report1_table.resizeColumnsToContents()
    
    def generate_shareholders_report(self):
        """Отчет об акционерах, владеющих акциями компании"""
        query = """
            SELECT DISTINCT
                s.name,
                s.type,
                s.inn,
                SUM(acs.quantity) as total_shares
            FROM shareholders s
            JOIN accounts a ON s.shareholder_id = a.shareholder_id
            JOIN account_shares acs ON a.account_id = acs.account_id
            JOIN share_issues si ON acs.issue_id = si.issue_id
            WHERE si.company_id = %s
            GROUP BY s.shareholder_id, s.name, s.type, s.inn
            ORDER BY total_shares DESC
        """
        results = self.parent.db.execute_query(query, (self.company_id,))
        
        self.report2_table.setRowCount(len(results))
        for i, row in enumerate(results):
            self.report2_table.setItem(i, 0, QTableWidgetItem(row['name']))
            self.report2_table.setItem(i, 1, QTableWidgetItem('Физическое' if row['type'] == 'individual' else 'Юридическое'))
            self.report2_table.setItem(i, 2, QTableWidgetItem(row.get('inn', '-')))
            self.report2_table.setItem(i, 3, QTableWidgetItem(str(row['total_shares'])))
        
        self.report2_table.resizeColumnsToContents()
    
    def export_shares_accounts_pdf(self):
        """Экспорт отчета об акциях компании в PDF с диаграммами"""
        query = """
            SELECT 
                si.registration_number,
                si.share_type,
                si.quantity as total_quantity,
                COALESCE(SUM(acs.quantity), 0) as on_accounts
            FROM share_issues si
            LEFT JOIN account_shares acs ON si.issue_id = acs.issue_id
            WHERE si.company_id = %s
            GROUP BY si.issue_id, si.registration_number, si.share_type, si.quantity
            ORDER BY si.issue_id
        """
        results = self.parent.db.execute_query(query, (self.company_id,))
        
        if results:
            company = self.parent.company_model.get_by_id(self.company_id)
            pdf_exporter = PDFExporter(self)
            file_path = pdf_exporter.get_save_filename(self, f"company_shares_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            if file_path:
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.enums import TA_CENTER, TA_LEFT
                from reportlab.lib import colors
                from reportlab.graphics.shapes import Drawing
                from reportlab.graphics.charts.barcharts import VerticalBarChart
                from reportlab.graphics.charts.piecharts import Pie
                
                doc = SimpleDocTemplate(file_path, pagesize=A4,
                                       topMargin=20, bottomMargin=20,
                                       leftMargin=20, rightMargin=20)
                elements = []
                
                # Стили
                styles = getSampleStyleSheet()
                font_name = pdf_exporter.get_font_name()
                
                title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                    fontName=font_name, fontSize=16, alignment=TA_CENTER, spaceAfter=12,
                    textColor=colors.HexColor('#1a237e'))
                
                normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'],
                    fontName=font_name, fontSize=9)
                
                # Заголовок
                elements.append(Paragraph("Отчет об акциях компании", title_style))
                if company:
                    elements.append(Paragraph(company.get('full_name', ''), normal_style))
                elements.append(Spacer(1, 20))
                
                # Таблица
                headers = ["Регистрационный номер", "Тип", "Кол-во в выпуске", "На лицевых счетах"]
                table_data = []
                quantities = []
                reg_numbers = []
                on_accounts_list = []
                
                for row in results:
                    reg_num = row['registration_number']
                    qty = float(row['total_quantity']) if row['total_quantity'] else 0
                    on_acc = float(row['on_accounts']) if row['on_accounts'] else 0
                    quantities.append(qty)
                    on_accounts_list.append(on_acc)
                    reg_numbers.append(reg_num[-8:] if len(reg_num) > 8 else reg_num)
                    table_data.append([
                        reg_num,
                        row['share_type'],
                        f"{int(qty):,}" if qty == int(qty) else f"{qty:,}",
                        f"{int(on_acc):,}" if on_acc == int(on_acc) else f"{on_acc:,}"
                    ])
                
                # Создание таблицы
                t = pdf_exporter.create_table(table_data, headers)
                elements.extend(t)
                
                # Столбчатая диаграмма
                if quantities:
                    elements.append(Spacer(1, 20))
                    drawing = Drawing(400, 200)
                    bc = VerticalBarChart()
                    bc.x = 50
                    bc.y = 50
                    bc.width = 300
                    bc.height = 120
                    bc.data = [quantities[:10]]
                    bc.categoryAxis.categoryNames = reg_numbers[:10]
                    bc.categoryAxis.labels.angle = 45
                    bc.categoryAxis.labels.fontSize = 8
                    bc.categoryAxis.labels.fontName = font_name
                    bc.valueAxis.valueMin = 0
                    bc.valueAxis.valueMax = max(quantities) * 1.2 if quantities else 10
                    bc.bars[0].fillColor = colors.HexColor('#1a237e')
                    drawing.add(bc)
                    elements.append(Paragraph("Диаграмма количества акций по выпускам", normal_style))
                    elements.append(Spacer(1, 5))
                    elements.append(drawing)
                
                # Круговая диаграмма по типам акций
                type_quantities = {}
                for row in results:
                    stype = row['share_type']
                    qty = float(row['total_quantity']) if row['total_quantity'] else 0
                    type_quantities[stype] = type_quantities.get(stype, 0) + qty
                
                if type_quantities:
                    elements.append(Spacer(1, 20))
                    drawing2 = Drawing(400, 250)
                    pie = Pie()
                    pie.x = 150
                    pie.y = 70
                    pie.width = 150
                    pie.height = 150
                    pie.data = list(type_quantities.values())
                    pie.labels = list(type_quantities.keys())
                    pie.sideLabels = True
                    pie.slices.strokeWidth = 0.5
                    
                    colors_list = [colors.HexColor('#1a237e'), colors.HexColor('#4caf50')]
                    for i, color in enumerate(colors_list):
                        if i < len(pie.slices):
                            pie.slices[i].fillColor = color
                            pie.slices[i].fontName = font_name
                    
                    drawing2.add(pie)
                    elements.append(Paragraph("Распределение акций по типам", normal_style))
                    elements.append(Spacer(1, 5))
                    elements.append(drawing2)
                
                # Итоги
                total_qty = sum(quantities)
                total_on_acc = sum(on_accounts_list)
                elements.append(Spacer(1, 10))
                elements.append(Paragraph(f"<b>Всего выпусков: {len(results)}</b>", normal_style))
                elements.append(Paragraph(f"<b>Общее количество акций: {int(total_qty):,}</b>", normal_style))
                elements.append(Paragraph(f"<b>Акций на лицевых счетах: {int(total_on_acc):,}</b>", normal_style))
                elements.append(Paragraph(f"<b>Процент размещения: {(total_on_acc/total_qty*100):.1f}%</b>" if total_qty > 0 else "<b>Процент размещения: 0%</b>", normal_style))
                
                doc.build(elements)
                QMessageBox.information(self, "Успех", f"Отчет сохранен в файл:\n{file_path}")
        else:
            QMessageBox.information(self, "Результат", "Нет данных для отчета")
    
    def export_shareholders_pdf(self):
        """Экспорт отчета об акционерах компании в PDF с диаграммами"""
        query = """
            SELECT DISTINCT
                s.name,
                s.type,
                s.inn,
                SUM(acs.quantity) as total_shares
            FROM shareholders s
            JOIN accounts a ON s.shareholder_id = a.shareholder_id
            JOIN account_shares acs ON a.account_id = acs.account_id
            JOIN share_issues si ON acs.issue_id = si.issue_id
            WHERE si.company_id = %s
            GROUP BY s.shareholder_id, s.name, s.type, s.inn
            ORDER BY total_shares DESC
        """
        results = self.parent.db.execute_query(query, (self.company_id,))
        
        if results:
            company = self.parent.company_model.get_by_id(self.company_id)
            pdf_exporter = PDFExporter(self)
            file_path = pdf_exporter.get_save_filename(self, f"company_shareholders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            if file_path:
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.enums import TA_CENTER, TA_LEFT
                from reportlab.lib import colors
                from reportlab.graphics.shapes import Drawing
                from reportlab.graphics.charts.barcharts import VerticalBarChart
                from reportlab.graphics.charts.piecharts import Pie
                
                doc = SimpleDocTemplate(file_path, pagesize=A4,
                                       topMargin=20, bottomMargin=20,
                                       leftMargin=20, rightMargin=20)
                elements = []
                
                # Стили
                styles = getSampleStyleSheet()
                font_name = pdf_exporter.get_font_name()
                
                title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                    fontName=font_name, fontSize=16, alignment=TA_CENTER, spaceAfter=12,
                    textColor=colors.HexColor('#1a237e'))
                
                normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'],
                    fontName=font_name, fontSize=9)
                
                # Заголовок
                elements.append(Paragraph("Отчет об акционерах компании", title_style))
                if company:
                    elements.append(Paragraph(company.get('full_name', ''), normal_style))
                elements.append(Spacer(1, 20))
                
                # Таблица
                headers = ["Акционер", "Тип", "ИНН", "Кол-во акций"]
                table_data = []
                quantities = []
                names = []
                
                for row in results:
                    qty = float(row['total_shares']) if row['total_shares'] else 0
                    quantities.append(qty)
                    names.append(row['name'][:20] if len(row['name']) > 20 else row['name'])
                    table_data.append([
                        row['name'],
                        'Физическое' if row['type'] == 'individual' else 'Юридическое',
                        row.get('inn', '-'),
                        f"{int(qty):,}" if qty == int(qty) else f"{qty:,}"
                    ])
                
                t = pdf_exporter.create_table(table_data, headers)
                elements.extend(t)
                
                # Столбчатая диаграмма (топ-10)
                if quantities:
                    elements.append(Spacer(1, 20))
                    drawing = Drawing(400, 200)
                    bc = VerticalBarChart()
                    bc.x = 50
                    bc.y = 50
                    bc.width = 300
                    bc.height = 120
                    bc.data = [quantities[:10]]
                    bc.categoryAxis.categoryNames = names[:10]
                    bc.categoryAxis.labels.angle = 45
                    bc.categoryAxis.labels.fontSize = 7
                    bc.categoryAxis.labels.fontName = font_name
                    bc.valueAxis.valueMin = 0
                    bc.valueAxis.valueMax = max(quantities) * 1.2 if quantities else 10
                    bc.bars[0].fillColor = colors.HexColor('#1a237e')
                    drawing.add(bc)
                    elements.append(Paragraph("Топ-10 акционеров по количеству акций", normal_style))
                    elements.append(Spacer(1, 5))
                    elements.append(drawing)
                
                # Круговая диаграмма по типам акционеров
                type_counts = {'Физические лица': 0, 'Юридические лица': 0}
                for row in results:
                    qty = float(row['total_shares']) if row['total_shares'] else 0
                    if row['type'] == 'individual':
                        type_counts['Физические лица'] += qty
                    else:
                        type_counts['Юридические лица'] += qty
                
                if type_counts and (type_counts['Физические лица'] > 0 or type_counts['Юридические лица'] > 0):
                    elements.append(Spacer(1, 20))
                    drawing2 = Drawing(400, 250)
                    pie = Pie()
                    pie.x = 150
                    pie.y = 70
                    pie.width = 150
                    pie.height = 150
                    pie.data = list(type_counts.values())
                    pie.labels = list(type_counts.keys())
                    pie.sideLabels = True
                    pie.slices.strokeWidth = 0.5
                    
                    colors_list = [colors.HexColor('#1a237e'), colors.HexColor('#4caf50')]
                    for i, color in enumerate(colors_list):
                        if i < len(pie.slices):
                            pie.slices[i].fillColor = color
                            pie.slices[i].fontName = font_name
                    
                    drawing2.add(pie)
                    elements.append(Paragraph("Распределение акций по типам акционеров", normal_style))
                    elements.append(Spacer(1, 5))
                    elements.append(drawing2)
                
                # Итоги
                total_shares = sum(quantities)
                elements.append(Spacer(1, 10))
                elements.append(Paragraph(f"<b>Всего акционеров: {len(results)}</b>", normal_style))
                elements.append(Paragraph(f"<b>Общее количество акций: {int(total_shares):,}</b>", normal_style))
                
                doc.build(elements)
                QMessageBox.information(self, "Успех", f"Отчет сохранен в файл:\n{file_path}")
        else:
            QMessageBox.information(self, "Результат", "Нет данных для отчета")
    
    def refresh(self):
        self.load_data()