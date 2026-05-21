# utils/pdf_exporter.py - ПОЛНОСТЬЮ ИСПРАВЛЕННАЯ ВЕРСИЯ
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph, 
                                Spacer, PageBreak, Image, KeepTogether)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend
from datetime import datetime
from PyQt6.QtWidgets import QFileDialog, QMessageBox
import os

class PDFExporter:
    """Класс для экспорта отчетов в PDF с поддержкой кириллицы и диаграмм"""
    
    _fonts_registered = False
    
    @classmethod
    def register_fonts(cls):
        """Регистрация шрифтов для поддержки кириллицы"""
        if cls._fonts_registered:
            return
        
        # Список возможных путей к шрифтам на разных ОС
        possible_fonts = [
            # Linux
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
            '/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf',
            '/usr/share/fonts/truetype/freefont/FreeSans.ttf',
            '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf',
            '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf',
            # Windows
            'C:/Windows/Fonts/arial.ttf',
            'C:/Windows/Fonts/ariali.ttf',
            'C:/Windows/Fonts/times.ttf',
            'C:/Windows/Fonts/calibri.ttf',
            # macOS
            '/System/Library/Fonts/Helvetica.ttc',
            '/System/Library/Fonts/Arial.ttf',
            '/Library/Fonts/Arial.ttf',
        ]
        
        font_registered = False
        for font_path in possible_fonts:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('RussianFont', font_path))
                    font_registered = True
                    print(f"Зарегистрирован шрифт: {font_path}")
                    break
                except Exception as e:
                    continue
        
        # Если не нашли подходящий шрифт, используем стандартный
        if not font_registered:
            print("Не найден подходящий шрифт, используются стандартные шрифты")
        
        cls._fonts_registered = True
    
    def __init__(self, parent=None):
        self.parent = parent
        self.register_fonts()
    
    @staticmethod
    def get_save_filename(parent, default_name="report.pdf"):
        file_path, _ = QFileDialog.getSaveFileName(
            parent, "Сохранить отчет", default_name, "PDF Files (*.pdf);;All Files (*)"
        )
        return file_path
    
    @staticmethod
    def convert_to_float(value):
        """Преобразование Decimal в float для безопасных вычислений"""
        if hasattr(value, '__float__'):
            return float(value)
        return value if value is not None else 0
    
    def get_font_name(self):
        """Получение имени шрифта для кириллицы"""
        try:
            return 'RussianFont' if 'RussianFont' in pdfmetrics._fonts else 'Helvetica'
        except:
            return 'Helvetica'
    
    def get_styles(self):
        """Получение стилей с поддержкой кириллицы"""
        styles = getSampleStyleSheet()
        font_name = self.get_font_name()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=font_name,
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=12,
            textColor=colors.HexColor('#1a237e')
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=colors.HexColor('#546e7a')
        )
        
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=8,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#78909c')
        )
        
        table_title_style = ParagraphStyle(
            'TableTitle',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=12,
            alignment=TA_LEFT,
            spaceAfter=6
        )
        
        normal_style = ParagraphStyle(
            'NormalStyle',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=9
        )
        
        heading_style = ParagraphStyle(
            'HeadingStyle',
            parent=styles['Heading2'],
            fontName=font_name,
            fontSize=14,
            spaceAfter=10,
            textColor=colors.HexColor('#1a237e')
        )
        
        return {
            'title': title_style,
            'subtitle': subtitle_style,
            'date': date_style,
            'table_title': table_title_style,
            'normal': normal_style,
            'heading': heading_style
        }
    
    def create_header(self, title, subtitle=None):
        """Создание заголовка отчета"""
        styles = self.get_styles()
        elements = []
        elements.append(Paragraph(title, styles['title']))
        if subtitle:
            elements.append(Paragraph(subtitle, styles['subtitle']))
        current_date = datetime.now().strftime("%d.%m.%Y %H:%M")
        elements.append(Paragraph(f"Дата формирования: {current_date}", styles['date']))
        elements.append(Spacer(1, 10))
        return elements
    
    def create_table(self, data, headers, title=None):
        """Создание таблицы с данными с поддержкой кириллицы"""
        styles = self.get_styles()
        font_name = self.get_font_name()
        elements = []
        
        if title:
            elements.append(Paragraph(title, styles['table_title']))
        
        table_data = []
        
        # Заголовки
        header_row = []
        for header in headers:
            header_row.append(Paragraph(f"<b>{header}</b>", styles['table_title']))
        table_data.append(header_row)
        
        # Данные
        for row in data:
            formatted_row = []
            for cell in row:
                cell_str = str(cell) if cell is not None else '-'
                cell_str = cell_str.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                formatted_row.append(Paragraph(cell_str, styles['normal']))
            table_data.append(formatted_row)
        
        # Автоматическая ширина колонок
        if len(headers) <= 4:
            col_widths = [120, 80, 100, 100]
        elif len(headers) <= 6:
            col_widths = [100, 80, 80, 80, 80, 80]
        else:
            col_widths = [80] * len(headers)
        
        table = Table(table_data, repeatRows=1, colWidths=col_widths)
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 1), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ])
        table.setStyle(table_style)
        elements.append(table)
        elements.append(Spacer(1, 10))
        return elements
    
    def create_bar_chart(self, data, labels, title, width=400, height=200):
        """Создание столбчатой диаграммы"""
        # Преобразуем данные в float
        data = [float(self.convert_to_float(x)) for x in data]
        
        # Получаем имя шрифта
        font_name = self.get_font_name()
        
        drawing = Drawing(width, height)
        
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 50
        bc.width = width - 100
        bc.height = height - 80
        bc.data = [data]
        bc.categoryAxis.categoryNames = labels
        bc.categoryAxis.labels.angle = 45
        bc.categoryAxis.labels.fontSize = 8
        bc.categoryAxis.labels.fontName = font_name
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = max(data) * 1.2 if data else 10
        bc.bars[0].fillColor = colors.HexColor('#1a237e')
        
        drawing.add(bc)
        
        styles = self.get_styles()
        title_para = Paragraph(title, styles['normal'])
        
        return [title_para, Spacer(1, 5), drawing]
    
    def create_pie_chart(self, data, labels, title, width=400, height=250):
        """Создание круговой диаграммы с поддержкой кириллицы"""
        # Преобразуем данные в float
        data = [float(self.convert_to_float(x)) for x in data]
        
        # Получаем имя шрифта
        font_name = self.get_font_name()
        
        drawing = Drawing(width, height)
        
        pie = Pie()
        pie.x = 150
        pie.y = 65
        pie.width = 150
        pie.height = 150
        pie.data = data
        pie.labels = labels
        pie.sideLabels = True
        pie.slices.strokeWidth = 0.5
        
        # Устанавливаем шрифт для меток секторов
        for i in range(len(pie.slices)):
            pie.slices[i].fontName = font_name
            pie.slices[i].fontSize = 8
        
        # Настройка меток сбоку
        pie.sideLabels = True
        pie.sideLabelsOffset = 10
        
        # Цвета для секторов
        colors_list = [colors.HexColor('#1a237e'), colors.HexColor('#4caf50'), 
                       colors.HexColor('#ff9800'), colors.HexColor('#f44336'),
                       colors.HexColor('#9c27b0'), colors.HexColor('#00bcd4'),
                       colors.HexColor('#795548'), colors.HexColor('#607d8b')]
        for i, color in enumerate(colors_list):
            if i < len(pie.slices):
                pie.slices[i].fillColor = color
        
        drawing.add(pie)
        
        # Добавляем легенду для лучшего отображения
        if len(labels) <= 8:
            legend = Legend()
            legend.alignment = 'right'
            legend.x = width - 60
            legend.y = height - 80
            legend.colorNamePairs = [(pie.slices[i].fillColor, labels[i]) for i in range(len(labels))]
            legend.fontName = font_name
            legend.fontSize = 8
            drawing.add(legend)
        
        styles = self.get_styles()
        title_para = Paragraph(title, styles['normal'])
        
        return [title_para, Spacer(1, 5), drawing]
    
    def export_companies_report(self, companies_data, city=None):
        """Экспорт отчета об акционерных обществах"""
        file_path = self.get_save_filename(self.parent, f"companies_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        if not file_path:
            return False
        
        try:
            doc = SimpleDocTemplate(file_path, pagesize=A4, 
                                   topMargin=20*mm, bottomMargin=20*mm,
                                   leftMargin=15*mm, rightMargin=15*mm)
            elements = []
            
            title = "Отчет об акционерных обществах"
            subtitle = f"По городу: {city}" if city else "Все акционерные общества"
            elements.extend(self.create_header(title, subtitle))
            
            headers = ["Наименование", "Сокращенное", "ИНН", "ОГРН", "Уставной капитал", "Адрес"]
            table_data = []
            capitals = []
            names = []
            
            for company in companies_data:
                capital = self.convert_to_float(company.get('authorized_capital', 0))
                capitals.append(capital)
                names.append(company.get('short_name', '')[:20])
                table_data.append([
                    company.get('full_name', '-'),
                    company.get('short_name', '-'),
                    company.get('inn', '-'),
                    company.get('ogrn', '-'),
                    f"{capital:,.2f} руб.",
                    company.get('address', '-')
                ])
            
            elements.extend(self.create_table(table_data, headers, "Список акционерных обществ"))
            
            # Диаграмма
            if capitals and any(c > 0 for c in capitals):
                elements.append(Spacer(1, 10))
                chart_elements = self.create_bar_chart(
                    capitals[:10], names[:10], 
                    "Диаграмма уставных капиталов (топ-10)"
                )
                elements.extend(chart_elements)
            
            styles = self.get_styles()
            total_capital = sum(capitals)
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"<b>Всего компаний: {len(companies_data)}</b>", styles['normal']))
            elements.append(Paragraph(f"<b>Общий уставной капитал: {total_capital:,.2f} руб.</b>", styles['normal']))
            
            doc.build(elements)
            QMessageBox.information(self.parent, "Успех", f"Отчет сохранен в файл:\n{file_path}")
            return True
            
        except Exception as e:
            QMessageBox.critical(self.parent, "Ошибка", f"Ошибка при создании PDF: {str(e)}")
            return False
    
    def export_shareholders_report(self, shareholders_data, status=None):
        """Экспорт отчета об акционерах"""
        file_path = self.get_save_filename(self.parent, f"shareholders_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        if not file_path:
            return False
        
        try:
            doc = SimpleDocTemplate(file_path, pagesize=landscape(A4),
                                   topMargin=20*mm, bottomMargin=20*mm,
                                   leftMargin=15*mm, rightMargin=15*mm)
            elements = []
            
            title = "Отчет об акционерах"
            subtitle = f"Статус: {status}" if status else "Все акционеры"
            elements.extend(self.create_header(title, subtitle))
            
            headers = ["Тип", "Наименование", "ИНН", "Паспорт/ОГРН", "Адрес", "Статус"]
            table_data = []
            type_counts = {'individual': 0, 'legal': 0}
            
            for sh in shareholders_data:
                passport = sh.get('passport_data', '') or sh.get('ogrn', '-')
                sh_type = sh.get('type', 'individual')
                type_counts[sh_type] = type_counts.get(sh_type, 0) + 1
                table_data.append([
                    'Физическое лицо' if sh_type == 'individual' else 'Юридическое лицо',
                    sh.get('name', '-'),
                    sh.get('inn', '-'),
                    passport,
                    sh.get('address', '-'),
                    sh.get('status', '-')
                ])
            
            elements.extend(self.create_table(table_data, headers, "Список акционеров"))
            
            # Диаграмма типов акционеров
            if type_counts:
                elements.append(Spacer(1, 10))
                pie_elements = self.create_pie_chart(
                    [type_counts.get('individual', 0), type_counts.get('legal', 0)],
                    ['Физические лица', 'Юридические лица'],
                    "Распределение акционеров по типам", width=400, height=250
                )
                elements.extend(pie_elements)
            
            styles = self.get_styles()
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"<b>Всего акционеров: {len(shareholders_data)}</b>", styles['normal']))
            
            doc.build(elements)
            QMessageBox.information(self.parent, "Успех", f"Отчет сохранен в файл:\n{file_path}")
            return True
            
        except Exception as e:
            QMessageBox.critical(self.parent, "Ошибка", f"Ошибка при создании PDF: {str(e)}")
            return False
    
    def export_company_details_report(self, company_data, shares_data):
        """Отчет об отдельном АО с выпусками акций"""
        file_path = self.get_save_filename(self.parent, 
            f"company_{company_data.get('short_name', 'report')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        if not file_path:
            return False
        
        try:
            doc = SimpleDocTemplate(file_path, pagesize=A4,
                                   topMargin=20*mm, bottomMargin=20*mm,
                                   leftMargin=15*mm, rightMargin=15*mm)
            elements = []
            
            title = "Отчет об акционерном обществе"
            subtitle = company_data.get('full_name', '')
            elements.extend(self.create_header(title, subtitle))
            
            styles = self.get_styles()
            
            # Информация об АО
            elements.append(Paragraph("<b>Основная информация:</b>", styles['heading']))
            elements.append(Spacer(1, 5))
            
            authorized_capital = self.convert_to_float(company_data.get('authorized_capital', 0))
            
            info_data = [
                ["Полное наименование:", company_data.get('full_name', '-')],
                ["Сокращенное наименование:", company_data.get('short_name', '-')],
                ["ИНН:", company_data.get('inn', '-')],
                ["ОГРН:", company_data.get('ogrn', '-')],
                ["Адрес:", company_data.get('address', '-')],
                ["Уставной капитал:", f"{authorized_capital:,.2f} руб."],
                ["Город:", company_data.get('city', '-')],
            ]
            
            info_table = Table(info_data, colWidths=[120, 350])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), self.get_font_name()),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(info_table)
            elements.append(Spacer(1, 15))
            
            # Выпуски акций
            if shares_data:
                elements.append(Paragraph("<b>Выпуски акций:</b>", styles['heading']))
                elements.append(Spacer(1, 5))
                
                headers = ["Рег. номер", "Дата", "Тип", "Категория", "Количество", "Номинал", "Статус"]
                table_data = []
                quantities = []
                reg_numbers = []
                type_quantities = {}
                
                for share in shares_data:
                    qty = self.convert_to_float(share.get('quantity', 0))
                    nominal = self.convert_to_float(share.get('nominal_value', 0))
                    share_type = share.get('share_type', 'unknown')
                    quantities.append(qty)
                    reg_numbers.append(share.get('registration_number', '')[-8:])
                    type_quantities[share_type] = type_quantities.get(share_type, 0) + qty
                    table_data.append([
                        share.get('registration_number', '-'),
                        str(share.get('registration_date', '-')),
                        share_type,
                        share.get('category_series', '-'),
                        f"{int(qty):,}" if qty == int(qty) else f"{qty:,}",
                        f"{nominal:,.2f} руб.",
                        share.get('status', '-')
                    ])
                
                elements.extend(self.create_table(table_data, headers))
                
                # Диаграммы
                if quantities and reg_numbers:
                    elements.append(Spacer(1, 10))
                    chart_elements = self.create_bar_chart(
                        quantities[:10], reg_numbers[:10], 
                        "Диаграмма количества акций по выпускам"
                    )
                    elements.extend(chart_elements)
                
                # Круговая диаграмма по типам акций
                if type_quantities:
                    elements.append(Spacer(1, 15))
                    pie_elements = self.create_pie_chart(
                        list(type_quantities.values()), list(type_quantities.keys()),
                        "Распределение акций по типам", width=400, height=250
                    )
                    elements.extend(pie_elements)
                
                total_shares = sum(quantities)
                elements.append(Spacer(1, 10))
                elements.append(Paragraph(f"<b>Всего выпусков: {len(shares_data)}</b>", styles['normal']))
                elements.append(Paragraph(f"<b>Общее количество акций: {int(total_shares):,}</b>", styles['normal']))
            else:
                elements.append(Paragraph("<i>Нет выпусков акций</i>", styles['normal']))
            
            doc.build(elements)
            QMessageBox.information(self.parent, "Успех", f"Отчет сохранен в файл:\n{file_path}")
            return True
            
        except Exception as e:
            QMessageBox.critical(self.parent, "Ошибка", f"Ошибка при создании PDF: {str(e)}")
            return False
    
    def export_accounts_report(self, accounts_data, shareholder_name=None):
        """Экспорт отчета о лицевых счетах акционера"""
        file_path = self.get_save_filename(self.parent, f"accounts_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        if not file_path:
            return False
        
        try:
            doc = SimpleDocTemplate(file_path, pagesize=landscape(A4),
                                   topMargin=20*mm, bottomMargin=20*mm,
                                   leftMargin=15*mm, rightMargin=15*mm)
            elements = []
            
            title = "Отчет о лицевых счетах"
            subtitle = f"Акционер: {shareholder_name}" if shareholder_name else "Все лицевые счета"
            elements.extend(self.create_header(title, subtitle))
            
            headers = ["Акционер", "Номер счета", "Дата открытия", "Дата закрытия", "Остаток акций", "Статус"]
            table_data = []
            balances = []
            account_numbers = []
            
            for acc in accounts_data:
                balance = self.convert_to_float(acc.get('current_balance', 0))
                balances.append(balance)
                account_numbers.append(acc.get('account_number', ''))
                table_data.append([
                    acc.get('shareholder_name', '-'),
                    acc.get('account_number', '-'),
                    str(acc.get('open_date', '-')),
                    str(acc.get('close_date', '-')) if acc.get('close_date') else 'Активен',
                    f"{int(balance):,}" if balance == int(balance) else f"{balance:,}",
                    acc.get('status', '-')
                ])
            
            elements.extend(self.create_table(table_data, headers, "Список лицевых счетов"))
            
            # Диаграмма распределения акций
            if balances and any(b > 0 for b in balances):
                elements.append(Spacer(1, 10))
                chart_elements = self.create_bar_chart(
                    balances, account_numbers, 
                    "Диаграмма распределения акций по лицевым счетам"
                )
                elements.extend(chart_elements)
            
            styles = self.get_styles()
            total_shares = sum(balances)
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"<b>Всего счетов: {len(accounts_data)}</b>", styles['normal']))
            elements.append(Paragraph(f"<b>Общее количество акций: {int(total_shares):,}</b>", styles['normal']))
            
            doc.build(elements)
            QMessageBox.information(self.parent, "Успех", f"Отчет сохранен в файл:\n{file_path}")
            return True
            
        except Exception as e:
            QMessageBox.critical(self.parent, "Ошибка", f"Ошибка при создании PDF: {str(e)}")
            return False
    
    def export_operations_report(self, operations_data, account_number=None):
        """Экспорт отчета об операциях по лицевому счету"""
        file_path = self.get_save_filename(self.parent, f"operations_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        if not file_path:
            return False
        
        try:
            doc = SimpleDocTemplate(file_path, pagesize=landscape(A4),
                                   topMargin=20*mm, bottomMargin=20*mm,
                                   leftMargin=15*mm, rightMargin=15*mm)
            elements = []
            
            title = "Отчет об операциях"
            subtitle = f"Лицевой счет: {account_number}" if account_number else "Все операции"
            elements.extend(self.create_header(title, subtitle))
            
            headers = ["Дата", "Тип операции", "Компания", "Количество акций", "Основание"]
            table_data = []
            quantities = []
            
            for op in operations_data:
                qty = self.convert_to_float(op.get('quantity', 0))
                quantities.append(qty)
                table_data.append([
                    str(op.get('operation_date', '-')),
                    op.get('operation_type', '-'),
                    op.get('company_name', '-'),
                    f"{int(qty):,}" if qty == int(qty) else f"{qty:,}",
                    op.get('basis_document', '-') or '-'
                ])
            
            elements.extend(self.create_table(table_data, headers, "Список операций"))
            
            # Диаграмма по операциям
            if quantities:
                elements.append(Spacer(1, 10))
                # Считаем зачисления и списания
                credited = sum(op.get('quantity', 0) for op in operations_data if op.get('operation_type') == 'Зачисление')
                debited = sum(op.get('quantity', 0) for op in operations_data if op.get('operation_type') == 'Списание')
                
                if credited > 0 or debited > 0:
                    chart_elements = self.create_pie_chart(
                        [credited, debited],
                        ['Зачислено', 'Списано'],
                        "Соотношение зачислений и списаний", width=400, height=250
                    )
                    elements.extend(chart_elements)
            
            styles = self.get_styles()
            total_credited = sum(op.get('quantity', 0) for op in operations_data if op.get('operation_type') == 'Зачисление')
            total_debited = sum(op.get('quantity', 0) for op in operations_data if op.get('operation_type') == 'Списание')
            
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"<b>Всего операций: {len(operations_data)}</b>", styles['normal']))
            elements.append(Paragraph(f"<b>Зачислено акций: {int(total_credited):,}</b>", styles['normal']))
            elements.append(Paragraph(f"<b>Списано акций: {int(total_debited):,}</b>", styles['normal']))
            
            doc.build(elements)
            QMessageBox.information(self.parent, "Успех", f"Отчет сохранен в файл:\n{file_path}")
            return True
            
        except Exception as e:
            QMessageBox.critical(self.parent, "Ошибка", f"Ошибка при создании PDF: {str(e)}")
            return False
    
    def export_account_shares_report(self, account_data, shares_data):
        """Отчет о лицевом счете и акциях на нем"""
        file_path = self.get_save_filename(self.parent, 
            f"account_{account_data.get('account_number', 'report')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        if not file_path:
            return False
        
        try:
            doc = SimpleDocTemplate(file_path, pagesize=A4,
                                   topMargin=20*mm, bottomMargin=20*mm,
                                   leftMargin=15*mm, rightMargin=15*mm)
            elements = []
            
            title = "Отчет о лицевом счете"
            subtitle = f"Номер счета: {account_data.get('account_number', '')}"
            elements.extend(self.create_header(title, subtitle))
            
            styles = self.get_styles()
            
            # Информация о счете
            elements.append(Paragraph("<b>Информация о лицевом счете:</b>", styles['heading']))
            elements.append(Spacer(1, 5))
            
            current_balance = self.convert_to_float(account_data.get('current_balance', 0))
            
            info_data = [
                ["Акционер:", account_data.get('shareholder_name', '-')],
                ["Номер счета:", account_data.get('account_number', '-')],
                ["Дата открытия:", str(account_data.get('open_date', '-'))],
                ["Дата закрытия:", str(account_data.get('close_date', '-')) if account_data.get('close_date') else 'Активен'],
                ["Текущий остаток:", f"{int(current_balance):,} акций"],
                ["Статус:", account_data.get('status', '-')],
            ]
            
            info_table = Table(info_data, colWidths=[120, 350])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), self.get_font_name()),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(info_table)
            elements.append(Spacer(1, 15))
            
            # Акции на счете
            if shares_data:
                elements.append(Paragraph("<b>Акции на счете:</b>", styles['heading']))
                elements.append(Spacer(1, 5))
                
                headers = ["Компания", "Регистрационный номер", "Тип акций", "Количество", "Номинальная стоимость"]
                table_data = []
                quantities = []
                company_names = []
                company_quantities = {}
                
                for share in shares_data:
                    qty = self.convert_to_float(share.get('quantity', 0))
                    nominal = self.convert_to_float(share.get('nominal_value', 0))
                    company = share.get('company_name', '-')
                    quantities.append(qty)
                    company_names.append(company)
                    company_quantities[company] = company_quantities.get(company, 0) + qty
                    table_data.append([
                        company,
                        share.get('registration_number', '-'),
                        share.get('share_type', '-'),
                        f"{int(qty):,}" if qty == int(qty) else f"{qty:,}",
                        f"{nominal:,.2f} руб."
                    ])
                
                elements.extend(self.create_table(table_data, headers))
                
                if quantities and company_names:
                    elements.append(Spacer(1, 10))
                    chart_elements = self.create_bar_chart(
                        quantities[:10], [name[:15] for name in company_names[:10]], 
                        "Распределение акций по компаниям"
                    )
                    elements.extend(chart_elements)
                
                # Круговая диаграмма
                if company_quantities:
                    elements.append(Spacer(1, 10))
                    pie_elements = self.create_pie_chart(
                        list(company_quantities.values()), list(company_quantities.keys()),
                        "Структура портфеля акций", width=400, height=250
                    )
                    elements.extend(pie_elements)
                
                total_shares = sum(quantities)
                total_value = sum(
                    self.convert_to_float(s.get('quantity', 0)) * self.convert_to_float(s.get('nominal_value', 0)) 
                    for s in shares_data
                )
                elements.append(Spacer(1, 10))
                elements.append(Paragraph(f"<b>Всего видов акций: {len(shares_data)}</b>", styles['normal']))
                elements.append(Paragraph(f"<b>Общее количество акций: {int(total_shares):,}</b>", styles['normal']))
                elements.append(Paragraph(f"<b>Общая номинальная стоимость: {total_value:,.2f} руб.</b>", styles['normal']))
            else:
                elements.append(Paragraph("<i>На счете нет акций</i>", styles['normal']))
            
            doc.build(elements)
            QMessageBox.information(self.parent, "Успех", f"Отчет сохранен в файл:\n{file_path}")
            return True
            
        except Exception as e:
            QMessageBox.critical(self.parent, "Ошибка", f"Ошибка при создании PDF: {str(e)}")
            return False
    
    def export_shareholder_accounts_report(self, shareholder_data, accounts_data, shares_on_accounts=None):
        """Отчет об акционере и его лицевых счетах"""
        file_path = self.get_save_filename(self.parent, 
            f"shareholder_{shareholder_data.get('name', 'report')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        if not file_path:
            return False
        
        try:
            doc = SimpleDocTemplate(file_path, pagesize=landscape(A4),
                                   topMargin=20*mm, bottomMargin=20*mm,
                                   leftMargin=15*mm, rightMargin=15*mm)
            elements = []
            
            title = "Отчет об акционере"
            subtitle = shareholder_data.get('name', '')
            elements.extend(self.create_header(title, subtitle))
            
            styles = self.get_styles()
            
            # Информация об акционере
            elements.append(Paragraph("<b>Информация об акционере:</b>", styles['heading']))
            elements.append(Spacer(1, 5))
            
            shareholder_type = 'Физическое лицо' if shareholder_data.get('type') == 'individual' else 'Юридическое лицо'
            passport = shareholder_data.get('passport_data', '') or shareholder_data.get('ogrn', '-')
            
            info_data = [
                ["Тип:", shareholder_type],
                ["Наименование:", shareholder_data.get('name', '-')],
                ["ИНН:", shareholder_data.get('inn', '-')],
                ["Паспорт/ОГРН:", passport],
                ["Адрес:", shareholder_data.get('address', '-')],
                ["Статус:", shareholder_data.get('status', '-')],
            ]
            
            info_table = Table(info_data, colWidths=[120, 350])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), self.get_font_name()),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(info_table)
            elements.append(Spacer(1, 15))
            
            # Лицевые счета
            if accounts_data:
                elements.append(Paragraph("<b>Лицевые счета:</b>", styles['heading']))
                elements.append(Spacer(1, 5))
                
                headers = ["Номер счета", "Дата открытия", "Дата закрытия", "Остаток акций", "Статус"]
                table_data = []
                balances = []
                account_numbers = []
                
                for acc in accounts_data:
                    balance = self.convert_to_float(acc.get('current_balance', 0))
                    balances.append(balance)
                    account_numbers.append(acc.get('account_number', ''))
                    table_data.append([
                        acc.get('account_number', '-'),
                        str(acc.get('open_date', '-')),
                        str(acc.get('close_date', '-')) if acc.get('close_date') else 'Активен',
                        f"{int(balance):,}" if balance == int(balance) else f"{balance:,}",
                        acc.get('status', '-')
                    ])
                
                elements.extend(self.create_table(table_data, headers))
                
                if balances and any(b > 0 for b in balances):
                    elements.append(Spacer(1, 10))
                    chart_elements = self.create_bar_chart(
                        balances, account_numbers, 
                        "Диаграмма распределения акций по лицевым счетам"
                    )
                    elements.extend(chart_elements)
                
                total_balance = sum(balances)
                elements.append(Spacer(1, 10))
                elements.append(Paragraph(f"<b>Всего счетов: {len(accounts_data)}</b>", styles['normal']))
                elements.append(Paragraph(f"<b>Общее количество акций: {int(total_balance):,}</b>", styles['normal']))
                
                # Акции на счетах
                if shares_on_accounts:
                    elements.append(Spacer(1, 15))
                    elements.append(Paragraph("<b>Акции на счетах:</b>", styles['heading']))
                    elements.append(Spacer(1, 5))
                    
                    shares_headers = ["Номер счета", "Компания", "Рег. номер", "Тип", "Количество"]
                    shares_data_list = []
                    company_shares = {}
                    
                    for item in shares_on_accounts:
                        company = item.get('company_name', '-')
                        qty = self.convert_to_float(item.get('quantity', 0))
                        company_shares[company] = company_shares.get(company, 0) + qty
                        shares_data_list.append([
                            item.get('account_number', '-'),
                            company,
                            item.get('registration_number', '-'),
                            item.get('share_type', '-'),
                            f"{int(qty):,}" if qty == int(qty) else f"{qty:,}"
                        ])
                    
                    elements.extend(self.create_table(shares_data_list, shares_headers))
                    
                    if company_shares:
                        elements.append(Spacer(1, 10))
                        pie_elements = self.create_pie_chart(
                            list(company_shares.values()), list(company_shares.keys()),
                            "Распределение акций по компаниям", width=400, height=250
                        )
                        elements.extend(pie_elements)
            else:
                elements.append(Paragraph("<i>Нет лицевых счетов</i>", styles['normal']))
            
            doc.build(elements)
            QMessageBox.information(self.parent, "Успех", f"Отчет сохранен в файл:\n{file_path}")
            return True
            
        except Exception as e:
            QMessageBox.critical(self.parent, "Ошибка", f"Ошибка при создании PDF: {str(e)}")
            return False