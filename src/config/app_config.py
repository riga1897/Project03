
import os
from typing import Dict, Optional


class AppConfig:
    """Основная конфигурация приложения"""
    
    def __init__(self):
        # Тип хранилища по умолчанию
        self.storage_type = os.getenv('STORAGE_TYPE', 'postgres')
        
        # Настройки БД
        self.db_config = {
            'host': os.getenv('PGHOST', 'localhost'),
            'port': os.getenv('PGPORT', '5432'),
            'database': os.getenv('PGDATABASE', 'postgres'),
            'username': os.getenv('PGUSER', 'postgres'),
            'password': os.getenv('PGPASSWORD', '')
        }
        
        # Настройки JSON файла (резервный вариант)
        self.json_filename = os.getenv('JSON_STORAGE_FILE', 'data/storage/vacancies.json')
    
    def get_storage_type(self) -> str:
        """Возвращает тип хранилища"""
        return self.storage_type
    
    def set_storage_type(self, storage_type: str) -> None:
        """Устанавливает тип хранилища"""
        if storage_type in ['postgres', 'json']:
            self.storage_type = storage_type
        else:
            raise ValueError(f"Неподдерживаемый тип хранилища: {storage_type}")
    
    def get_db_config(self) -> Dict[str, str]:
        """Возвращает конфигурацию БД"""
        return self.db_config.copy()
    
    def set_db_config(self, config: Dict[str, str]) -> None:
        """Обновляет конфигурацию БД"""
        self.db_config.update(config)
    
    def get_json_filename(self) -> str:
        """Возвращает имя JSON файла"""
        return self.json_filename
    
    def set_json_filename(self, filename: str) -> None:
        """Устанавливает имя JSON файла"""
        self.json_filename = filename
