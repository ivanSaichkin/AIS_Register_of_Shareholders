# utils/pdf_exporter.py
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph, 
                                Spacer, PageBreak, Image, KeepTogether)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from PyQt6.QtWidgets import QFileDialog, QMessageBox
import os

class PDFExporter:
    """Класс для экспорта отчетов в PDF с поддержкой кириллицы"""
    
    # Регистрация шрифтов для поддержки кириллицы
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
            # Windows
            'C:/Windows/Fonts/arial.ttf',
            'C:/Windows/Fonts/times.ttf',
            'C:/Windows/Fonts/calibri.ttf',
            # macOS
            '/System/Library/Fonts/Helvetica.ttc',
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
                    print(f"Ошибка регистрации шрифта {font_path}: {e}")
                    continue
        
        # Если не нашли подходящий шрифт, создаем базовый
        if not font_registered:
            print("Не найден подходящий шрифт, будут использованы стандартные шрифты")
        
        cls._fonts_registered = True
    
    def __init__(self, parent=None):
        self.parent = parent
        self.register_fonts()
    
    @staticmethod
    def get_save_filename(parent, default_name="report.pdf"):
        """Диалог выбора файла для сохранения"""
        file_path, _ = QFileDialog.getSaveFileName(
            parent,
            "Сохранить отчет",
            default_name,
            "PDF Files (*.pdf);;All Files (*)"
        )
        return file_path
    
    def get_styles(self):
        """Получение стилей с поддержкой кириллицы"""
        styles = getSampleStyleSheet()
        
        # Определяем название шрифта для кириллицы
        font_name = 'RussianFont' if 'RussianFont' in pdfmetrics._fonts else 'Helvetica'
        
        # Стиль для основного заголовка
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=font_name,
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=12,
            textColor=colors.HexColor('#1a237e')
        )
        
        # Стиль для подзаголовка
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=colors.HexColor('#546e7a')
        )
        
        # Стиль для даты
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=8,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#78909c')
        )
        
        # Стиль для заголовка таблицы
        table_title_style = ParagraphStyle(
            'TableTitle',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_LEFT,
            spaceAfter=6,
            fontName=font_name
        )
        
        # Стиль для обычного текста
        normal_style = ParagraphStyle(
            'NormalStyle',
            parent=styles['Normal'],
            fontSize=9,
            fontName=font_name
        )
        
        return {
            'title': title_style,
            'subtitle': subtitle_style,
            'date': date_style,
            'table_title': table_title_style,
            'normal': normal_style
        }
    
    def create_header(self, title, subtitle=None):
        """Создание заголовка отчета"""
        styles = self.get_styles()
        
        elements = []
        elements.append(Paragraph(title, styles['title']))
        if subtitle:
            elements.append(Paragraph(subtitle, styles['subtitle']))
        
        # Информация о дате создания
        current_date = datetime.now().strftime("%d.%m.%Y %H:%M")
        elements.append(Paragraph(f"Дата формирования: {current_date}", styles['date']))
        elements.append(Spacer(1, 10))
        
        return elements
    
    def create_table(self, data, headers, title=None):
        """Создание таблицы с данными с поддержкой кириллицы"""
        styles = self.get_styles()
        
        elements = []
        
        if title:
            elements.append(Paragraph(title, styles['table_title']))
        
        # Подготовка данных для таблицы
        table_data = []
        
        # Заголовки (преобразуем в Paragraph для поддержки кириллицы)
        header_row = []
        for header in headers:
            header_row.append(Paragraph(f"<b>{header}</b>", styles['table_title']))
        table_data.append(header_row)
        
        # Данные
        for row in data:
            formatted_row = []
            for cell in row:
                cell_str = str(cell) if cell is not None else '-'
                # Заменяем специальные символы для безопасного отображения
                cell_str = cell_str.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                formatted_row.append(Paragraph(cell_str, styles['normal']))
            table_data.append(formatted_row)
        
        # Создание таблицы
        table = Table(table_data, repeatRows=1)
        
        # Стиль таблицы
        table_style = TableStyle([
            # Заголовок
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # Строки данных
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 1), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            
            # Границы
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            
            # Чередование цветов строк
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ])
        
        table.setStyle(table_style)
        elements.append(table)
        elements.append(Spacer(1, 10))
        
        return elements
    
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
            
            # Заголовок
            title = "Отчет об акционерных обществах"
            subtitle = f"По городу: {city}" if city else "Все акционерные общества"
            elements.extend(self.create_header(title, subtitle))
            
            # Данные для таблицы
            headers = ["Наименование", "Сокращенное", "ИНН", "ОГРН", "Уставной капитал", "Адрес"]
            table_data = []
            for company in companies_data:
                table_data.append([
                    company.get('full_name', '-'),
                    company.get('short_name', '-'),
                    company.get('inn', '-'),
                    company.get('ogrn', '-'),
                    f"{company.get('authorized_capital', 0):,.2f} руб.",
                    company.get('address', '-')
                ])
            
            elements.extend(self.create_table(table_data, headers, "Список акционерных обществ"))
            
            # Итоговая информация
            styles = self.get_styles()
            summary = Paragraph(f"<b>Всего компаний: {len(companies_data)}</b>", styles['normal'])
            elements.append(summary)
            
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
            
            # Заголовок
            title = "Отчет об акционерах"
            subtitle = f"Статус: {status}" if status else "Все акционеры"
            elements.extend(self.create_header(title, subtitle))
            
            # Данные для таблицы
            headers = ["Тип", "Наименование", "ИНН", "Паспорт/ОГРН", "Адрес", "Статус"]
            table_data = []
            for sh in shareholders_data:
                passport = sh.get('passport_data', '') or sh.get('ogrn', '-')
                table_data.append([
                    'Физическое лицо' if sh.get('type') == 'individual' else 'Юридическое лицо',
                    sh.get('name', '-'),
                    sh.get('inn', '-'),
                    passport,
                    sh.get('address', '-'),
                    sh.get('status', '-')
                ])
            
            elements.extend(self.create_table(table_data, headers, "Список акционеров"))
            
            # Итоговая информация
            styles = self.get_styles()
            summary = Paragraph(f"<b>Всего акционеров: {len(shareholders_data)}</b>", styles['normal'])
            elements.append(summary)
            
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
            
            # Заголовок
            title = "Отчет о лицевых счетах"
            subtitle = f"Акционер: {shareholder_name}" if shareholder_name else "Все лицевые счета"
            elements.extend(self.create_header(title, subtitle))
            
            # Данные для таблицы
            headers = ["Акционер", "Номер счета", "Дата открытия", "Дата закрытия", "Остаток акций", "Статус"]
            table_data = []
            for acc in accounts_data:
                table_data.append([
                    acc.get('shareholder_name', '-'),
                    acc.get('account_number', '-'),
                    str(acc.get('open_date', '-')),
                    str(acc.get('close_date', '-')) if acc.get('close_date') else 'Активен',
                    str(acc.get('current_balance', '0')),
                    acc.get('status', '-')
                ])
            
            elements.extend(self.create_table(table_data, headers, "Список лицевых счетов"))
            
            # Итоговая информация
            styles = self.get_styles()
            total_shares = sum(acc.get('current_balance', 0) for acc in accounts_data)
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"<b>Всего счетов: {len(accounts_data)}</b>", styles['normal']))
            elements.append(Paragraph(f"<b>Общее количество акций: {total_shares}</b>", styles['normal']))
            
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
            
            # Заголовок
            title = "Отчет об операциях"
            subtitle = f"Лицевой счет: {account_number}" if account_number else "Все операции"
            elements.extend(self.create_header(title, subtitle))
            
            # Данные для таблицы
            headers = ["Дата", "Тип операции", "Компания", "Количество акций", "Основание"]
            table_data = []
            for op in operations_data:
                table_data.append([
                    str(op.get('operation_date', '-')),
                    op.get('operation_type', '-'),
                    op.get('company_name', '-'),
                    str(op.get('quantity', '0')),
                    op.get('basis_document', '-') or '-'
                ])
            
            elements.extend(self.create_table(table_data, headers, "Список операций"))
            
            # Итоговая информация
            styles = self.get_styles()
            total_credited = sum(op.get('quantity', 0) for op in operations_data if op.get('operation_type') == 'Зачисление')
            total_debited = sum(op.get('quantity', 0) for op in operations_data if op.get('operation_type') == 'Списание')
            
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"<b>Всего операций: {len(operations_data)}</b>", styles['normal']))
            elements.append(Paragraph(f"<b>Зачислено акций: {total_credited}</b>", styles['normal']))
            elements.append(Paragraph(f"<b>Списано акций: {total_debited}</b>", styles['normal']))
            
            doc.build(elements)
            QMessageBox.information(self.parent, "Успех", f"Отчет сохранен в файл:\n{file_path}")
            return True
            
        except Exception as e:
            QMessageBox.critical(self.parent, "Ошибка", f"Ошибка при создании PDF: {str(e)}")
            return False
    
    def export_shares_on_account_report(self, shares_data, account_number):
        """Экспорт отчета об акциях на лицевом счете"""
        file_path = self.get_save_filename(self.parent, f"shares_on_account_{account_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        if not file_path:
            return False
        
        try:
            doc = SimpleDocTemplate(file_path, pagesize=A4,
                                   topMargin=20*mm, bottomMargin=20*mm,
                                   leftMargin=15*mm, rightMargin=15*mm)
            elements = []
            
            # Заголовок
            title = "Отчет об акциях на лицевом счете"
            subtitle = f"Номер счета: {account_number}"
            elements.extend(self.create_header(title, subtitle))
            
            # Данные для таблицы
            headers = ["Компания", "Регистрационный номер", "Тип акций", "Количество", "Номинальная стоимость"]
            table_data = []
            for share in shares_data:
                table_data.append([
                    share.get('company_name', '-'),
                    share.get('registration_number', '-'),
                    share.get('share_type', '-'),
                    str(share.get('quantity', '0')),
                    f"{share.get('nominal_value', 0):,.2f} руб."
                ])
            
            elements.extend(self.create_table(table_data, headers, "Акции на счете"))
            
            # Итоговая информация
            styles = self.get_styles()
            total_shares = sum(share.get('quantity', 0) for share in shares_data)
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"<b>Всего видов акций: {len(shares_data)}</b>", styles['normal']))
            elements.append(Paragraph(f"<b>Общее количество акций: {total_shares}</b>", styles['normal']))
            
            doc.build(elements)
            QMessageBox.information(self.parent, "Успех", f"Отчет сохранен в файл:\n{file_path}")
            return True
            
        except Exception as e:
            QMessageBox.critical(self.parent, "Ошибка", f"Ошибка при создании PDF: {str(e)}")
            return False