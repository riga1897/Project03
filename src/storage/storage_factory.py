
from typing import Union, Dict, Optional
from src.storage.json_saver import JSONSaver
from src.storage.postgres_saver import PostgresSaver
from src.config.db_config import DatabaseConfig


class StorageFactory:
    """Фабрика для создания объектов хранилища"""
    
    @staticmethod
    def create_storage(storage_type: str = "postgres", 
                      config: Optional[Dict[str, str]] = None,
                      filename: Optional[str] = None) -> Union[JSONSaver, PostgresSaver]:
        """
        Создает объект хранилища в зависимости от типа
        
        Args:
            storage_type: Тип хранилища ("json" или "postgres")
            config: Конфигурация БД (для postgres)
            filename: Имя файла (для json)
            
        Returns:
            Объект хранилища
        """
        if storage_type.lower() == "json":
            return JSONSaver(filename or "data/storage/vacancies.json")
        elif storage_type.lower() == "postgres":
            db_config = DatabaseConfig()
            final_config = db_config.get_config(config)
            return PostgresSaver(final_config)
        else:
            raise ValueError(f"Неподдерживаемый тип хранилища: {storage_type}")
    
    @staticmethod
    def get_default_storage() -> Union[JSONSaver, PostgresSaver]:
        """
        Возвращает хранилище по умолчанию (PostgreSQL)
        
        Returns:
            Объект PostgreSQL хранилища
        """
        return StorageFactory.create_storage("postgres")
