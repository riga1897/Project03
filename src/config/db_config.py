
import os
from typing import Dict, Optional


class DatabaseConfig:
    """Конфигурация подключения к базе данных"""
    
    def __init__(self):
        self.default_config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, str]:
        """Получает конфигурацию по умолчанию из переменных окружения"""
        return {
            'host': os.getenv('PGHOST', 'localhost'),
            'port': os.getenv('PGPORT', '5432'),
            'database': os.getenv('PGDATABASE', 'postgres'),
            'username': os.getenv('PGUSER', 'postgres'),
            'password': os.getenv('PGPASSWORD', '')
        }
    
    def get_config(self, custom_config: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Возвращает конфигурацию БД
        
        Args:
            custom_config: Пользовательская конфигурация (опционально)
            
        Returns:
            Dict[str, str]: Конфигурация подключения к БД
        """
        if custom_config:
            config = self.default_config.copy()
            config.update(custom_config)
            return config
        return self.default_config
    
    def test_connection(self, config: Optional[Dict[str, str]] = None) -> bool:
        """
        Тестирует подключение к БД
        
        Args:
            config: Конфигурация для тестирования (опционально)
            
        Returns:
            bool: True если подключение успешно
        """
        test_config = config or self.default_config
        
        try:
            import psycopg2
            connection = psycopg2.connect(
                host=test_config['host'],
                port=test_config['port'],
                database=test_config['database'],
                user=test_config['username'],
                password=test_config['password']
            )
            connection.close()
            return True
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
            return False
