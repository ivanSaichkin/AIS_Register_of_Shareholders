# utils/pdf_exporter.py
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph, 
                                Spacer, PageBreak, Image, KeepTogether)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import QDate
import os

class PDFExporter:
    """Класс для экспорта отчетов в PDF"""
    
    def __init__(self, parent=None):
        self.parent = parent
    
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
    
    def create_header(self, title, subtitle=None):
        """Создание заголовка отчета"""
        styles = getSampleStyleSheet()
        
        # Стиль для основного заголовка
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=12,
            textColor=colors.HexColor('#1a237e')
        )
        
        # Стиль для подзаголовка
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=colors.HexColor('#546e7a')
        )
        
        elements = []
        elements.append(Paragraph(title, title_style))
        if subtitle:
            elements.append(Paragraph(subtitle, subtitle_style))
        
        # Информация о дате создания
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#78909c')
        )
        current_date = datetime.now().strftime("%d.%m.%Y %H:%M")
        elements.append(Paragraph(f"Дата формирования: {current_date}", date_style))
        elements.append(Spacer(1, 10))
        
        return elements
    
    def create_table(self, data, headers, title=None):
        """Создание таблицы с данными"""
        styles = getSampleStyleSheet()
        elements = []
        
        if title:
            title_style = ParagraphStyle(
                'TableTitle',
                parent=styles['Normal'],
                fontSize=12,
                alignment=TA_LEFT,
                spaceAfter=6,
                fontName='Helvetica-Bold'
            )
            elements.append(Paragraph(title, title_style))
        
        # Подготовка данных для таблицы
        table_data = [headers]
        for row in data:
            # Преобразуем все данные в строки
            formatted_row = [str(cell) if cell is not None else '-' for cell in row]
            table_data.append(formatted_row)
        
        # Создание таблицы
        table = Table(table_data, repeatRows=1)
        
        # Стиль таблицы
        table_style = TableStyle([
            # Заголовок
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # Строки данных
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            
            # Границы
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
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
            styles = getSampleStyleSheet()
            summary = Paragraph(f"<b>Всего компаний: {len(companies_data)}</b>", styles['Normal'])
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
            styles = getSampleStyleSheet()
            summary = Paragraph(f"<b>Всего акционеров: {len(shareholders_data)}</b>", styles['Normal'])
            elements.append(summary)
            
            doc.build(elements)
            QMessageBox.information(self.parent, "Успех", f"Отчет сохранен в файл:\n{file_path}")
            return True
            
        except Exception as e:
            QMessageBox.critical(self.parent, "Ошибка", f"Ошибка при создании PDF: {str(e)}")
            return False
    
    def export_company_details_report(self, company_data, shares_data):
        """Экспорт подробного отчета об акционерном обществе и его акциях"""
        file_path = self.get_save_filename(self.parent, f"company_{company_data.get('short_name', 'report')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        if not file_path:
            return False
        
        try:
            doc = SimpleDocTemplate(file_path, pagesize=A4,
                                   topMargin=20*mm, bottomMargin=20*mm,
                                   leftMargin=15*mm, rightMargin=15*mm)
            elements = []
            
            # Заголовок
            title = f"Отчет об акционерном обществе"
            subtitle = company_data.get('full_name', '')
            elements.extend(self.create_header(title, subtitle))
            
            # Информация об АО
            styles = getSampleStyleSheet()
            info_style = ParagraphStyle('InfoStyle', parent=styles['Normal'], fontSize=10, spaceAfter=6)
            
            elements.append(Paragraph("<b>Основная информация:</b>", styles['Heading4']))
            elements.append(Spacer(1, 5))
            elements.append(Paragraph(f"<b>Полное наименование:</b> {company_data.get('full_name', '-')}", info_style))
            elements.append(Paragraph(f"<b>Сокращенное наименование:</b> {company_data.get('short_name', '-')}", info_style))
            elements.append(Paragraph(f"<b>ИНН:</b> {company_data.get('inn', '-')}", info_style))
            elements.append(Paragraph(f"<b>ОГРН:</b> {company_data.get('ogrn', '-')}", info_style))
            elements.append(Paragraph(f"<b>Адрес:</b> {company_data.get('address', '-')}", info_style))
            elements.append(Paragraph(f"<b>Уставной капитал:</b> {company_data.get('authorized_capital', 0):,.2f} руб.", info_style))
            elements.append(Paragraph(f"<b>Город:</b> {company_data.get('city', '-')}", info_style))
            elements.append(Spacer(1, 10))
            
            # Информация о выпусках акций
            if shares_data:
                elements.append(Paragraph("<b>Выпуски акций:</b>", styles['Heading4']))
                elements.append(Spacer(1, 5))
                
                headers = ["Рег. номер", "Дата", "Тип", "Категория", "Количество", "Номинал", "Статус"]
                table_data = []
                for share in shares_data:
                    table_data.append([
                        share.get('registration_number', '-'),
                        str(share.get('registration_date', '-')),
                        share.get('share_type', '-'),
                        share.get('category_series', '-'),
                        str(share.get('quantity', '0')),
                        f"{share.get('nominal_value', 0):,.2f} руб.",
                        share.get('status', '-')
                    ])
                
                elements.extend(self.create_table(table_data, headers, "Выпуски акций"))
                elements.append(Paragraph(f"<b>Всего выпусков: {len(shares_data)}</b>", styles['Normal']))
            else:
                elements.append(Paragraph("<i>Нет выпусков акций</i>", styles['Italic']))
            
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
            styles = getSampleStyleSheet()
            total_shares = sum(acc.get('current_balance', 0) for acc in accounts_data)
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"<b>Всего счетов: {len(accounts_data)}</b>", styles['Normal']))
            elements.append(Paragraph(f"<b>Общее количество акций: {total_shares}</b>", styles['Normal']))
            
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
            styles = getSampleStyleSheet()
            total_credited = sum(op.get('quantity', 0) for op in operations_data if op.get('operation_type') == 'Зачисление')
            total_debited = sum(op.get('quantity', 0) for op in operations_data if op.get('operation_type') == 'Списание')
            
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"<b>Всего операций: {len(operations_data)}</b>", styles['Normal']))
            elements.append(Paragraph(f"<b>Зачислено акций: {total_credited}</b>", styles['Normal']))
            elements.append(Paragraph(f"<b>Списано акций: {total_debited}</b>", styles['Normal']))
            
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
            styles = getSampleStyleSheet()
            total_shares = sum(share.get('quantity', 0) for share in shares_data)
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"<b>Всего видов акций: {len(shares_data)}</b>", styles['Normal']))
            elements.append(Paragraph(f"<b>Общее количество акций: {total_shares}</b>", styles['Normal']))
            
            doc.build(elements)
            QMessageBox.information(self.parent, "Успех", f"Отчет сохранен в файл:\n{file_path}")
            return True
            
        except Exception as e:
            QMessageBox.critical(self.parent, "Ошибка", f"Ошибка при создании PDF: {str(e)}")
            return False