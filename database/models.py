# database/models.py
from database.db_manager import DatabaseManager
from typing import List, Dict, Optional

class CompanyModel:
    """Модель для работы с акционерными обществами"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def get_all(self) -> List[Dict]:
        return self.db.execute_query("""
            SELECT c.*, 
                   COUNT(DISTINCT si.issue_id) as shares_count
            FROM joint_stock_companies c
            LEFT JOIN share_issues si ON c.company_id = si.company_id
            GROUP BY c.company_id
            ORDER BY c.company_id
        """)
    
    def get_by_id(self, company_id: int) -> Optional[Dict]:
        result = self.db.execute_query(
            "SELECT * FROM joint_stock_companies WHERE company_id = %s",
            (company_id,)
        )
        return result[0] if result else None
    
    def get_by_name(self, name: str) -> List[Dict]:
        return self.db.execute_query(
            "SELECT * FROM joint_stock_companies WHERE full_name ILIKE %s OR short_name ILIKE %s",
            (f'%{name}%', f'%{name}%')
        )
    
    def get_by_city(self, city: str) -> List[Dict]:
        return self.db.execute_query(
            "SELECT * FROM joint_stock_companies WHERE city ILIKE %s",
            (f'%{city}%',)
        )
    
    def create(self, data: Dict) -> int:
        return self.db.execute_insert("""
            INSERT INTO joint_stock_companies 
            (full_name, short_name, inn, ogrn, address, authorized_capital, city)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING company_id
        """, (data['full_name'], data['short_name'], data['inn'], 
              data['ogrn'], data['address'], data['authorized_capital'], data.get('city')))
    
    def update(self, company_id: int, data: Dict) -> int:
        return self.db.execute_update("""
            UPDATE joint_stock_companies 
            SET full_name = %s, short_name = %s, inn = %s, ogrn = %s,
                address = %s, authorized_capital = %s, city = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE company_id = %s
        """, (data['full_name'], data['short_name'], data['inn'],
              data['ogrn'], data['address'], data['authorized_capital'], 
              data.get('city'), company_id))
    
    def delete(self, company_id: int) -> int:
        return self.db.execute_delete(
            "DELETE FROM joint_stock_companies WHERE company_id = %s",
            (company_id,)
        )


class ShareIssueModel:
    """Модель для работы с выпусками акций"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def get_all(self) -> List[Dict]:
        return self.db.execute_query("""
            SELECT si.*, c.full_name as company_name
            FROM share_issues si
            JOIN joint_stock_companies c ON si.company_id = c.company_id
            ORDER BY si.issue_id
        """)
    
    def get_by_company(self, company_id: int) -> List[Dict]:
        return self.db.execute_query(
            "SELECT * FROM share_issues WHERE company_id = %s ORDER BY issue_id",
            (company_id,)
        )
    
    def get_by_registration_number(self, reg_number: str) -> Optional[Dict]:
        result = self.db.execute_query("""
            SELECT si.*, c.full_name as company_name
            FROM share_issues si
            JOIN joint_stock_companies c ON si.company_id = c.company_id
            WHERE si.registration_number = %s
        """, (reg_number,))
        return result[0] if result else None
    
    def get_by_nominal_range(self, min_value: float, max_value: float) -> List[Dict]:
        return self.db.execute_query("""
            SELECT si.*, c.full_name as company_name
            FROM share_issues si
            JOIN joint_stock_companies c ON si.company_id = c.company_id
            WHERE si.nominal_value BETWEEN %s AND %s
        """, (min_value, max_value))
    
    def create(self, data: Dict) -> int:
        return self.db.execute_insert("""
            INSERT INTO share_issues 
            (company_id, registration_number, registration_date, share_type, 
             category_series, quantity, nominal_value, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING issue_id
        """, (data['company_id'], data['registration_number'], data['registration_date'],
              data['share_type'], data.get('category_series'), data['quantity'],
              data['nominal_value'], data.get('status', 'размещен')))
    
    def update(self, issue_id: int, data: Dict) -> int:
        return self.db.execute_update("""
            UPDATE share_issues 
            SET registration_number = %s, registration_date = %s, share_type = %s,
                category_series = %s, quantity = %s, nominal_value = %s, status = %s
            WHERE issue_id = %s
        """, (data['registration_number'], data['registration_date'], data['share_type'],
              data.get('category_series'), data['quantity'], data['nominal_value'],
              data.get('status'), issue_id))
    
    def delete(self, issue_id: int) -> int:
        return self.db.execute_delete(
            "DELETE FROM share_issues WHERE issue_id = %s",
            (issue_id,)
        )


class ShareholderModel:
    """Модель для работы с акционерами"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def get_all(self) -> List[Dict]:
        return self.db.execute_query("""
            SELECT s.*, COUNT(a.account_id) as accounts_count
            FROM shareholders s
            LEFT JOIN accounts a ON s.shareholder_id = a.shareholder_id
            GROUP BY s.shareholder_id
            ORDER BY s.shareholder_id
        """)
    
    def get_by_id(self, shareholder_id: int) -> Optional[Dict]:
        result = self.db.execute_query(
            "SELECT * FROM shareholders WHERE shareholder_id = %s",
            (shareholder_id,)
        )
        return result[0] if result else None
    
    def get_by_name(self, name: str) -> List[Dict]:
        return self.db.execute_query(
            "SELECT * FROM shareholders WHERE name ILIKE %s ORDER BY name",
            (f'%{name}%',)
        )
    
    def get_by_status(self, status: str) -> List[Dict]:
        return self.db.execute_query(
            "SELECT * FROM shareholders WHERE status = %s",
            (status,)
        )
    
    def create(self, data: Dict) -> int:
        return self.db.execute_insert("""
            INSERT INTO shareholders 
            (type, name, inn, passport_data, ogrn, address, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING shareholder_id
        """, (data['type'], data['name'], data.get('inn'), data.get('passport_data'),
              data.get('ogrn'), data['address'], data.get('status', 'активный')))
    
    def update(self, shareholder_id: int, data: Dict) -> int:
        return self.db.execute_update("""
            UPDATE shareholders 
            SET name = %s, inn = %s, passport_data = %s, ogrn = %s,
                address = %s, status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE shareholder_id = %s
        """, (data['name'], data.get('inn'), data.get('passport_data'),
              data.get('ogrn'), data['address'], data.get('status'), shareholder_id))
    
    def delete(self, shareholder_id: int) -> int:
        # Проверка на наличие акций
        accounts = self.db.execute_query(
            "SELECT * FROM accounts WHERE shareholder_id = %s AND current_balance > 0",
            (shareholder_id,)
        )
        if accounts:
            raise ValueError("Нельзя удалить акционера с положительным остатком акций")
        return self.db.execute_delete(
            "DELETE FROM shareholders WHERE shareholder_id = %s",
            (shareholder_id,)
        )


class AccountModel:
    """Модель для работы с лицевыми счетами"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def get_all(self) -> List[Dict]:
        return self.db.execute_query("""
            SELECT a.*, s.name as shareholder_name, s.type as shareholder_type
            FROM accounts a
            JOIN shareholders s ON a.shareholder_id = s.shareholder_id
            ORDER BY a.account_id
        """)
    
    def get_by_id(self, account_id: int) -> Optional[Dict]:
        result = self.db.execute_query("""
            SELECT a.*, s.name as shareholder_name
            FROM accounts a
            JOIN shareholders s ON a.shareholder_id = s.shareholder_id
            WHERE a.account_id = %s
        """, (account_id,))
        return result[0] if result else None
    
    def get_by_number(self, account_number: str) -> Optional[Dict]:
        result = self.db.execute_query("""
            SELECT a.*, s.name as shareholder_name
            FROM accounts a
            JOIN shareholders s ON a.shareholder_id = s.shareholder_id
            WHERE a.account_number = %s
        """, (account_number,))
        return result[0] if result else None
    
    def get_by_shareholder(self, shareholder_id: int) -> List[Dict]:
        return self.db.execute_query(
            "SELECT * FROM accounts WHERE shareholder_id = %s ORDER BY account_id",
            (shareholder_id,)
        )
    
    def get_by_status(self, status: str) -> List[Dict]:
        return self.db.execute_query("""
            SELECT a.*, s.name as shareholder_name
            FROM accounts a
            JOIN shareholders s ON a.shareholder_id = s.shareholder_id
            WHERE a.status = %s
        """, (status,))
    
    def get_shares_on_account(self, account_id: int) -> List[Dict]:
        return self.db.execute_query("""
            SELECT acs.*, si.registration_number, si.share_type, si.nominal_value,
                   c.full_name as company_name
            FROM account_shares acs
            JOIN share_issues si ON acs.issue_id = si.issue_id
            JOIN joint_stock_companies c ON si.company_id = c.company_id
            WHERE acs.account_id = %s
        """, (account_id,))
    
    def create(self, data: Dict) -> int:
        return self.db.execute_insert("""
            INSERT INTO accounts 
            (shareholder_id, account_number, open_date, close_date, current_balance, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING account_id
        """, (data['shareholder_id'], data['account_number'], data['open_date'],
              data.get('close_date'), data.get('current_balance', 0), data.get('status', 'активный')))
    
    def update(self, account_id: int, data: Dict) -> int:
        return self.db.execute_update("""
            UPDATE accounts 
            SET close_date = %s, status = %s
            WHERE account_id = %s
        """, (data.get('close_date'), data.get('status'), account_id))
    
    def add_shares(self, account_id: int, issue_id: int, quantity: int) -> int:
        # Проверка существующей записи
        existing = self.db.execute_query("""
            SELECT * FROM account_shares WHERE account_id = %s AND issue_id = %s
        """, (account_id, issue_id))
        
        if existing:
            return self.db.execute_update("""
                UPDATE account_shares SET quantity = quantity + %s
                WHERE account_id = %s AND issue_id = %s
            """, (quantity, account_id, issue_id))
        else:
            return self.db.execute_insert("""
                INSERT INTO account_shares (account_id, issue_id, quantity)
                VALUES (%s, %s, %s)
                RETURNING account_share_id
            """, (account_id, issue_id, quantity))


class OperationModel:
    """Модель для работы с операциями"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def get_by_account(self, account_id: int) -> List[Dict]:
        return self.db.execute_query("""
            SELECT o.*, ot.name as operation_type, si.registration_number,
                   c.full_name as company_name
            FROM operations o
            JOIN operation_types ot ON o.type_id = ot.type_id
            JOIN share_issues si ON o.share_issue_id = si.issue_id
            JOIN joint_stock_companies c ON si.company_id = c.company_id
            WHERE o.account_id = %s
            ORDER BY o.operation_date DESC
        """, (account_id,))
    
    def create(self, data: Dict) -> int:
        return self.db.execute_insert("""
            INSERT INTO operations 
            (account_id, type_id, operation_date, share_issue_id, quantity, 
             basis_document, from_account_id, to_account_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING operation_id
        """, (data['account_id'], data['type_id'], data['operation_date'],
              data['share_issue_id'], data['quantity'], data.get('basis_document'),
              data.get('from_account_id'), data.get('to_account_id')))


class UserModel:
    """Модель для работы с пользователями"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def authenticate(self, username: str) -> Optional[Dict]:
        result = self.db.execute_query(
            "SELECT * FROM users WHERE username = %s",
            (username,)
        )
        return result[0] if result else None
    

# database/models.py (дополнение к существующему файлу)

class UserModel:
    """Модель для работы с пользователями"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def authenticate(self, username: str) -> Optional[Dict]:
        result = self.db.execute_query(
            "SELECT * FROM users WHERE username = %s",
            (username,)
        )
        return result[0] if result else None
    
    def create_user(self, username: str, role: str, shareholder_id: int = None, company_id: int = None) -> int:
        """Создание нового пользователя"""
        # Проверяем, существует ли уже такой пользователь
        existing = self.db.execute_query(
            "SELECT user_id FROM users WHERE username = %s",
            (username,)
        )
        if existing:
            return existing[0]['user_id']
        
        return self.db.execute_insert("""
            INSERT INTO users (username, role, shareholder_id, company_id)
            VALUES (%s, %s, %s, %s)
            RETURNING user_id
        """, (username, role, shareholder_id, company_id))
    
    def create_auto_user_for_company(self, company_name: str, company_id: int) -> int:
        """Автоматическое создание пользователя для сотрудника АО"""
        # Генерируем username из названия компании
        username = f"emp_{company_name.lower().replace(' ', '_').replace('"', '').replace(',', '')[:30]}"
        return self.create_user(username, 'employee', None, company_id)
    
    def create_auto_user_for_shareholder(self, shareholder_name: str, shareholder_id: int) -> int:
        """Автоматическое создание пользователя для акционера"""
        # Генерируем username из ФИО/наименования
        username = shareholder_name.lower().replace(' ', '_').replace('"', '').replace(',', '')[:30]
        # Добавляем суффикс если имя слишком короткое
        if len(username) < 3:
            username = f"user_{shareholder_id}"
        return self.create_user(username, 'shareholder', shareholder_id, None)