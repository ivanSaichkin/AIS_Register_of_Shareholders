# database/db_manager.py
import psycopg2
from psycopg2 import sql, extras
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

class DatabaseManager:
    """Управление подключением к базе данных"""
    
    def __init__(self, host: str = 'localhost', database: str = 'shareholders_registry',
                 user: str = 'postgres', password: str = 'postgres', port: int = 5432):
        self.conn_params = {
            'host': host,
            'database': database,
            'user': user,
            'password': password,
            'port': port
        }
        self.connection = None
        
    def connect(self):
        """Установка соединения с БД"""
        try:
            self.connection = psycopg2.connect(**self.conn_params)
            self.connection.autocommit = False
            return True
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return False
    
    def disconnect(self):
        """Закрытие соединения"""
        if self.connection:
            self.connection.close()
    
    @contextmanager
    def get_cursor(self):
        """Получение курсора с автоматическим управлением транзакциями"""
        cursor = self.connection.cursor(cursor_factory=extras.DictCursor)
        try:
            yield cursor
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Выполнение SELECT запроса"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_insert(self, query: str, params: tuple = None) -> int:
        """Выполнение INSERT запроса и возврат ID"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()[0] if cursor.rowcount > 0 else None
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Выполнение UPDATE запроса"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount
    
    def execute_delete(self, query: str, params: tuple = None) -> int:
        """Выполнение DELETE запроса"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount