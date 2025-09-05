"""Модули для работы с хранением данных."""
# Обновлены импорты в __init__.py для включения AbstractDBManager.
from .abstract import AbstractVacancyStorage
from .abstract_db_manager import AbstractDBManager
from .db_manager import DBManager
from .postgres_saver import PostgresSaver
from .storage_factory import StorageFactory

__all__ = ["AbstractVacancyStorage", "AbstractDBManager", "DBManager", "PostgresSaver", "StorageFactory"]