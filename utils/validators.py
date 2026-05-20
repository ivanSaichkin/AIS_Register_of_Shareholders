# utils/validators.py
import re
from datetime import date

class Validators:
    """Класс для валидации данных"""
    
    @staticmethod
    def validate_inn(inn: str) -> bool:
        """Проверка ИНН (10 или 12 цифр)"""
        return bool(re.match(r'^\d{10}$|^\d{12}$', inn))
    
    @staticmethod
    def validate_ogrn(ogrn: str) -> bool:
        """Проверка ОГРН (13 цифр)"""
        return bool(re.match(r'^\d{13}$', ogrn))
    
    @staticmethod
    def validate_passport(passport: str) -> bool:
        """Проверка паспортных данных (серия номер)"""
        return bool(re.match(r'^\d{4}\s?\d{6}$', passport))
    
    @staticmethod
    def validate_positive_number(value: float) -> bool:
        """Проверка положительного числа"""
        try:
            return float(value) > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_positive_int(value: int) -> bool:
        """Проверка положительного целого числа"""
        try:
            return int(value) > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_date_range(start_date: date, end_date: date) -> bool:
        """Проверка, что дата начала не позже даты окончания"""
        return start_date <= end_date
    
    @staticmethod
    def validate_registration_number(number: str) -> bool:
        """Проверка регистрационного номера выпуска (формат XXX-XXX-XXX)"""
        return bool(re.match(r'^\d{3}-\d{3}-\d{3}$', number))
    
    @staticmethod
    def validate_account_number(number: str) -> bool:
        """Проверка номера лицевого счета"""
        return bool(re.match(r'^[A-Z0-9]{6,20}$', number, re.IGNORECASE))
    
    @staticmethod
    def validate_shareholder_status(status: str) -> bool:
        """Проверка статуса акционера"""
        valid_statuses = ['активный', 'заблокированный', 'неактивный']
        return status.lower() in valid_statuses
    
    @staticmethod
    def validate_share_type(share_type: str) -> bool:
        """Проверка типа акции"""
        valid_types = ['обыкновенная', 'привилегированная']
        return share_type.lower() in valid_types