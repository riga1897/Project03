"""
Простой адаптер для работы с PostgreSQL без psycopg2
Использует subprocess и psql для выполнения запросов
"""

import os
import subprocess
import json
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


class SimpleDBAdapter:
    """Простой адаптер для работы с PostgreSQL через psql"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise RuntimeError("DATABASE_URL не установлен")
    
    def __enter__(self):
        """Поддержка контекстного менеджера"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Поддержка контекстного менеджера"""
        pass  # Простой адаптер не требует закрытия соединения
    
    def cursor(self, cursor_factory=None):
        """Имитация cursor() для совместимости с psycopg2"""
        return SimpleCursor(self)
    
    def test_connection(self) -> bool:
        """Проверка соединения с БД"""
        try:
            cmd = [
                "psql", self.database_url,
                "-c", "SELECT 1",
                "-t",
                "--quiet"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception:
            return False


class SimpleCursor:
    """Простой курсор для совместимости с psycopg2"""
    
    def __init__(self, adapter):
        self.adapter = adapter
        self._last_results = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def execute(self, query, params=()):
        """Выполнение SQL запроса"""
        try:
            # Подготовка запроса с параметрами
            if params:
                for i, param in enumerate(params):
                    placeholder = f"%s"
                    if isinstance(param, str):
                        query = query.replace(placeholder, f"'{param}'", 1)
                    elif param is None:
                        query = query.replace(placeholder, "NULL", 1)
                    else:
                        query = query.replace(placeholder, str(param), 1)
            
            cmd = [
                "psql", self.adapter.database_url,
                "-c", query,
                "-t",  # только данные
                "--quiet"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                logger.error(f"Ошибка выполнения запроса: {result.stderr}")
                self._last_results = []
                return
            
            # Парсинг результата для SELECT запросов
            if query.strip().upper().startswith('SELECT'):
                lines = result.stdout.strip().split('\n')
                rows = []
                for line in lines:
                    if line.strip():
                        # Простой парсинг табличного вывода
                        fields = [field.strip() for field in line.split('|')]
                        if fields and fields[0]:  # Пропускаем пустые строки
                            rows.append(tuple(fields))
                self._last_results = rows
            else:
                self._last_results = []
                
        except subprocess.TimeoutExpired:
            logger.error("Тайм-аут выполнения запроса")
            self._last_results = []
        except Exception as e:
            logger.error(f"Ошибка выполнения запроса: {e}")
            self._last_results = []
    
    def fetchone(self):
        """Получение одной строки результата"""
        if self._last_results:
            result = self._last_results[0]
            # Попытка конвертировать строковые числа в числа
            converted = []
            for field in result:
                if isinstance(field, str) and field.isdigit():
                    converted.append(int(field))
                elif isinstance(field, str) and field.replace('.', '').isdigit():
                    converted.append(float(field))
                else:
                    converted.append(field)
            return tuple(converted)
        return None
    
    def fetchall(self):
        """Получение всех строк результата"""
        return self._last_results
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Выполнение SELECT запроса"""
        try:
            # Подготовка запроса с параметрами
            if params:
                # Простая замена параметров (не для продакшена!)
                for i, param in enumerate(params):
                    placeholder = f"${i+1}"
                    if isinstance(param, str):
                        query = query.replace(placeholder, f"'{param}'")
                    else:
                        query = query.replace(placeholder, str(param))
            
            # Выполнение через psql с JSON выводом
            cmd = [
                "psql", self.database_url,
                "-c", query,
                "-t",  # только данные
                "--quiet"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                logger.error(f"Ошибка выполнения запроса: {result.stderr}")
                return []
            
            # Парсинг результата
            lines = result.stdout.strip().split('\n')
            rows = []
            for line in lines:
                if line.strip():
                    try:
                        # Простой парсинг табличного вывода
                        fields = [field.strip() for field in line.split('|')]
                        if fields and fields[0]:  # Пропускаем пустые строки
                            rows.append({"data": fields})
                    except Exception:
                        continue
            
            return rows
            
        except subprocess.TimeoutExpired:
            logger.error("Тайм-аут выполнения запроса")
            return []
        except Exception as e:
            logger.error(f"Ошибка выполнения запроса: {e}")
            return []
    
    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """Выполнение INSERT/UPDATE/DELETE запроса"""
        try:
            # Подготовка запроса с параметрами  
            if params:
                for i, param in enumerate(params):
                    placeholder = f"${i+1}"
                    if isinstance(param, str):
                        query = query.replace(placeholder, f"'{param}'")
                    else:
                        query = query.replace(placeholder, str(param))
            
            cmd = [
                "psql", self.database_url,
                "-c", query,
                "--quiet"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                logger.error(f"Ошибка выполнения обновления: {result.stderr}")
                return 0
            
            # Попытка извлечь количество затронутых строк из вывода
            output = result.stdout.strip()
            if "INSERT" in output and "1" in output:
                return 1
            elif "UPDATE" in output or "DELETE" in output:
                # Простой парсинг числа из строки типа "UPDATE 5"
                words = output.split()
                for word in words:
                    if word.isdigit():
                        return int(word)
            
            return 1  # По умолчанию считаем что операция прошла успешно
            
        except Exception as e:
            logger.error(f"Ошибка выполнения обновления: {e}")
            return 0
    
    def test_connection(self) -> bool:
        """Проверка соединения с БД"""
        try:
            result = self.execute_query("SELECT 1 as test")
            return len(result) > 0
        except Exception:
            return False


# Глобальный экземпляр адаптера
db_adapter = SimpleDBAdapter()


def get_db_adapter():
    """Получение адаптера БД"""
    return db_adapter